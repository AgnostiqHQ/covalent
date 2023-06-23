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

import os
import subprocess
import sys


def install_autoclass_doc_dependencies() -> None:
    """Install the packages required to build the documentation from plugin
    autoclass."""

    try:
        # Install covalent from branch source which includes this branch's changes to docs.
        subprocess.check_call([sys.executable, "-m", "pip", "install", "../"])
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r",
                              "autodoc_executor_plugins_requirements.txt"])
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
    cmd.communicate()

    os.chdir(pwd)
