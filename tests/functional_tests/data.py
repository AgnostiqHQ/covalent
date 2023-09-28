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

"""
Mock data for integration testing.
"""

import os

import covalent as ct
from covalent._results_manager import Result

TEST_RESULTS_DIR = os.environ.get("COVALENT_DATA_DIR") or ct.get_config("dispatcher.results_dir")


def get_mock_result() -> Result:
    """Construct and return a result object corresponding to a lattice."""

    @ct.electron
    def identity(x):
        return x

    @ct.lattice
    def pipeline(y):
        return identity(x=y)

    pipeline.build_graph(y=1)

    return Result(lattice=pipeline)


def get_mock_result_2() -> Result:
    """Construct and return a result object corresponding to a lattice."""

    @ct.electron
    def identity(x):
        return x

    @ct.electron
    def product(x, y):
        return x * y

    @ct.lattice
    def pipeline(x, y):
        res = product(x=x, y=y)
        return identity(x=res)

    pipeline.build_graph(x=1, y=1)

    return Result(
        lattice=pipeline,
    )


def get_mock_result_3() -> Result:
    """Construct and return a result object corresponding to a lattice."""

    @ct.lattice
    @ct.electron
    def pipeline(x, y):
        return x * y

    pipeline.build_graph(x=1, y=1)

    return Result(
        lattice=pipeline,
    )
