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

"""
Unit tests for DataStore object
"""

from covalent._shared_files.config import get_config
from covalent_dispatcher._db.datastore import DataStore


def test_datastore_init():
    """Test data store initialization method."""

    ds = DataStore(db_URL=None)
    assert ds.db_URL == "sqlite+pysqlite:///" + get_config("dispatcher.db_path")
