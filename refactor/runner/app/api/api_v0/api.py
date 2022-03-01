from app.api.api_v0.endpoints import recipe, user
from fastapi import APIRouter

api_router = APIRouter()

# Will be /task instead of /recipes or /users
api_router.include_router(recipe.router, prefix="/task", tags=["task"])
# api_router.include_router(user.router, prefix="/users", tags=["users"])
