from fastapi import APIRouter

from app.api.api_v1.endpoints import submit

api_router = APIRouter()
api_router.include_router(submit.router, prefix="/submit", tags=["Submit"])
