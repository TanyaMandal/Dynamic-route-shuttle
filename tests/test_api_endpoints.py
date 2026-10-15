import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import store

client = TestClient(app)

def test_api_root():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert "Dynamic Employee Shuttle" in data["project"]

def test_api_auth_login():
    response = client.post("/api/auth/login", json={"email": "admin@techpark.com", "password": "admin123"})
    assert response.status_code == 200
    data = response.json()
    assert data["role"] == "admin"
    assert "access_token" in data

def test_seed_and_generate_plan():
    # 1. Seed 50 benchmark requests
    seed_res = client.post("/api/demo/seed-50")
    assert seed_res.status_code == 200
    assert seed_res.json()["request_count"] == 50

    # 2. Generate plan
    plan_res = client.post("/api/plans/generate")
    assert plan_res.status_code == 200
    plan = plan_res.json()
    assert "metrics" in plan
    assert len(plan["routes"]) > 0
    assert plan["metrics"]["total_distance_km"] > 0
    assert plan["metrics"]["deadline_compliance_pct"] > 0

    plan_id = plan["id"]

    # 3. Compare with baseline
    compare_res = client.get(f"/api/plans/{plan_id}/compare")
    assert compare_res.status_code == 200
    comp_data = compare_res.json()
    assert len(comp_data["comparisons"]) == 7
    assert "Dynamic system reduced" in comp_data["summary"]

    # 4. Simulate road closure disruption
    disrupt_res = client.post("/api/disruptions/simulate", json={
        "disruption_type": "road_closure",
        "plan_id": plan_id,
        "affected_entity_id": "HUB_SILKBOARD__HSR_SECTOR_7",
        "description": "Silk Board Monsoon Waterlogging"
    })
    assert disrupt_res.status_code == 200
    disrupt_data = disrupt_res.json()
    assert len(disrupt_data["revised_routes"]) > 0
