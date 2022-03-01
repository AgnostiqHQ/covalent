from fastapi import APIRouter

from app.api.api_v1.endpoints import workflow, fs

api_router = APIRouter()
api_router.include_router(workflow.router, prefix="/workflow", tags=["Workflow"])
api_router.include_router(fs.router, prefix="/fs", tags=["Data"])
