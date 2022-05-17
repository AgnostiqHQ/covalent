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

import os
from typing import List, Union

from dotenv import find_dotenv, load_dotenv
from pydantic import AnyHttpUrl, BaseSettings, validator

HOME_PATH = os.environ.get("XDG_CACHE_HOME") or (os.environ["HOME"] + "/.cache")
load_dotenv(os.path.join(HOME_PATH, "covalent", ".env"))


class Settings(BaseSettings):
    API_V0_STR: str = "/api/v0"
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []
    RUNNER_SVC_PORT: int = 8003
    RUNNER_SVC_HOST: str = "localhost"
    RESULTS_SVC_PORT: int = 8005
    RESULTS_SVC_HOST: str = "localhost"
    DISPATCHER_SVC_PORT: int = 8002
    DISPATCHER_SVC_HOST: str = "localhost"
    UI_SVC_PORT: int = 8000
    UI_SVC_HOST: str = "localhost"

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    class Config:
        case_sensitive = True


settings = Settings()

print("Configuration:")
print(settings)
