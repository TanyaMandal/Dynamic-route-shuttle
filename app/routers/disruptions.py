from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from app.models.schemas import DisruptionSimulateRequest, DisruptionRecoveryResponse
from app.database import store
from app.services.road_network import city_network
from app.services.disruptions import DisruptionRecoveryEngine, PRESET_DISRUPTIONS
import uuid

router = APIRouter(prefix="/api/disruptions", tags=["Disruption Simulation"])

@router.get("/presets")
def get_presets():
    return PRESET_DISRUPTIONS

@router.get("/road-segments")
def get_road_segments():
    return city_network.get_road_segments()

@router.post("/simulate", response_model=DisruptionRecoveryResponse)
def simulate_disruption(payload: DisruptionSimulateRequest):
    plan = next((p for p in store.plans if p["id"] == payload.plan_id), None)
    if not plan:
        # Fall back to latest plan
        if not store.plans:
            raise HTTPException(status_code=400, detail="Please generate a route plan first before simulating disruptions.")
        plan = store.plans[-1]

    engine = DisruptionRecoveryEngine(plan, store.shuttles, store.requests)

    if payload.disruption_type == "road_closure":
        # Expecting entity format "NODEA__NODEB"
        if "__" not in payload.affected_entity_id:
            raise HTTPException(status_code=400, detail="Invalid road segment format. Use 'NODE_A__NODE_B'")
        node_u, node_v = payload.affected_entity_id.split("__")
        recovery_result = engine.simulate_road_closure(node_u, node_v, payload.description or "Road Closure")
    else:
        # Shuttle breakdown
        recovery_result = engine.simulate_shuttle_breakdown(payload.affected_entity_id, payload.description or "Shuttle Breakdown")

    disruption_id = f"DISRUPT_{uuid.uuid4().hex[:6].upper()}"
    revised_plan_id = f"PLAN_REVISED_{uuid.uuid4().hex[:6].upper()}"

    # Record disruption
    store.disruptions.append({
        "id": disruption_id,
        "type": payload.disruption_type,
        "description": payload.description,
        "affected_entity": payload.affected_entity_id,
        "extra_distance_km": recovery_result["extra_distance_km"],
        "extra_delay_min": recovery_result["extra_delay_min"]
    })

    return {
        "disruption_id": disruption_id,
        "disruption_type": payload.disruption_type,
        "description": payload.description or "Simulated Disruption",
        "original_plan_id": plan["id"],
        "revised_plan_id": revised_plan_id,
        "extra_distance_km": recovery_result["extra_distance_km"],
        "extra_delay_min": recovery_result["extra_delay_min"],
        "passengers_reassigned": recovery_result["passengers_reassigned"],
        "passengers_unserved": recovery_result["passengers_unserved"],
        "revised_routes": recovery_result["revised_routes"],
        "message": recovery_result["message"]
    }
