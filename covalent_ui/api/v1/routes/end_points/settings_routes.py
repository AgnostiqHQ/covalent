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
# Relief from the License may be granted by purchasing a commercial license.

"""Settings Route"""


from typing import Dict, Optional

from fastapi import APIRouter

from covalent._shared_files.config import _ConfigManager as settings
from covalent_ui.api.v1.models.settings_model import (
    GetSettingsResponseModel,
    UpdateSettingsResponseModel,
    Validators,
)

routes: APIRouter = APIRouter()


@routes.get("/settings", response_model=GetSettingsResponseModel)
def get_settings():
    """
    Read the configuration from file.

    Args:
        None

    Returns:
        Configuration file as json object.
    """
    return GetSettingsResponseModel(data=settings().config_data)


@routes.post("/settings", response_model=UpdateSettingsResponseModel)
def post_settings(new_entries: Optional[Dict] = None, override_existing: bool = True):
    """
    Update the exising configuration dictionary with the configuration sent in request body.
    Only executor fields are writable.

    Args:
        new_entries: Dictionary of new entries added or updated in the config.
        override_existing: If True (default), config values from the config file
            or the input dictionary (new_entries) take precedence over any existing
            values in the config.

    Returns:
        settings updated successfully when updated.
    """
    if len([validator.value for validator in Validators if validator.value in new_entries]) != 0:
        return UpdateSettingsResponseModel(data="Field cannot be updated")
    settings().update_config(new_entries, override_existing)
    return UpdateSettingsResponseModel(data="settings updated successfully")
