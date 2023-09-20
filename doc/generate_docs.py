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

import os
import subprocess


def run(clean_dir: bool = False) -> None:
    """Convenience function for generating documentation from code docstrings.

    Meant to be only called by setup.py in above directory.

    Args:
        clean_dir: If True, all generated files from the last build are removed,
            and not regenerated.
    """

    pwd = os.getcwd()
    os.chdir("doc")

    if clean_dir:
        print("Removing old build")
        cmd = subprocess.Popen(["make", "clean"])
    else:
        cmd = subprocess.Popen(["make", "html"])
    cmd.communicate()

    os.chdir(pwd)
