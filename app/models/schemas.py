from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import time, datetime

# --- Auth Schemas ---
class UserRegister(BaseModel):
    email: str
    full_name: str
    password: str
    role: str = Field(default="employee", pattern="^(employee|admin)$")

class UserLogin(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    email: str
    full_name: str
    role: str

# --- Shuttle Schemas ---
class ShuttleCreate(BaseModel):
    name: str
    seat_capacity: int = Field(gt=0, le=50)
    start_location_name: str
    start_lat: float
    start_lng: float
    status: str = "active"

class ShuttleUpdate(BaseModel):
    name: Optional[str] = None
    seat_capacity: Optional[int] = None
    status: Optional[str] = None

class ShuttleResponse(ShuttleCreate):
    id: str
    created_at: Optional[str] = None

# --- Pickup Request Schemas ---
class PickupRequestCreate(BaseModel):
    employee_name: str
    pickup_lat: float
    pickup_lng: float
    pickup_location_name: Optional[str] = "Pickup Location"
    destination: str = "Central Tech Park Campus"
    arrival_deadline: str = "09:00:00"  # HH:MM:SS

class PickupRequestResponse(PickupRequestCreate):
    id: str
    user_id: Optional[str] = None
    status: str
    unserved_reason: Optional[str] = None
    created_at: Optional[str] = None

# --- Routing & Plan Schemas ---
class RouteStopSchema(BaseModel):
    sequence_num: int
    stop_name: str
    lat: float
    lng: float
    estimated_arrival_time: str
    passenger_count: int
    passenger_names: List[str] = []

class RouteSchema(BaseModel):
    shuttle_id: str
    shuttle_name: str
    capacity: int
    assigned_passengers_count: int
    total_distance_km: float
    total_duration_min: float
    stops: List[RouteStopSchema]
    polyline: List[List[float]]  # [[lat, lng], ...]

class PlanMetricsSchema(BaseModel):
    total_distance_km: float
    total_travel_time_min: float
    avg_waiting_time_min: float
    vehicle_utilization_pct: float
    avg_walking_distance_m: float
    deadline_compliance_pct: float
    unserved_requests_count: int
    total_shuttles_used: int

class PlanResponse(BaseModel):
    id: str
    plan_name: str
    status: str
    metrics: PlanMetricsSchema
    routes: List[RouteSchema]
    unserved_requests: List[Dict[str, Any]] = []
    created_at: str

# --- Baseline Comparison Schema ---
class MetricComparison(BaseModel):
    metric_name: str
    baseline_value: float
    optimised_value: float
    improvement_pct: float
    target_direction: str  # "lower" or "higher"

class PlanComparisonResponse(BaseModel):
    plan_id: str
    comparisons: List[MetricComparison]
    summary: str

# --- Disruption Schemas ---
class DisruptionSimulateRequest(BaseModel):
    disruption_type: str = Field(..., pattern="^(road_closure|shuttle_breakdown)$")
    plan_id: str
    affected_entity_id: str  # e.g., "shuttle_id" or "nodeA_nodeB"
    description: Optional[str] = "Simulated Disruption"

class DisruptionRecoveryResponse(BaseModel):
    disruption_id: str
    disruption_type: str
    description: str
    original_plan_id: str
    revised_plan_id: str
    extra_distance_km: float
    extra_delay_min: float
    passengers_reassigned: int
    passengers_unserved: int
    revised_routes: List[RouteSchema]
    message: str
