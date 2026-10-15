from fastapi import APIRouter, HTTPException
from typing import List
from app.models.schemas import ShuttleCreate, ShuttleUpdate, ShuttleResponse
from app.database import store
from app.services.seeder import SEED_SHUTTLES
import uuid

router = APIRouter(prefix="/api/shuttles", tags=["Fleet Management"])

# Ensure store has default shuttles
if not store.shuttles:
    store.shuttles = [dict(s) for s in SEED_SHUTTLES]

@router.get("", response_model=List[ShuttleResponse])
def get_all_shuttles():
    return store.shuttles

@router.post("", response_model=ShuttleResponse)
def create_shuttle(shuttle_data: ShuttleCreate):
    new_shuttle = shuttle_data.dict()
    new_shuttle["id"] = f"SHUTTLE_{uuid.uuid4().hex[:6].upper()}"
    store.shuttles.append(new_shuttle)
    return new_shuttle

@router.put("/{shuttle_id}", response_model=ShuttleResponse)
def update_shuttle(shuttle_id: str, updates: ShuttleUpdate):
    shuttle = next((s for s in store.shuttles if s["id"] == shuttle_id), None)
    if not shuttle:
        raise HTTPException(status_code=404, detail="Shuttle not found")
    
    update_data = updates.dict(exclude_unset=True)
    for k, v in update_data.items():
        shuttle[k] = v
    return shuttle

@router.delete("/{shuttle_id}")
def delete_shuttle(shuttle_id: str):
    global store
    store.shuttles = [s for s in store.shuttles if s["id"] != shuttle_id]
    return {"message": "Shuttle removed successfully"}
