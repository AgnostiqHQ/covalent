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

from fastapi import APIRouter

from covalent_ui.os_api.api_v0.utils.sqlite_loader import (
    get_electrons,
    get_lattice,
    get_links,
    load_file,
)

routes = APIRouter()


@routes.get("/load-sqlite")
async def get_sqlite():
    return await get_lattice()


@routes.post("/load-sqlite")
async def load_sqlite():
    return await load_file()


@routes.get("/get-electrons")
async def get_elec():
    return await get_electrons()


@routes.get("/get-link")
async def get_electron_link():
    return await get_links()
