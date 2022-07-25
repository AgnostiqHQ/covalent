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
Integration test for choosing Conda environments within an executor.
"""

import covalent as ct
import covalent._results_manager.results_manager as rm
from covalent_dispatcher._db.dispatchdb import DispatchDB


def test_using_current_env() -> None:
    """Test that the Conda environment can be specified in the executor
    initialization and used in a simple electron."""

    tmp_executor = ct.executor.LocalExecutor()
    has_conda = tmp_executor.get_conda_path()
    if not has_conda:
        return

    tmp_executor.get_conda_envs()
    conda_env = tmp_executor.current_env

    executor = ct.executor.LocalExecutor(conda_env=conda_env, current_env_on_conda_fail=True)

    @ct.electron(executor=executor)
    def passthrough(x):
        return x

    @ct.lattice()
    def workflow(y):
        return passthrough(x=y)

    dispatch_id = ct.dispatch(workflow)(y="input")
    result = ct.get_result(dispatch_id, wait=True)

    assert result.result == "input"
