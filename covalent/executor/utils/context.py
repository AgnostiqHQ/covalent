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
