from typing import Any, Sequence

from app import crud
from app.api import deps
from app.schemas.recipe import Recipe, RecipeCreate
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

router = APIRouter()


# @router.get("/", status_code=200, response_model=Sequence[Recipe])
# def fetch_recipes(
#     *,
#     max_results: int = 10,
#     db: Session = Depends(deps.get_db),
# ) -> Any:
#     """
#     Fetch all recipes
#     """

#     return crud.recipe.get_all(db=db, limit=max_results)


@router.put("/run", status_code=202, response_model=Recipe)
def run_task(*, some_object_yet_to_decide: Any) -> Any:
    """
    API Endpoint (/api/task/run) to run a task
    """

    return {"run_task": "run task"}


@router.get("/status", status_code=200, response_model=Recipe)
def check_status(*, another_object_yet_to_decide: Any) -> Any:
    """
    API Endpoint (/api/task/status) to check status of a task
    """

    return {"check_status": "check status"}


@router.delete("/cancel", status_code=200, response_model=Recipe)
def cancel_task(*, another_object_yet_to_decide: Any) -> Any:
    """
    API Endpoint (/api/task/cancel) to cancel a task
    """

    return {"cancel_task": "cancel task"}


# @router.post("/", status_code=201, response_model=Recipe)
# def create_recipe(*, recipe_in: RecipeCreate, db: Session = Depends(deps.get_db)) -> dict:
#     """
#     Create a new recipe in the database.
#     """

#     return crud.recipe.create(db=db, obj_in=recipe_in)
