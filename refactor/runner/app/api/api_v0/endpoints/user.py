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
from app.schemas.user import User, UserCreate, UserUpdate
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

router = APIRouter()


@router.get("/", status_code=200, response_model=Sequence[User])
def fetch_users(
    *,
    max_results: int = 10,
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Fetch all users
    """

    return crud.user.get_all(db=db, limit=max_results)


@router.get("/{user_id}", status_code=200, response_model=User)
def fetch_user(
    *,
    user_id: int,
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Fetch a single user by ID
    """
    result = crud.user.get(db=db, id=user_id)
    if not result:
        # the exception is raised, not returned - you will get a validation
        # error otherwise.
        raise HTTPException(status_code=404, detail=f"User with ID {user_id} not found")

    return result


@router.delete("/{user_id}", status_code=200, response_model=User)
def delete_user(
    *,
    user_id: int,
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Fetch a single user by ID
    """

    return crud.user.remove(db=db, id=user_id)


@router.put("/{user_id}", status_code=201, response_model=User)
def update_user(*, user_id: int, user_in: UserUpdate, db: Session = Depends(deps.get_db)) -> dict:
    """
    Update a user in the database.
    """

    user = crud.user.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=400, detail=f"User with ID: {user_in.id} not found.")

    return crud.user.update(db=db, obj_in=user_in, db_obj=user)


@router.post("/", status_code=201, response_model=User)
def create_user(*, user_in: UserCreate, db: Session = Depends(deps.get_db)) -> dict:
    """
    Create a new user in the database.
    """

    return crud.user.create(db=db, obj_in=user_in)
