import math
import networkx as nx
from typing import Dict, List, Tuple, Any, Optional

def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate the great circle distance in meters between two coordinates."""
    R = 6371000.0  # Earth radius in meters
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    a = math.sin(delta_phi / 2.0) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return R * c

class CityRoadNetwork:
    def __init__(self):
        self.graph = nx.Graph()
        self.office_node = "OFFICE_CAMPUS"
        self.blocked_edges = set()
        self._initialize_city_network()

    def _initialize_city_network(self):
        # 1. Define Hub and Sector Nodes with Realistic Coordinates
        # Base center around 12.9716, 77.5946
        nodes_data = {
            "OFFICE_CAMPUS": {"name": "Central Tech Park Campus", "lat": 12.9716, "lng": 77.5946, "type": "office"},
            
            # Key Intersections & Ring Road Hubs
            "HUB_SILKBOARD": {"name": "Central Silk Board Junction", "lat": 12.9176, "lng": 77.6234, "type": "hub"},
            "HUB_MARATHAHALLI": {"name": "Marathahalli Bridge Hub", "lat": 12.9560, "lng": 77.7011, "type": "hub"},
            "HUB_BELLANDUR": {"name": "Bellandur Outer Ring Road Hub", "lat": 12.9295, "lng": 77.6775, "type": "hub"},
            "HUB_HEBBAL": {"name": "Hebbal Expressway Hub", "lat": 13.0358, "lng": 77.5970, "type": "hub"},
            "HUB_TOWN_HALL": {"name": "Town Hall Central Hub", "lat": 12.9647, "lng": 77.5857, "type": "hub"},

            # Residential Sectors
            "KORAMANGALA_4TH": {"name": "Koramangala 4th Block", "lat": 12.9345, "lng": 77.6265, "type": "residential"},
            "KORAMANGALA_80FT": {"name": "Koramangala 80ft Road", "lat": 12.9430, "lng": 77.6320, "type": "residential"},
            "HSR_SECTOR_1": {"name": "HSR Layout Sector 1", "lat": 12.9121, "lng": 77.6446, "type": "residential"},
            "HSR_SECTOR_2": {"name": "HSR Layout Sector 2", "lat": 12.9080, "lng": 77.6510, "type": "residential"},
            "HSR_SECTOR_7": {"name": "HSR Layout Sector 7", "lat": 12.9160, "lng": 77.6390, "type": "residential"},
            "BTM_2ND_STAGE": {"name": "BTM Layout 2nd Stage", "lat": 12.9140, "lng": 77.6100, "type": "residential"},
            "BTM_WATER_TANK": {"name": "BTM Water Tank Circle", "lat": 12.9180, "lng": 77.6040, "type": "residential"},
            "IND_100FT": {"name": "Indiranagar 100ft Road", "lat": 12.9719, "lng": 77.6412, "type": "residential"},
            "IND_DEFENCE": {"name": "Indiranagar Defence Colony", "lat": 12.9785, "lng": 77.6380, "type": "residential"},
            "WHITEFIELD_EPIP": {"name": "Whitefield EPIP Zone", "lat": 12.9815, "lng": 77.7289, "type": "residential"},
            "WHITEFIELD_HOPE": {"name": "Whitefield Hope Farm", "lat": 12.9840, "lng": 77.7470, "type": "residential"},
            "KADUBEESANAHALLI": {"name": "Kadubeesanahalli Circle", "lat": 12.9370, "lng": 77.6930, "type": "residential"},
            "JAYANAGAR_4TH": {"name": "Jayanagar 4th Block Complex", "lat": 12.9290, "lng": 77.5830, "type": "residential"},
            "JAYANAGAR_9TH": {"name": "Jayanagar 9th Block", "lat": 12.9190, "lng": 77.5910, "type": "residential"},
            "ECITY_PHASE1": {"name": "Electronic City Phase 1 Gate", "lat": 12.8450, "lng": 77.6650, "type": "residential"},
            "ECITY_TOLL": {"name": "Electronic City Elevated Tollway", "lat": 12.8750, "lng": 77.6520, "type": "residential"}
        }

        for node_id, data in nodes_data.items():
            self.graph.add_node(node_id, **data)

        # 2. Add Road Arteries and Connecting Edges with Real Distances
        connections = [
            ("OFFICE_CAMPUS", "HUB_TOWN_HALL", 40),
            ("OFFICE_CAMPUS", "IND_100FT", 35),
            ("OFFICE_CAMPUS", "KORAMANGALA_80FT", 35),
            ("OFFICE_CAMPUS", "HUB_HEBBAL", 50),
            
            ("HUB_TOWN_HALL", "JAYANAGAR_4TH", 30),
            ("JAYANAGAR_4TH", "JAYANAGAR_9TH", 30),
            ("JAYANAGAR_9TH", "BTM_WATER_TANK", 30),
            ("BTM_WATER_TANK", "BTM_2ND_STAGE", 25),
            ("BTM_2ND_STAGE", "HUB_SILKBOARD", 30),

            ("KORAMANGALA_80FT", "KORAMANGALA_4TH", 25),
            ("KORAMANGALA_4TH", "HUB_SILKBOARD", 30),
            ("HUB_SILKBOARD", "HSR_SECTOR_7", 30),
            ("HSR_SECTOR_7", "HSR_SECTOR_1", 25),
            ("HSR_SECTOR_1", "HSR_SECTOR_2", 25),
            ("HSR_SECTOR_2", "HUB_BELLANDUR", 35),

            ("IND_100FT", "IND_DEFENCE", 25),
            ("IND_100FT", "HUB_MARATHAHALLI", 40),
            ("HUB_MARATHAHALLI", "KADUBEESANAHALLI", 35),
            ("KADUBEESANAHALLI", "HUB_BELLANDUR", 35),
            ("HUB_MARATHAHALLI", "WHITEFIELD_EPIP", 35),
            ("WHITEFIELD_EPIP", "WHITEFIELD_HOPE", 30),

            ("HUB_SILKBOARD", "ECITY_TOLL", 55),
            ("ECITY_TOLL", "ECITY_PHASE1", 50),

            # Alternative / secondary routes
            ("KORAMANGALA_4TH", "HSR_SECTOR_7", 25),
            ("HUB_BELLANDUR", "HUB_SILKBOARD", 40),
            ("IND_DEFENCE", "HUB_HEBBAL", 45)
        ]

        for u, v, speed in connections:
            lat1, lon1 = nodes_data[u]["lat"], nodes_data[u]["lng"]
            lat2, lon2 = nodes_data[v]["lat"], nodes_data[v]["lng"]
            dist_km = haversine(lat1, lon1, lat2, lon2) / 1000.0
            duration_min = (dist_km / speed) * 60.0
            self.graph.add_edge(u, v, length_km=dist_km, speed_kmh=speed, weight=duration_min, name=f"{u} <-> {v}")

    def find_nearest_node(self, lat: float, lng: float) -> Tuple[str, float]:
        """Find the nearest graph node to a given lat/lng and return (node_id, distance_meters)."""
        min_dist = float("inf")
        best_node = self.office_node
        for node_id, data in self.graph.nodes(data=True):
            dist = haversine(lat, lng, data["lat"], data["lng"])
            if dist < min_dist:
                min_dist = dist
                best_node = node_id
        return best_node, min_dist

    def get_shortest_path(self, start_node: str, end_node: str) -> Tuple[List[str], float, float]:
        """Returns (path_nodes, total_distance_km, total_time_min)."""
        if start_node == end_node:
            return [start_node], 0.0, 0.0
        try:
            path = nx.shortest_path(self.graph, source=start_node, target=end_node, weight="weight")
            total_dist = 0.0
            total_time = 0.0
            for i in range(len(path) - 1):
                edge_data = self.graph[path[i]][path[i+1]]
                total_dist += edge_data.get("length_km", 0.0)
                total_time += edge_data.get("weight", 0.0)
            return path, round(total_dist, 2), round(total_time, 1)
        except nx.NetworkXNoPath:
            return [], float("inf"), float("inf")

    def get_path_coordinates(self, path_nodes: List[str]) -> List[List[float]]:
        """Returns [[lat, lng], [lat, lng], ...] for drawing polylines on Leaflet map."""
        coords = []
        for node in path_nodes:
            if node in self.graph.nodes:
                coords.append([self.graph.nodes[node]["lat"], self.graph.nodes[node]["lng"]])
        return coords

    def block_edge(self, u: str, v: str) -> bool:
        """Simulate a road closure between node u and node v."""
        if self.graph.has_edge(u, v):
            edge_attr = self.graph[u][v]
            self.blocked_edges.add((u, v, tuple(edge_attr.items())))
            self.graph.remove_edge(u, v)
            return True
        return False

    def unblock_all(self):
        """Restore all blocked edges."""
        self._initialize_city_network()
        self.blocked_edges.clear()

    def get_road_segments(self) -> List[Dict[str, Any]]:
        """Returns available road segments for disruption selection."""
        segments = []
        for u, v, data in self.graph.edges(data=True):
            u_name = self.graph.nodes[u].get("name", u)
            v_name = self.graph.nodes[v].get("name", v)
            segments.append({
                "id": f"{u}__{v}",
                "node_u": u,
                "node_v": v,
                "label": f"{u_name} to {v_name}",
                "length_km": round(data.get("length_km", 0), 2)
            })
        return segments

city_network = CityRoadNetwork()
