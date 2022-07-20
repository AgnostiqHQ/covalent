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

"""
Tests for self-contained entry point for the dispatcher
"""

import time
from concurrent.futures import ThreadPoolExecutor

import covalent
import covalent_dispatcher as dispatcher

from .data import get_mock_result


def test_run_dispatcher():
    """
    Test run_dispatcher by passing a result object for a lattice and check if no exception is raised.
    """

    workflow_pool = ThreadPoolExecutor()
    task_pool = ThreadPoolExecutor()

    try:
        dispatch_id = dispatcher.run_dispatcher(
            json_lattice=get_mock_result().lattice.serialize_to_json(),
            workflow_pool=workflow_pool,
            tasks_pool=task_pool,
        )
    except Exception as e:
        assert False, f"Exception raised: {e}"

    workflow_pool.shutdown()
    task_pool.shutdown()
