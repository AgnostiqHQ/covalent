from app.api.api_v1.endpoints import recipe, user
from fastapi import APIRouter

api_router = APIRouter()
api_router.include_router(recipe.router, prefix="/recipes", tags=["recipes"])
api_router.include_router(user.router, prefix="/users", tags=["users"])
