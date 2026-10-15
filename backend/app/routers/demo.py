from fastapi import APIRouter
from typing import Dict, Any
from app.database import store
from app.services.seeder import generate_benchmark_50_dataset

router = APIRouter(prefix="/api/demo", tags=["Demo & Benchmark"])

@router.post("/seed-50")
def seed_benchmark_dataset():
    """Seeds exactly 50 employees across 6 residential sectors and 5 shuttles."""
    shuttles, requests = generate_benchmark_50_dataset()
    store.shuttles = [dict(s) for s in shuttles]
    store.requests = [dict(r) for r in requests]
    store.plans = []
    store.disruptions = []

    return {
        "message": "Benchmark dataset initialized successfully with 50 employees and 5 shuttles.",
        "shuttle_count": len(store.shuttles),
        "request_count": len(store.requests),
        "total_fleet_capacity": sum(s["seat_capacity"] for s in store.shuttles)
    }

@router.post("/reset")
def reset_system():
    store.requests = []
    store.plans = []
    store.disruptions = []
    return {"message": "System state reset. Ready for new scenario."}
