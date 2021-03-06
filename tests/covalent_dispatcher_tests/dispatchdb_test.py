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

"""Unit tests for the DispatchDB."""

import simplejson

import covalent as ct
from covalent._results_manager.result import Result
from covalent_dispatcher._db.dispatchdb import DispatchDB


@ct.electron
def add(a, b):
    return a + b


@ct.electron
def identity(a):
    return a


@ct.lattice
def check(a, b):
    result1 = add(a=a, b=b)
    return identity(a=result1)


def test_save_db(mocker):
    """Test the db save method."""

    with DispatchDB(":memory:") as db:
        res = Result(check, "/home/test/results", "asdf")
        persist_mock = mocker.patch("covalent._results_manager.result.Result.persist")
        db.save_db(result_object=res)
        persist_mock.assert_called_once()
