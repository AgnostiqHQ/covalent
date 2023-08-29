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

"""QA script to test the call deps return value functionality."""


import covalent as ct


def test_call_deps_retval():
    """Test the call deps return value functionality."""

    def greeting_one():
        return "hello"

    def greeting_two():
        return "howdy"

    def greeting_three():
        return "hey"

    @ct.electron(
        call_before=[
            ct.DepsCall(greeting_one, retval_keyword="greetings"),
            ct.DepsCall(greeting_two, retval_keyword="greetings"),
        ]
    )
    def get_all_greetings(greetings=[]):
        return greetings

    @ct.electron(
        call_before=[
            ct.DepsCall(greeting_three, retval_keyword="greeting"),
        ]
    )
    def get_one_greeting(greeting=None):
        return f"{greeting}, whats up?"

    @ct.lattice
    def workflow():
        greetings = get_all_greetings()
        greeting = get_one_greeting()
        return [greeting] + greetings

    # Dispatch the workflow
    dispatch_id = ct.dispatch(workflow)()
    res = ct.get_result(dispatch_id, wait=True)
    assert res.result == ["hey, whats up?", "hello", "howdy"]
    assert res.status == "COMPLETED"
