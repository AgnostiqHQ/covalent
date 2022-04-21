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

"""Main Covalent public functionality."""


import contextlib
import os

from . import executor
from ._shared_files.config import get_config, set_config
from ._shared_files.interface import cancel_workflow, dispatch, dispatch_sync, get_result, sync
from ._shared_files.util_classes import RESULT_STATUS as status
from ._workflow import Lepton
from ._workflow import electron_func as electron
from ._workflow import lattice_func as lattice

try:
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../VERSION")) as f:
        __version__ = f.read().strip()
except FileNotFoundError:
    pass

__all__ = [s for s in dir() if not s.startswith("_")]

for _s in dir():
    if not _s.startswith("_"):
        _obj = globals()[_s]
        _obj.__module__ = __name__
