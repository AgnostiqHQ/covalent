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


"""Caching for static attributes of a dispatch"""

from functools import lru_cache

from covalent._shared_files import logger
from covalent._shared_files.config import get_config

from .result import get_result_object

LRU_CACHE_SIZE = get_config("dispatcher.lru_num_dispatches")


app_log = logger.app_log


# This must only be used for static data as we don't have yet any
# intelligent invalidation logic.
@lru_cache(maxsize=LRU_CACHE_SIZE)
def get_cached_result_object(dispatch_id: str):
    srv_res = get_result_object(dispatch_id, bare=False)
    app_log.debug(f"Caching result {dispatch_id}")
    srv_res.populate_assets()
    return srv_res
