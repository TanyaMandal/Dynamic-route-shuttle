from fastapi import APIRouter, HTTPException, status
from app.models.schemas import UserRegister, UserLogin, TokenResponse
from app.database import store
import uuid

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

@router.post("/register", response_model=TokenResponse)
def register(user_data: UserRegister):
    # Check if user already exists
    for u in store.users:
        if u["email"].lower() == user_data.email.lower():
            raise HTTPException(status_code=400, detail="Email already registered")
            
    user_id = str(uuid.uuid4())
    new_user = {
        "id": user_id,
        "email": user_data.email,
        "full_name": user_data.full_name,
        "password": user_data.password, # In production hash with bcrypt
        "role": user_data.role
    }
    store.users.append(new_user)
    
    return TokenResponse(
        access_token=f"mock_token_{user_id}",
        user_id=user_id,
        email=new_user["email"],
        full_name=new_user["full_name"],
        role=new_user["role"]
    )

@router.post("/login", response_model=TokenResponse)
def login(creds: UserLogin):
    user = next((u for u in store.users if u["email"].lower() == creds.email.lower() and u["password"] == creds.password), None)
    if not user:
        # Default mock admin and employee credentials for easy testing
        if creds.email == "admin@techpark.com" and creds.password == "admin123":
            user = {
                "id": "ADMIN_001",
                "email": "admin@techpark.com",
                "full_name": "Transport Coordinator",
                "role": "admin"
            }
        elif creds.email == "employee@techpark.com" and creds.password == "emp123":
            user = {
                "id": "EMP_001",
                "email": "employee@techpark.com",
                "full_name": "Aarav Sharma",
                "role": "employee"
            }
        else:
            raise HTTPException(status_code=401, detail="Invalid email or password")
            
    return TokenResponse(
        access_token=f"mock_token_{user['id']}",
        user_id=user["id"],
        email=user["email"],
        full_name=user["full_name"],
        role=user["role"]
    )
