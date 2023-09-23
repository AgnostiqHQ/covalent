# Copyright 2021 Agnostiq Inc.
#
# This file is part of Covalent.
#
# Licensed under the Apache License 2.0 (the "License"). A copy of the
# License may be obtained with this software package or at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Use of this file is prohibited except in compliance with the License.
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Settings Route"""


from typing import Dict

from fastapi import APIRouter, HTTPException, status

from covalent._shared_files.config import ConfigManager
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
    server = {}
    client = {}

    settings = ConfigManager()

    [
        server.update({validator.value: settings.config_data[validator.value]})
        for validator in Validators
    ]
    [
        client.update({keys: settings.config_data[keys]})
        for keys in settings.config_data
        if keys not in server
    ]
    return GetSettingsResponseModel(server=server, client=client)


@routes.post("/settings", response_model=UpdateSettingsResponseModel)
def post_settings(new_entries: Dict, override_existing: bool = True):
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
    file_type = next(iter(new_entries.keys()))
    first_key = next(iter(new_entries[file_type].keys()))
    if first_key == "":
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=[
                {
                    "loc": ["path", "update-settings"],
                    "msg": "Key should not be empty string",
                    "type": None,
                }
            ],
        )
    if len([validator.value for validator in Validators if validator.value in new_entries]) != 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=[
                {
                    "loc": ["path", "update-settings"],
                    "msg": "Field cannot be updated",
                    "type": None,
                }
            ],
        )
    settings = ConfigManager()
    settings.update_config(new_entries[file_type], override_existing)
    return UpdateSettingsResponseModel(data="settings updated successfully")
