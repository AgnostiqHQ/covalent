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

"""Utility functions for results manager."""

import requests

from .._shared_files.config import get_config


def convert_to_lattice_function_call(
    lattice_function_string: str, lattice_function_name: str, inputs: dict
) -> str:
    """
    Converts a lattice function string to a function call string inside
    `__name__` condition as well.

    Args:
        lattice_function_string: The lattice function string to convert.
        lattice_function_name: The name of the lattice function.
        inputs: The inputs to the lattice function.

    Returns:
        function_call_str: The converted lattice function string.
    """

    inp = ""

    if inputs["args"]:
        inp += "".join(f"{value}, " for value in inputs["args"])
    if inputs["kwargs"]:
        inp += "".join(f"{key}={value}, " for key, value in inputs["kwargs"].items())

    function_call_str = lattice_function_string
    function_call_str += f'if __name__ == "__main__":\n    {lattice_function_name}({inp})\n'
    return function_call_str


def _db_path(
    dispatcher: str = get_config("dispatcher.address") + ":" + str(get_config("dispatcher.port")),
) -> str:
    url = "http://" + dispatcher + "/api/db-path"
    r = requests.get(url)
    path = r.json()
    return path
