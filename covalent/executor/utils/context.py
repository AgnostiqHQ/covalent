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

from contextlib import contextmanager

from pydantic import BaseModel


class Context(BaseModel):
    node_id: int = None
    dispatch_id: str = None


def get_context():
    return current_context


@contextmanager
def set_context(node_id: int, dispatch_id: str):
    global current_context
    global unset_context
    current_context = Context(node_id=node_id, dispatch_id=dispatch_id)
    yield
    current_context = unset_context


unset_context = Context()
current_context = unset_context
