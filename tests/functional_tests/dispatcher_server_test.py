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

import covalent as ct
import covalent._results_manager.results_manager as rm
from covalent_dispatcher._db.dispatchdb import DispatchDB


@ct.electron
def identity(x):
    return x


@ct.electron
def add(x, y):
    import random
    import time

    time.sleep(random.choice([1, 2]))
    return x + y


@ct.lattice
def pipeline(a, b):
    res_1 = add(x=a, y=b)
    return identity(x=res_1)


def test_dispatcher_server():
    # After the dispatcher server has been started, you can run the following
    dispatch_id = ct.dispatch(pipeline)(a=2, b=1)
    assert dispatch_id is not None

    # Wait for it to complete
    result = ct.get_result(dispatch_id, wait=True)
    assert result is not None

    assert result.start_time is not None
    assert result.end_time is not None
    assert result.end_time > result.start_time
    assert result.status == str(ct.status.COMPLETED)
    assert result.result == 3

    rm._delete_result(dispatch_id)
