# Copyright 2023 Agnostiq Inc.
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


"""Helper functions for re-dispatching workflows."""

from typing import Callable, Dict, List, Optional

from .._results_manager.results_manager import get_result


def get_request_body(
    dispatch_id: str,
    new_args: Optional[List] = None,
    new_kwargs: Optional[Dict] = None,
    replace_electrons: Optional[Dict[str, Callable]] = None,
    reuse_previous_results: bool = False,
) -> Dict:
    """Get request body for re-dispatching a workflow."""
    if new_args is None:
        new_args = []
    if new_kwargs is None:
        new_kwargs = {}
    if replace_electrons is None:
        replace_electrons = {}
    if new_args or new_kwargs:
        res = get_result(dispatch_id)
        lat = res.lattice
        lat.build_graph(*new_args, **new_kwargs)
        json_lattice = lat.serialize_to_json()
    else:
        json_lattice = None
    updates = {k: v.electron_object.as_transportable_dict for k, v in replace_electrons.items()}

    return {
        "json_lattice": json_lattice,
        "dispatch_id": dispatch_id,
        "electron_updates": updates,
        "reuse_previous_results": reuse_previous_results,
    }
