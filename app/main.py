from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, shuttles, requests, plans, disruptions, demo
from app.config import settings
from app.database import get_supabase
from app.services.seeder import generate_benchmark_50_dataset
from app.database import store

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Attempt Supabase connection or initialize demo defaults
    get_supabase()
    if not store.shuttles:
        shuttles, reqs = generate_benchmark_50_dataset()
        store.shuttles = [dict(s) for s in shuttles]
        store.requests = [dict(r) for r in reqs]
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Backend API for Dynamic Employee Shuttle Routing System with Shared Pickup Clustering, VRPTW Multi-Shuttle Routing, Disruption Recovery, and Baseline Comparison.",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware for React Native Expo
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(auth.router)
app.include_router(shuttles.router)
app.include_router(requests.router)
app.include_router(plans.router)
app.include_router(disruptions.router)
app.include_router(demo.router)

import os
from fastapi.responses import FileResponse

STATIC_INDEX = os.path.join(os.path.dirname(__file__), "static", "index.html")

@app.get("/app", response_class=FileResponse)
def serve_app():
    return FileResponse(STATIC_INDEX)

@app.get("/")
def root():
    return {
        "project": settings.PROJECT_NAME,
        "status": "online",
        "web_dashboard_url": "/app",
        "docs_url": "/docs",
        "active_shuttles": len(store.shuttles),
        "pending_requests": len(store.requests)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
