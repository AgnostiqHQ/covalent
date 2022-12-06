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

from ..._results_manager.results_manager import get_result
from ..._shared_files.context_managers import active_dispatch_info_manager
from ..._shared_files.util_classes import DispatchInfo
from ..._workflow.electron import Electron, get_serialized_function_str
from ..._workflow.transport import TransportableObject

"""Utils for generating electron deltas"""


def _get_new_metadata(meta_dict: dict):
    return {k: v for k, v in meta_dict.items() if v}


def to_electron_update(e: Electron):
    return {
        "name": e.function.__name__,
        "function": TransportableObject(e.function).to_dict(),
        "function_string": get_serialized_function_str(e.function),
        "metadata": _get_new_metadata(e.metadata),
    }


def _generate_electron_updates(dispatch_id, replace_electrons):
    with active_dispatch_info_manager.claim(DispatchInfo(dispatch_id)):
        electron_objects = {k: v() for k, v in replace_electrons.items()}

    return {k: to_electron_update(v) for k, v in electron_objects.items()}


def redispatch_real(
    dispatch_id: str,
    new_args=[],
    new_kwargs={},
    replace_electrons={},
    reuse_previous_results=False,
):
    if new_args or new_kwargs:
        res = get_result(dispatch_id)
        lat = res.lattice
        lat.build_graph(*new_args, **new_kwargs)
        json_lattice = lat.serialize_to_json()
    else:
        json_lattice = None
    updates = _generate_electron_updates(dispatch_id, replace_electrons)

    return {
        "json_lattice": json_lattice,
        "dispatch_id": dispatch_id,
        "electron_updates": updates,
        "reuse_previous_results": reuse_previous_results,
    }
