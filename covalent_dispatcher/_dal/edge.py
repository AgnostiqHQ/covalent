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

"""DB-backed edge"""


from typing import Dict

from .._db import models
from .controller import Record
from .db_interfaces.edge_utils import _to_edge_attrs, _to_endpoints


class Edge:
    def __init__(self, record: models.ElectronDependency, uid_node_id_map: Dict):
        self.source, self.target = _to_endpoints(record, uid_node_id_map)
        self.attrs = _to_edge_attrs(record)


class ElectronDependency(Record[models.ElectronDependency]):
    model = models.ElectronDependency
