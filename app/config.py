import os
from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    model_config = ConfigDict(case_sensitive=True, extra="ignore")

    PROJECT_NAME: str = "Dynamic Employee Shuttle Routing System"
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "https://your-project.supabase.co")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "your-anon-or-service-role-key")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "supersecretkey_mca_minor_project_shuttle_2026")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))
    
    MAX_WALKING_DISTANCE_METERS: float = float(os.getenv("MAX_WALKING_DISTANCE_METERS", "400.0"))
    SHUTTLE_DEFAULT_SPEED_KMH: float = float(os.getenv("SHUTTLE_DEFAULT_SPEED_KMH", "30.0"))
    
    OFFICE_NAME: str = os.getenv("OFFICE_NAME", "Central Tech Park Campus")
    OFFICE_LAT: float = float(os.getenv("OFFICE_LAT", "12.9716"))
    OFFICE_LNG: float = float(os.getenv("OFFICE_LNG", "77.5946"))

settings = Settings()
