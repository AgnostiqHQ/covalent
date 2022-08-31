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

import glob
import os
import shutil
import tempfile
from subprocess import Popen

import pytest

import covalent as ct

rootdir = os.path.dirname(ct.__file__)
tutorial_dir = "/../doc/source/tutorials/**/"
suffix = "*.ipynb"
notebooks = glob.glob(rootdir + tutorial_dir + suffix, recursive=True)
tutorial_requirements = glob.glob(rootdir + tutorial_dir + "requirements.txt", recursive=True)
expected_return_values = [0] * len(notebooks)


@pytest.mark.skipif(
    os.environ.get("RUN_TUTORIALS") != "TRUE",
    reason="Required RUN_TUTORIALS env variable to be set to TRUE",
)
@pytest.mark.parametrize(
    "file, requirements, expected_return_value",
    zip(notebooks, tutorial_requirements, expected_return_values),
)
def test_tutorial(file, requirements, expected_return_value):
    # Create venv for tutorial
    venv_location = tempfile.mkdtemp()
    create_venv = Popen(f"python -m venv {venv_location}", shell=True)
    create_venv.communicate()
    assert create_venv.returncode == expected_return_value

    # Intall tutorial requirements into venv
    python_executable = os.path.join(venv_location, "bin/python")
    install_deps = Popen(f"{python_executable} -m pip install -r {requirements}", shell=True)
    install_deps.communicate()
    assert install_deps.returncode == expected_return_value

    install_jupyter = Popen(f"{python_executable} -m pip install jupyter", shell=True)
    install_jupyter.communicate()
    assert install_jupyter.returncode == expected_return_value

    # Run tutorial notebook
    jupyter = os.path.join(venv_location, "bin/jupyter")
    proc = Popen(
        f"{jupyter} nbconvert {file} --to script --stdout | {python_executable}", shell=True
    )
    proc.communicate()
    assert proc.returncode == expected_return_value

    # Cleanup virtualenv
    shutil.rmtree(venv_location)
