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

"""Unit tests for the Dispatcher."""

import covalent as ct


def test_dispatch_workflow_on_stop():
    @ct.electron
    def new_func(a, b, c, d, e):
        return a + b + c + d + e

    @ct.electron
    @ct.lattice
    def work_func(a, b, c):
        return new_func(a, b, c, d=4, e=5)

    dispatch_id = ct.dispatch(work_func)(5, 6, 7)
    assert (
        dispatch_id
        == "Dispatcher object must be covalent workflow. Instead, a function was passed"
    )
