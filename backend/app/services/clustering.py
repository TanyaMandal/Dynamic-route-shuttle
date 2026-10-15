import math
from typing import List, Dict, Any, Tuple
from app.services.road_network import city_network, haversine
from app.config import settings

class PickupCluster:
    def __init__(self, cluster_id: str, node_id: str, name: str, lat: float, lng: float):
        self.cluster_id = cluster_id
        self.node_id = node_id
        self.name = name
        self.lat = lat
        self.lng = lng
        self.requests: List[Dict[str, Any]] = []
        self.walking_distances: Dict[str, float] = {}

    def add_request(self, req: Dict[str, Any], walk_m: float):
        self.requests.append(req)
        self.walking_distances[req["id"]] = round(walk_m, 1)

    @property
    def passenger_count(self) -> int:
        return len(self.requests)

    @property
    def avg_walking_distance(self) -> float:
        if not self.walking_distances:
            return 0.0
        return sum(self.walking_distances.values()) / len(self.walking_distances)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "cluster_id": self.cluster_id,
            "node_id": self.node_id,
            "name": self.name,
            "lat": self.lat,
            "lng": self.lng,
            "passenger_count": self.passenger_count,
            "avg_walking_distance_m": round(self.avg_walking_distance, 1),
            "requests": self.requests,
            "walking_distances": self.walking_distances
        }

def select_shared_pickup_points(
    requests: List[Dict[str, Any]], 
    max_walking_dist_m: float = None
) -> List[PickupCluster]:
    """
    FR-07, FR-08, FR-09:
    Clusters employee requests into shared pickup points on the road graph,
    strictly respecting the maximum allowable walking distance constraint.
    """
    if max_walking_dist_m is None:
        max_walking_dist_m = settings.MAX_WALKING_DISTANCE_METERS

    clusters: List[PickupCluster] = []
    
    # 1. Map each request to potential candidate road nodes or group by proximity
    for req in requests:
        lat = req["pickup_lat"]
        lng = req["pickup_lng"]
        
        # Check if it fits into an existing cluster within max walking distance
        assigned = False
        for cluster in clusters:
            dist = haversine(lat, lng, cluster.lat, cluster.lng)
            if dist <= max_walking_dist_m:
                cluster.add_request(req, dist)
                assigned = True
                break
        
        if not assigned:
            # Snap to closest road network node
            nearest_node, dist_to_node = city_network.find_nearest_node(lat, lng)
            node_data = city_network.graph.nodes[nearest_node]
            
            # If snapping to node is within walking distance, use node coordinates
            if dist_to_node <= max_walking_dist_m:
                new_cluster = PickupCluster(
                    cluster_id=f"CLUSTER_{len(clusters) + 1}",
                    node_id=nearest_node,
                    name=f"Pickup @ {node_data.get('name', nearest_node)}",
                    lat=node_data["lat"],
                    lng=node_data["lng"]
                )
                new_cluster.add_request(req, dist_to_node)
            else:
                # If nearest road node is further, create a micro-stop at the employee's accessible coordinate
                new_cluster = PickupCluster(
                    cluster_id=f"CLUSTER_{len(clusters) + 1}",
                    node_id=nearest_node,
                    name=f"Shared Stop {len(clusters) + 1} ({req.get('pickup_location_name', 'Sector Stop')})",
                    lat=lat,
                    lng=lng
                )
                new_cluster.add_request(req, 0.0)
                
            clusters.append(new_cluster)

    return clusters
