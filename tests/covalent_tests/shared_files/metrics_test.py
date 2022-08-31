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

"""Unit tests for metrics module."""

from covalent._shared_files.metrics import (
    PerformanceMetrics,
    PlatformMetadata,
    WorkflowBenchmarkResult,
)


def test_platform_metdata():
    """Test the platform metadata object."""

    pmd = PlatformMetadata()
    assert pmd.arch is not None
    assert pmd.system is not None
    assert pmd.machine is not None
    assert pmd.os is not None
    assert pmd.python_version is not None
    print(pmd.arch)
    print(pmd.system)
    print(pmd.machine)
    print(pmd.os)
    print(pmd.python_version)
