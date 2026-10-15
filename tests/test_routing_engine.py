import pytest
import time
from app.services.road_network import city_network, haversine
from app.services.clustering import select_shared_pickup_points
from app.services.optimizer import MultiShuttleOptimizer
from app.services.baseline import FixedRouteBaseline, compare_plans
from app.services.disruptions import DisruptionRecoveryEngine
from app.services.seeder import generate_benchmark_50_dataset

def test_road_network_connectivity():
    """Verify that all residential clusters connect to the Central Tech Park."""
    office = "OFFICE_CAMPUS"
    for node in city_network.graph.nodes:
        if node != office:
            path, dist, t = city_network.get_shortest_path(node, office)
            assert len(path) > 1, f"Node {node} has no path to office!"
            assert dist > 0.0
            assert t > 0.0

def test_clustering_walking_distance_constraint():
    """Verify that no employee is assigned a pickup point exceeding the max walking distance."""
    _, requests = generate_benchmark_50_dataset()
    max_walk_m = 400.0
    clusters = select_shared_pickup_points(requests, max_walking_dist_m=max_walk_m)

    assert len(clusters) > 0
    total_clustered_reqs = sum(c.passenger_count for c in clusters)
    assert total_clustered_reqs == len(requests)

    for c in clusters:
        for r_id, walk_d in c.walking_distances.items():
            assert walk_d <= max_walk_m + 5.0, f"Walking distance {walk_d}m exceeded {max_walk_m}m limit!"

def test_multi_shuttle_optimizer_performance_and_capacity():
    """Verify multi-shuttle optimizer performance (NFR-01: <30s) and capacity constraint (FR-11)."""
    shuttles, requests = generate_benchmark_50_dataset()
    optimizer = MultiShuttleOptimizer(shuttles)

    start_time = time.time()
    plan = optimizer.generate_plan(requests)
    elapsed = time.time() - start_time

    # Performance requirement: Must finish well under 30 seconds
    assert elapsed < 5.0, f"Optimization took {elapsed}s, expected < 5s!"

    # Capacity constraint: No shuttle exceeds its seat capacity
    for route in plan["routes"]:
        assert route["assigned_passengers_count"] <= route["capacity"]
        assert len(route["stops"]) > 0
        assert len(route["polyline"]) > 0

    # Metrics verification
    metrics = plan["metrics"]
    assert metrics["vehicle_utilization_pct"] > 0.0
    assert metrics["total_distance_km"] > 0.0
    assert metrics["avg_walking_distance_m"] <= 400.0

def test_fixed_baseline_comparison():
    """Verify that dynamic optimizer beats the fixed-route baseline on travel distance and waiting time."""
    shuttles, requests = generate_benchmark_50_dataset()
    optimizer = MultiShuttleOptimizer(shuttles)
    plan = optimizer.generate_plan(requests)

    baseline_engine = FixedRouteBaseline(shuttles)
    baseline_metrics = baseline_engine.run_baseline(requests)

    comparisons = compare_plans(plan["metrics"], baseline_metrics)
    assert len(comparisons) == 7

    # Dynamic system should achieve lower waiting times and travel distance than static bus loops
    dist_comp = next(c for c in comparisons if c["metric_name"] == "Total Travel Distance (km)")
    wait_comp = next(c for c in comparisons if c["metric_name"] == "Avg Passenger Waiting Time (min)")
    assert dist_comp["improvement_pct"] > 0
    assert wait_comp["improvement_pct"] > 0

def test_disruption_recovery_road_closure():
    """Verify dynamic recovery when a key road segment is blocked."""
    shuttles, requests = generate_benchmark_50_dataset()
    optimizer = MultiShuttleOptimizer(shuttles)
    plan = optimizer.generate_plan(requests)

    engine = DisruptionRecoveryEngine(plan, shuttles, requests)
    # Simulate blocking Silk Board to HSR link
    res = engine.simulate_road_closure("HUB_SILKBOARD", "HSR_SECTOR_7", "Test Monsoon Waterlogging")

    assert res["disruption_type"] == "road_closure"
    assert len(res["revised_routes"]) == len(plan["routes"])
    # City network should remain unblocked after test
    assert not city_network.blocked_edges

def test_disruption_recovery_shuttle_breakdown():
    """Verify dynamic recovery when a shuttle breaks down."""
    shuttles, requests = generate_benchmark_50_dataset()
    optimizer = MultiShuttleOptimizer(shuttles)
    plan = optimizer.generate_plan(requests)

    engine = DisruptionRecoveryEngine(plan, shuttles, requests)
    res = engine.simulate_shuttle_breakdown("SHUTTLE_2", "Test Engine Breakdown")

    assert res["disruption_type"] == "shuttle_breakdown"
    assert res["passengers_affected"] > 0
    assert "reassigned" in res["message"]
