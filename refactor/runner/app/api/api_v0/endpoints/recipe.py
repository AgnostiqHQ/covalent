# Copyright 2021 Agnostiq Inc.
#
# This file is part of Covalent.
#
# Licensed under the GNU Affero General Public License 3.0 (the "License").
# A copy of the License may be obtained with this software package or at
#
#      https://www.gnu.org/licenses/agpl-3.0.en.html
#
# Use of this file is prohibited except in compliance with the License. Any
# modifications or derivative works of this file must retain this copyright
# notice, and modified files must contain a notice indicating that they have
# been altered from the originals.
#
# Covalent is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE. See the License for more details.
#
# Relief from the License may be granted by purchasing a commercial license.


from typing import Any, Optional, Sequence

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


# TODO: Change response mode to a custom class similar to found in Recipe schema


@router.put("/run", status_code=202, response_model=dict)
def run_task(*, some_object_yet_to_decide: Optional[Any] = None) -> Any:
    """
    API Endpoint (/api/task/run) to run a task
    """

    return {"run_task": "run task"}


@router.get("/status", status_code=200, response_model=dict)
def check_status(*, another_object_yet_to_decide: Optional[Any] = None) -> Any:
    """
    API Endpoint (/api/task/status) to check status of a task
    """

    return {"check_status": "check status"}


@router.delete("/cancel", status_code=200, response_model=dict)
def cancel_task(*, another_object_yet_to_decide: Optional[Any] = None) -> Any:
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
