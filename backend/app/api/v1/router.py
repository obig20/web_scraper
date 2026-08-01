"""API v1 router aggregation."""

from fastapi import APIRouter

from app.api.v1 import viral

api_router = APIRouter()

@api_router.get("/")
async def root():
    return {"message": "Crime Horror Research Engine API", "status": "running"}

# Include viral content routes
api_router.include_router(viral.router)
