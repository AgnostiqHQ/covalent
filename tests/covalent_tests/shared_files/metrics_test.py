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

"""Unit tests for metrics module."""

from covalent._shared_files.metrics import PlatformMetadata


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
