import logging
from typing import Dict, Any, List, Optional
from app.config import settings

logger = logging.getLogger("uvicorn")

supabase_client = None

def get_supabase():
    global supabase_client
    if supabase_client is not None:
        return supabase_client

    if settings.SUPABASE_URL and "your-project" not in settings.SUPABASE_URL and settings.SUPABASE_KEY and "your-anon" not in settings.SUPABASE_KEY:
        try:
            from supabase import create_client
            supabase_client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
            logger.info("Connected to Supabase PostgreSQL database successfully.")
        except Exception as e:
            logger.warning(f"Failed to connect to Supabase: {e}. Falling back to high-performance local store.")
            supabase_client = None
    else:
        logger.info("Supabase placeholder detected. Using in-memory store for local testing/development.")
    return supabase_client

# Local fallback store so all algorithms, test cases, and demos work immediately
class LocalDataStore:
    def __init__(self):
        self.users: List[Dict[str, Any]] = []
        self.shuttles: List[Dict[str, Any]] = []
        self.requests: List[Dict[str, Any]] = []
        self.plans: List[Dict[str, Any]] = []
        self.routes: List[Dict[str, Any]] = []
        self.route_stops: List[Dict[str, Any]] = []
        self.disruptions: List[Dict[str, Any]] = []
        self.comparisons: List[Dict[str, Any]] = []

store = LocalDataStore()
