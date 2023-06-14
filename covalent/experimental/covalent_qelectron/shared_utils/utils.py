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

import cloudpickle
import orjson as json


def cloudpickle_serialize(obj):
    return cloudpickle.dumps(obj)


def cloudpickle_deserialize(obj):
    return cloudpickle.loads(obj)


def dummy_serialize(obj):
    try:
        return [o.json() for o in obj]
    except (AttributeError, TypeError):
        return obj


def dummy_deserialize(ser_obj):
    try:
        return [json.loads(ser_o) for ser_o in ser_obj]
    except (json.JSONDecodeError, TypeError):
        return ser_obj


def select_first_executor(qnode, executors):
    """Selects the first executor to run the qnode"""
    return executors[0]
