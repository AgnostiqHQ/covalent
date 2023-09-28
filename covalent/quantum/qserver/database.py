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

from pathlib import Path

from ..._shared_files.config import get_config
from .serialize import JsonLmdb, Strategy
from .utils import CircuitInfo


def set_serialization_strategy(strategy_name):
    """
    Select a serialization strategy for the database
    """
    Database.serialization_strategy = strategy_name


class Database:
    # dash-separated names result in fallback strategy with try/except loops,
    # other valid strategy names uses the one strategy every time
    # see `covalent_qelectron/quantum_server/serialize.py`
    serialization_strategy = (Strategy.PICKLE, Strategy.ORJSON)

    @property
    def strategy_name(self):
        # using a property here for dynamic access
        # allows runtime strategy selection with `set_serialization_strategy()`
        return Database.serialization_strategy

    def __init__(self, db_dir=None):
        if db_dir:
            self.db_dir = Path(db_dir)
        else:
            self.db_dir = Path(get_config("dispatcher")["qelectron_db_path"])

    def _get_db_path(self, dispatch_id, node_id, *, mkdir=False):
        dispatch_id = "default-dispatch" if dispatch_id is None else dispatch_id
        node_id = "default-node" if node_id is None else node_id
        db_path = self.db_dir.joinpath(dispatch_id, f"node-{node_id}")
        if mkdir:
            db_path.mkdir(parents=True, exist_ok=True)

        return db_path.resolve().absolute()

    def _open(self, dispatch_id, node_id, mkdir=False):
        db_path = self._get_db_path(dispatch_id, node_id, mkdir=mkdir)

        if not db_path.exists():
            raise FileNotFoundError(f"Missing database directory {db_path}.")

        return JsonLmdb.open_with_strategy(
            file=str(db_path), flag="c", strategy_name=self.strategy_name
        )

    def set(self, keys, values, *, dispatch_id, node_id):
        with self._open(dispatch_id, node_id, mkdir=True) as db:
            for i, circuit_id in enumerate(keys):
                stored_val: dict = db.get(circuit_id, None)
                if stored_val is None:
                    continue

                stored_val.update(values[i])
                values[i] = stored_val

            db.update(dict(zip(keys, values)))

    def get_circuit_ids(self, *, dispatch_id, node_id):
        with self._open(dispatch_id, node_id) as db:
            return list(db.keys())

    def get_circuit_info(self, circuit_id, *, dispatch_id, node_id):
        with self._open(dispatch_id, node_id) as db:
            return CircuitInfo(**db.get(circuit_id, None))

    def get_db(self, *, dispatch_id, node_id):
        db_copy = {}
        with self._open(dispatch_id, node_id) as db:
            for key, value in db.items():
                db_copy[key] = value

        return db_copy
