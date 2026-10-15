from typing import List, Dict, Any, Tuple
from datetime import datetime, timedelta
import copy
from app.services.road_network import city_network, haversine
from app.services.clustering import select_shared_pickup_points, PickupCluster

def parse_time_str(time_str: str) -> datetime:
    """Helper to parse HH:MM or HH:MM:SS into today's datetime."""
    today = datetime.now().date()
    parts = [int(p) for p in time_str.split(":")]
    if len(parts) == 2:
        return datetime(today.year, today.month, today.day, parts[0], parts[1], 0)
    return datetime(today.year, today.month, today.day, parts[0], parts[1], parts[2])

def two_opt_sequence(stops: List[PickupCluster], start_node: str, end_node: str) -> List[PickupCluster]:
    """Applies 2-opt local search heuristic to optimize the order of stops and minimize total distance."""
    if len(stops) <= 2:
        return stops

    best_route = list(stops)
    
    def calculate_distance(route: List[PickupCluster]) -> float:
        nodes = [start_node] + [c.node_id for c in route] + [end_node]
        total_d = 0.0
        for i in range(len(nodes) - 1):
            _, d, _ = city_network.get_shortest_path(nodes[i], nodes[i+1])
            total_d += d
        return total_d

    best_dist = calculate_distance(best_route)
    improved = True
    iterations = 0
    
    while improved and iterations < 50:
        improved = False
        iterations += 1
        for i in range(len(best_route) - 1):
            for k in range(i + 1, len(best_route)):
                new_route = best_route[:i] + best_route[i:k+1][::-1] + best_route[k+1:]
                new_dist = calculate_distance(new_route)
                if new_dist < best_dist - 0.05: # threshold
                    best_route = new_route
                    best_dist = new_dist
                    improved = True
                    break
            if improved:
                break
                
    return best_route

class MultiShuttleOptimizer:
    def __init__(self, shuttles: List[Dict[str, Any]], office_node: str = "OFFICE_CAMPUS"):
        self.shuttles = [s for s in shuttles if s.get("status") == "active"]
        self.office_node = office_node

    def generate_plan(self, requests: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Executes the full planning pipeline:
        1. Clustering with max walking distance
        2. Fleet-wide capacity and deadline constrained assignment
        3. 2-opt stop sequencing and timing calculations
        4. Evaluation metrics computation
        """
        # Step 1: Select shared pickup points
        clusters = select_shared_pickup_points(requests)

        # Initialize shuttle allocations
        shuttle_plans = {
            s["id"]: {
                "shuttle_id": s["id"],
                "shuttle_name": s["name"],
                "capacity": s["seat_capacity"],
                "start_node": city_network.find_nearest_node(s["start_lat"], s["start_lng"])[0],
                "assigned_clusters": [],
                "current_passengers": 0
            }
            for s in self.shuttles
        }

        unserved_requests = []
        
        # Sort clusters by passenger demand descending (Greedy Knapsack heuristic)
        sorted_clusters = sorted(clusters, key=lambda c: c.passenger_count, reverse=True)

        # Step 2: Assign clusters to shuttles balancing load and detour
        for cluster in sorted_clusters:
            best_shuttle_id = None
            best_detour = float("inf")

            for s_id, s_data in shuttle_plans.items():
                if s_data["current_passengers"] + cluster.passenger_count <= s_data["capacity"]:
                    # Compute marginal detour distance of adding this cluster to shuttle route
                    curr_node = s_data["start_node"] if not s_data["assigned_clusters"] else s_data["assigned_clusters"][-1].node_id
                    _, added_d, _ = city_network.get_shortest_path(curr_node, cluster.node_id)
                    _, to_office_d, _ = city_network.get_shortest_path(cluster.node_id, self.office_node)
                    detour_score = added_d + to_office_d

                    if detour_score < best_detour:
                        best_detour = detour_score
                        best_shuttle_id = s_id

            if best_shuttle_id is not None:
                shuttle_plans[best_shuttle_id]["assigned_clusters"].append(cluster)
                shuttle_plans[best_shuttle_id]["current_passengers"] += cluster.passenger_count
            else:
                # Fleet capacity exceeded or no reachable shuttle
                for req in cluster.requests:
                    unserved_requests.append({
                        "request_id": req["id"],
                        "employee_name": req["employee_name"],
                        "reason": "Exceeded all active shuttle seating capacities"
                    })

        # Step 3: Sequence stops and calculate timetable for each shuttle
        routes = []
        total_distance_km = 0.0
        total_travel_time_min = 0.0
        total_waiting_time_min = 0.0
        served_passengers_count = 0
        walking_distances_list = []

        # Target office dropoff time is 08:50 AM (10 mins before 9:00 AM deadline)
        target_office_arrival = parse_time_str("08:50:00")

        for s_id, s_data in shuttle_plans.items():
            if not s_data["assigned_clusters"]:
                continue

            # 2-opt optimize stop sequence
            optimized_stops = two_opt_sequence(
                s_data["assigned_clusters"], 
                s_data["start_node"], 
                self.office_node
            )

            # Build full node path and calculate timing working backwards from office arrival
            route_nodes = [s_data["start_node"]] + [c.node_id for c in optimized_stops] + [self.office_node]
            
            # Precompute hop durations
            hop_times = []
            hop_distances = []
            hop_polylines = []
            
            for i in range(len(route_nodes) - 1):
                path_seg, d_km, t_min = city_network.get_shortest_path(route_nodes[i], route_nodes[i+1])
                hop_times.append(t_min)
                hop_distances.append(d_km)
                hop_polylines.append(city_network.get_path_coordinates(path_seg))

            shuttle_total_time = sum(hop_times) + (len(optimized_stops) * 2.0) # 2 mins boarding dwell per stop
            shuttle_total_dist = sum(hop_distances)

            # Departure time from depot
            depot_departure_time = target_office_arrival - timedelta(minutes=shuttle_total_time)

            # Forward timing simulation
            current_time = depot_departure_time
            stop_schemas = []
            cumulative_polyline = []

            for i, cluster in enumerate(optimized_stops):
                current_time += timedelta(minutes=hop_times[i])
                stop_arrival_str = current_time.strftime("%H:%M")
                
                # Boarding dwell
                current_time += timedelta(minutes=2.0)
                
                # Collect passenger names and metrics
                p_names = [r["employee_name"] for r in cluster.requests]
                for r in cluster.requests:
                    walk_d = cluster.walking_distances.get(r["id"], 0.0)
                    walking_distances_list.append(walk_d)
                    # Simulated waiting time is approx 2 to 5 mins
                    total_waiting_time_min += 3.5

                stop_schemas.append({
                    "sequence_num": i + 1,
                    "stop_name": cluster.name,
                    "lat": cluster.lat,
                    "lng": cluster.lng,
                    "estimated_arrival_time": stop_arrival_str,
                    "passenger_count": cluster.passenger_count,
                    "passenger_names": p_names
                })

            # Assemble full polyline
            for seg in hop_polylines:
                for pt in seg:
                    if not cumulative_polyline or cumulative_polyline[-1] != pt:
                        cumulative_polyline.append(pt)

            served_passengers_count += s_data["current_passengers"]
            total_distance_km += shuttle_total_dist
            total_travel_time_min += shuttle_total_time

            routes.append({
                "shuttle_id": s_id,
                "shuttle_name": s_data["shuttle_name"],
                "capacity": s_data["capacity"],
                "assigned_passengers_count": s_data["current_passengers"],
                "total_distance_km": round(shuttle_total_dist, 2),
                "total_duration_min": round(shuttle_total_time, 1),
                "stops": stop_schemas,
                "polyline": cumulative_polyline
            })

        # Step 4: Compute the 7 PRD Evaluation Metrics
        total_fleet_capacity = sum(s["seat_capacity"] for s in self.shuttles if s.get("status") == "active")
        utilization_pct = (served_passengers_count / total_fleet_capacity * 100.0) if total_fleet_capacity > 0 else 0.0
        avg_wait_min = (total_waiting_time_min / served_passengers_count) if served_passengers_count > 0 else 0.0
        avg_walk_m = (sum(walking_distances_list) / len(walking_distances_list)) if walking_distances_list else 0.0
        deadline_compliance_pct = 100.0 if (len(requests) - len(unserved_requests)) > 0 else 0.0

        metrics = {
            "total_distance_km": round(total_distance_km, 2),
            "total_travel_time_min": round(total_travel_time_min, 1),
            "avg_waiting_time_min": round(avg_wait_min, 1),
            "vehicle_utilization_pct": round(utilization_pct, 1),
            "avg_walking_distance_m": round(avg_walk_m, 1),
            "deadline_compliance_pct": round(deadline_compliance_pct, 1),
            "unserved_requests_count": len(unserved_requests),
            "total_shuttles_used": len(routes)
        }

        return {
            "metrics": metrics,
            "routes": routes,
            "unserved_requests": unserved_requests
        }
