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


# Below might be /api/task/status

# @router.get("/{recipe_id}", status_code=200, response_model=Recipe)
# def fetch_recipe(
#     *,
#     recipe_id: int,
#     db: Session = Depends(deps.get_db),
# ) -> Any:
#     """
#     Fetch a single recipe by ID
#     """
#     result = crud.recipe.get(db=db, id=recipe_id)
#     if not result:
#         # the exception is raised, not returned - you will get a validation
#         # error otherwise.
#         raise HTTPException(status_code=404, detail=f"Recipe with ID {recipe_id} not found")

#     return result


# Below might be /api/task/cancel

# @router.delete("/{recipe_id}", status_code=200, response_model=Recipe)
# def delete_recipe(
#     *,
#     recipe_id: int,
#     db: Session = Depends(deps.get_db),
# ) -> Any:
#     """
#     Fetch a single recipe by ID
#     """

#     return crud.recipe.remove(db=db, id=recipe_id)


# Below might be /api/task/run

# @router.put("/{recipe_id}", status_code=201, response_model=Recipe)
# def update_recipe(
#     *, recipe_id: int, recipe_in: RecipeCreate, db: Session = Depends(deps.get_db)
# ) -> dict:
#     """
#     Update a recipe in the database.
#     """

#     recipe = crud.recipe.get(db, id=recipe_id)
#     if not recipe:
#         raise HTTPException(status_code=400, detail=f"Recipe with ID: {recipe_in.id} not found.")

#     return crud.recipe.update(db=db, obj_in=recipe_in, db_obj=recipe)


# @router.post("/", status_code=201, response_model=Recipe)
# def create_recipe(*, recipe_in: RecipeCreate, db: Session = Depends(deps.get_db)) -> dict:
#     """
#     Create a new recipe in the database.
#     """

#     return crud.recipe.create(db=db, obj_in=recipe_in)
