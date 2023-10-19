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
import sys


def install_autoclass_doc_dependencies() -> None:
    """Install the packages required to build the documentation from plugin
    autoclass."""

    try:
        # Install covalent from branch source which includes this branch's changes to docs.
        subprocess.check_call([sys.executable, "-m", "pip", "install", "../"])
        subprocess.check_call(
            [
                sys.executable,
                "-m",
                "pip",
                "install",
                "-r",
                "autodoc_executor_plugins_requirements.txt",
            ]
        )
    except subprocess.CalledProcessError as e:
        print(f"Error handling dependency with error: {e}")
        sys.exit(1)


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
        install_autoclass_doc_dependencies()
        cmd = subprocess.Popen(["make", "html"])
    _, stderr = cmd.communicate()

    if cmd.returncode != 0:
        print(f"Error running 'make': {stderr}")

    os.chdir(pwd)
