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

"""Mappings between electron attributes and DB records"""


from ..._db import models


def _to_endpoints(e_record: models.ElectronDependency, uid_node_id_map: dict):
    source = uid_node_id_map[e_record.parent_electron_id]
    target = uid_node_id_map[e_record.electron_id]
    return source, target


def _to_edge_attrs(e_record: models.ElectronDependency):
    attrs = {
        "edge_name": e_record.edge_name,
        "param_type": e_record.parameter_type,
        "arg_index": e_record.arg_index,
    }

    return attrs
