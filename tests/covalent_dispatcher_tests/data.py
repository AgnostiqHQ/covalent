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
Mock data for integration testing.
"""

import covalent as ct
from covalent._results_manager import Result

TEST_RESULTS_DIR = "/tmp/results"


def get_mock_result() -> Result:
    """Construct and return a result object corresponding to a lattice."""

    @ct.electron
    def identity(x):
        return x

    @ct.lattice(results_dir=TEST_RESULTS_DIR)
    def pipeline(y):
        return identity(x=y)

    pipeline.build_graph(y=1)

    return Result(
        lattice=pipeline,
        results_dir=pipeline.metadata["results_dir"],
    )


def get_mock_result_2() -> Result:
    """Construct and return a result object corresponding to a lattice."""

    @ct.electron
    def identity(x):
        return x

    @ct.electron
    def product(x, y):
        return x * y

    @ct.lattice(results_dir=TEST_RESULTS_DIR)
    def pipeline(x, y):
        res = product(x=x, y=y)
        return identity(x=res)

    pipeline.build_graph(x=1, y=1)

    return Result(
        lattice=pipeline,
        results_dir=pipeline.metadata["results_dir"],
    )


def get_mock_result_3() -> Result:
    """Construct and return a result object corresponding to a lattice."""

    @ct.lattice(results_dir=TEST_RESULTS_DIR)
    @ct.electron
    def pipeline(x, y):
        return x * y

    pipeline.build_graph(x=1, y=1)

    return Result(
        lattice=pipeline,
        results_dir=pipeline.metadata["results_dir"],
    )
