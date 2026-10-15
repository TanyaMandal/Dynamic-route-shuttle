from fastapi import APIRouter, HTTPException
from typing import List, Optional
from app.models.schemas import PickupRequestCreate, PickupRequestResponse
from app.database import store
import uuid

router = APIRouter(prefix="/api/requests", tags=["Pickup Requests"])

@router.get("", response_model=List[PickupRequestResponse])
def get_requests(user_id: Optional[str] = None):
    if user_id:
        return [r for r in store.requests if r.get("user_id") == user_id]
    return store.requests

@router.post("", response_model=PickupRequestResponse)
def create_pickup_request(req_data: PickupRequestCreate, user_id: Optional[str] = "EMP_001"):
    # FR-04: Validate coordinates and inputs
    if not (12.7 <= req_data.pickup_lat <= 13.2 and 77.4 <= req_data.pickup_lng <= 77.9):
        raise HTTPException(status_code=400, detail="Pickup coordinates outside city service boundary")
        
    new_req = req_data.dict()
    new_req["id"] = f"REQ_{uuid.uuid4().hex[:6].upper()}"
    new_req["user_id"] = user_id
    new_req["status"] = "pending"
    new_req["unserved_reason"] = None
    
    store.requests.append(new_req)
    return new_req

@router.delete("/{request_id}")
def cancel_pickup_request(request_id: str):
    req = next((r for r in store.requests if r["id"] == request_id), None)
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")
        
    req["status"] = "cancelled"
    return {"message": "Pickup request cancelled"}
