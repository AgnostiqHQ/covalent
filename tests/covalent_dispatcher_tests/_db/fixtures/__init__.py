#!/usr/bin/env python

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

import datetime

import pytest

from covalent_dispatcher._db import models


@pytest.fixture
def workflow_fixture():
    """A collection of DB models to be re-used in unit tests for DB"""

    electron_dependency = models.ElectronDependency(
        electron_id=2, parent_electron_id=1, edge_name="arg_1", created_at=datetime.datetime.now()
    )

    return {"electron_dependency": [electron_dependency]}
