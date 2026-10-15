from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
from app.models.schemas import PlanResponse, PlanComparisonResponse
from app.database import store
from app.services.optimizer import MultiShuttleOptimizer
from app.services.baseline import FixedRouteBaseline, compare_plans
import uuid
from datetime import datetime

router = APIRouter(prefix="/api/plans", tags=["Routing & Planning"])

@router.post("/generate", response_model=PlanResponse)
def generate_route_plan():
    # Load pending or active requests
    active_requests = [r for r in store.requests if r.get("status") in ("pending", "assigned")]
    if not active_requests:
        raise HTTPException(status_code=400, detail="No active pickup requests found to optimize.")
        
    active_shuttles = [s for s in store.shuttles if s.get("status") == "active"]
    if not active_shuttles:
        raise HTTPException(status_code=400, detail="No active shuttles in fleet.")

    # Run VRPTW multi-shuttle optimizer
    optimizer = MultiShuttleOptimizer(active_shuttles)
    plan_output = optimizer.generate_plan(active_requests)

    plan_id = f"PLAN_{uuid.uuid4().hex[:8].upper()}"
    plan_record = {
        "id": plan_id,
        "plan_name": f"Daily Morning Shift Plan ({datetime.now().strftime('%Y-%m-%d %H:%M')})",
        "status": "finalized",
        "metrics": plan_output["metrics"],
        "routes": plan_output["routes"],
        "unserved_requests": plan_output["unserved_requests"],
        "created_at": datetime.now().isoformat()
    }

    # Store plan
    store.plans.append(plan_record)

    # Mark requests as assigned
    for r in active_requests:
        is_unserved = any(u["request_id"] == r["id"] for u in plan_output["unserved_requests"])
        if is_unserved:
            r["status"] = "unserved"
            r["unserved_reason"] = "Capacity exceeded"
        else:
            r["status"] = "assigned"

    return plan_record

@router.get("/latest", response_model=PlanResponse)
def get_latest_plan():
    if not store.plans:
        raise HTTPException(status_code=404, detail="No plans generated yet. Click 'Generate Route Plan'.")
    return store.plans[-1]

@router.get("/{plan_id}", response_model=PlanResponse)
def get_plan_by_id(plan_id: str):
    plan = next((p for p in store.plans if p["id"] == plan_id), None)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    return plan

@router.get("/{plan_id}/compare", response_model=PlanComparisonResponse)
def compare_plan_with_baseline(plan_id: str):
    plan = next((p for p in store.plans if p["id"] == plan_id), None)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    # Run baseline on current requests and shuttles
    baseline_solver = FixedRouteBaseline(store.shuttles)
    active_requests = [r for r in store.requests if r.get("status") != "cancelled"]
    baseline_metrics = baseline_solver.run_baseline(active_requests)

    comparisons = compare_plans(plan["metrics"], baseline_metrics)

    summary_text = (
        f"Dynamic system reduced total travel distance by {comparisons[0]['improvement_pct']}% "
        f"and cut waiting time by {comparisons[1]['improvement_pct']}%, with {plan['metrics']['deadline_compliance_pct']}% on-time arrival rate."
    )

    return {
        "plan_id": plan_id,
        "comparisons": comparisons,
        "summary": summary_text
    }
