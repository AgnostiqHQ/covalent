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

"""Main Covalent public functionality."""

from importlib import metadata

from . import _file_transfer as fs  # nopycln: import
from . import executor, leptons  # nopycln: import
from ._dispatcher_plugins import local_dispatch as dispatch  # nopycln: import
from ._dispatcher_plugins import local_dispatch_sync as dispatch_sync  # nopycln: import
from ._dispatcher_plugins import local_redispatch as redispatch  # nopycln: import
from ._dispatcher_plugins import stop_triggers  # nopycln: import
from ._file_transfer import strategies as fs_strategies  # nopycln: import
from ._programmatic.commands import (  # nopycln: import
    covalent_start,
    covalent_stop,
    is_covalent_running,
)
from ._results_manager.results_manager import (  # nopycln: import
    cancel,
    get_result,
    get_result_manager,
)
from ._shared_files.config import get_config, reload_config, set_config  # nopycln: import
from ._shared_files.util_classes import RESULT_STATUS as status  # nopycln: import
from ._workflow import (  # nopycln: import
    DepsBash,
    DepsCall,
    DepsPip,
    Lepton,
    TransportableObject,
    electron,
    lattice,
)
from ._workflow.electron import wait  # nopycln: import
from ._workflow.qelectron import qelectron  # nopycln: import
from .executor.utils import get_context  # nopycln: import
from .quantum import QCluster  # nopycln: import

__all__ = [s for s in dir() if not s.startswith("_")]

for _s in dir():
    if not _s.startswith("_"):
        _obj = globals()[_s]
        _obj.__module__ = __name__

__version__ = metadata.version("covalent")
