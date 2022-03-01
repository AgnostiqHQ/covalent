from fastapi import APIRouter

from app.api.api_v1.endpoints import workflow

api_router = APIRouter()
api_router.include_router(workflow.router, prefix="/workflow", tags=["Workflow"])
