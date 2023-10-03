# Copyright 2023 Agnostiq Inc.
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
