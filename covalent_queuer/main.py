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

from pathlib import Path

from app.api.api_v0.api import api_router
from app.api.health import health_router
from app.core.config import settings
from fastapi import FastAPI

BASE_PATH = Path(__file__).resolve().parent

app = FastAPI(title="Covalent Queuer Service API")


app.include_router(api_router, prefix=settings.API_V0_STR)
app.include_router(health_router)

if __name__ == "__main__":
    # Use this for debugging purposes only
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.QUEUER_SVC_HOST,
        port=settings.QUEUER_SVC_PORT,
        log_level="debug",
        reload=True,
    )
