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
