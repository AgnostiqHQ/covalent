#!/usr/bin/env python

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
