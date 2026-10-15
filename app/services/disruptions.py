from typing import List, Dict, Any, Tuple
from app.services.road_network import city_network
from app.services.optimizer import MultiShuttleOptimizer, two_opt_sequence
import copy

PRESET_DISRUPTIONS = [
    {
        "id": "PRESET_ROAD_SILKBOARD",
        "title": "Silk Board Junction Flyover Waterlogging",
        "type": "road_closure",
        "affected_entity": "HUB_SILKBOARD__HSR_SECTOR_7",
        "description": "Heavy monsoon waterlogging at Silk Board Junction closing the flyover link to HSR Sector 7."
    },
    {
        "id": "PRESET_ROAD_ORR",
        "title": "Outer Ring Road Pipeline Repair Closure",
        "type": "road_closure",
        "affected_entity": "HUB_MARATHAHALLI__KADUBEESANAHALLI",
        "description": "Emergency pipeline burst closing road segment between Marathahalli Hub and Kadubeesanahalli."
    },
    {
        "id": "PRESET_SHUTTLE_BREAKDOWN",
        "title": "Shuttle S2 (Tech Cruiser) Engine Breakdown",
        "type": "shuttle_breakdown",
        "affected_entity": "SHUTTLE_2",
        "description": "Shuttle S2 reported radiator overheating and complete engine stall en route."
    }
]

class DisruptionRecoveryEngine:
    def __init__(self, current_plan: Dict[str, Any], all_shuttles: List[Dict[str, Any]], all_requests: List[Dict[str, Any]]):
        self.original_plan = copy.deepcopy(current_plan)
        self.shuttles = copy.deepcopy(all_shuttles)
        self.requests = copy.deepcopy(all_requests)

    def simulate_road_closure(self, node_u: str, node_v: str, description: str) -> Dict[str, Any]:
        """
        FR-15, FR-16, FR-17, FR-18:
        Simulate road closure by blocking edge (u, v) in NetworkX graph,
        identifying affected routes, and recalculating detours.
        """
        # Block edge in NetworkX
        city_network.block_edge(node_u, node_v)

        revised_routes = []
        extra_distance_total = 0.0
        extra_delay_total = 0.0
        affected_passengers_count = 0

        try:
            for route in self.original_plan["routes"]:
                # Check if this route traverses blocked road
                stops = route["stops"]
                if not stops:
                    revised_routes.append(route)
                    continue

                shuttle_data = next((s for s in self.shuttles if s["id"] == route["shuttle_id"]), None)
                start_node = city_network.find_nearest_node(shuttle_data["start_lat"], shuttle_data["start_lng"])[0] if shuttle_data else "OFFICE_CAMPUS"
                stop_nodes = [city_network.find_nearest_node(st["lat"], st["lng"])[0] for st in stops]
                route_nodes = [start_node] + stop_nodes + [city_network.office_node]

                # Recalculate shortest path without the blocked edge
                recalculated_hop_coords = []
                recalculated_dist = 0.0
                recalculated_time = 0.0
                path_feasible = True

                for i in range(len(route_nodes) - 1):
                    seg_path, d, t = city_network.get_shortest_path(route_nodes[i], route_nodes[i+1])
                    if not seg_path:
                        path_feasible = False
                        break
                    recalculated_dist += d
                    recalculated_time += t
                    recalculated_hop_coords.append(city_network.get_path_coordinates(seg_path))

                if not path_feasible:
                    # Infeasible detour, retain with alert
                    revised_routes.append(route)
                    continue

                diff_dist = max(0.0, recalculated_dist - route["total_distance_km"])
                diff_time = max(0.0, recalculated_time - (route["total_duration_min"] - (len(stops) * 2.0)))

                if diff_dist > 0.05 or diff_time > 0.5:
                    affected_passengers_count += route["assigned_passengers_count"]
                    extra_distance_total += diff_dist
                    extra_delay_total += diff_time

                # Flatten new polyline
                new_poly = []
                for hop in recalculated_hop_coords:
                    for pt in hop:
                        if not new_poly or new_poly[-1] != pt:
                            new_poly.append(pt)

                revised_r = copy.deepcopy(route)
                revised_r["total_distance_km"] = round(recalculated_dist, 2)
                revised_r["total_duration_min"] = round(recalculated_time + (len(stops) * 2.0), 1)
                revised_r["polyline"] = new_poly
                revised_routes.append(revised_r)

        finally:
            # Unblock edge so the graph stays fresh for subsequent queries
            city_network.unblock_all()

        return {
            "disruption_type": "road_closure",
            "description": description,
            "extra_distance_km": round(extra_distance_total, 2),
            "extra_delay_min": round(extra_delay_total, 1),
            "passengers_affected": affected_passengers_count,
            "passengers_reassigned": affected_passengers_count,
            "passengers_unserved": 0,
            "revised_routes": revised_routes,
            "message": f"Alternative detour found avoiding {node_u} <-> {node_v}. Extra distance: +{round(extra_distance_total, 2)} km, Extra delay: +{round(extra_delay_total, 1)} min."
        }

    def simulate_shuttle_breakdown(self, broken_shuttle_id: str, description: str) -> Dict[str, Any]:
        """
        FR-15, FR-16, FR-17, FR-18:
        Simulate breakdown of a specific shuttle, reallocating its stranded
        passengers to surviving shuttles within available spare seat capacity.
        """
        # Find broken shuttle route
        broken_route = next((r for r in self.original_plan["routes"] if r["shuttle_id"] == broken_shuttle_id), None)
        if not broken_route:
            return {
                "disruption_type": "shuttle_breakdown",
                "description": description,
                "extra_distance_km": 0.0,
                "extra_delay_min": 0.0,
                "passengers_affected": 0,
                "passengers_reassigned": 0,
                "passengers_unserved": 0,
                "revised_routes": self.original_plan["routes"],
                "message": "Selected shuttle is not part of the active route plan."
            }

        stranded_passengers_count = broken_route["assigned_passengers_count"]
        surviving_shuttles = [s for s in self.shuttles if s["id"] != broken_shuttle_id and s.get("status") == "active"]

        # Re-run optimizer with surviving shuttles for the entire request pool
        optimizer = MultiShuttleOptimizer(surviving_shuttles)
        new_plan = optimizer.generate_plan(self.requests)

        reassigned_count = stranded_passengers_count - len(new_plan["unserved_requests"])
        unserved_count = len(new_plan["unserved_requests"])
        extra_dist = max(0.0, new_plan["metrics"]["total_distance_km"] - self.original_plan["metrics"]["total_distance_km"])
        extra_delay = max(0.0, new_plan["metrics"]["avg_waiting_time_min"] - self.original_plan["metrics"]["avg_waiting_time_min"])

        return {
            "disruption_type": "shuttle_breakdown",
            "description": description,
            "extra_distance_km": round(extra_dist, 2),
            "extra_delay_min": round(extra_delay, 1),
            "passengers_affected": stranded_passengers_count,
            "passengers_reassigned": max(0, reassigned_count),
            "passengers_unserved": unserved_count,
            "revised_routes": new_plan["routes"],
            "message": f"Shuttle {broken_route['shuttle_name']} breakdown processed. {max(0, reassigned_count)} passengers reassigned across surviving fleet. {unserved_count} unserved."
        }
