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

"""Utility functions for results manager."""


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
