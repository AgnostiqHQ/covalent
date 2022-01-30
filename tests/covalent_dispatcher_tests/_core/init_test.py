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
Tests for the core functionality of the dispatcher.
"""

import cloudpickle as pickle
import covalent as ct

from covalent_dispatcher._core import _plan_workflow
from covalent._results_manager import Result
from covalent._results_manager import results_manager as rm

TEST_RESULTS_DIR = "/tmp/results"


def get_mock_result() -> Result:
    """Construct a mock result object corresponding to a lattice."""

    import sys

    @ct.electron
    def task(x):
        print(f"stdout: {x}")
        print("Error!", file=sys.stderr)
        return x


    @ct.lattice(results_dir=TEST_RESULTS_DIR)
    def pipeline(x):
        return task(x)

    pipeline.build_graph(x="absolute")
    pipeline.check_consumable()

    return Result(
        lattice=pipeline,
        results_dir=pipeline.metadata["results_dir"],
    )


def test_plan_workflow():
    """Test workflow planning method.
    """

    mock_result = get_mock_result()
    _plan_workflow(result_object=mock_result)

    # Updated transport graph post planning
    updated_tg = pickle.loads(mock_result.lattice.transport_graph.serialize(metadata_only=True))

    assert 'results_dir' in updated_tg['nodes'][0]['exec_plan'].execution_args
