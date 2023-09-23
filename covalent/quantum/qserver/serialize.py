# Copyright 2023 Agnostiq Inc.
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
Implement several different serialization methods for QNode output data written
to the database.
"""
import warnings
import zlib
from abc import ABC, abstractmethod
from enum import Enum
from typing import Sequence, Union

import cloudpickle as pickle
import lmdb
import orjson
from lmdbm.lmdbm import Lmdb, remove_lmdbm


class _Serializer(ABC):
    """
    base class for serializer strategies
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """
        strategy name
        """

    @abstractmethod
    def pre_value(self, value):
        """
        returns processed value to be written to db
        """
        raise NotImplementedError()

    @abstractmethod
    def post_value(self, value):
        """
        post-process value read from db and return
        """
        raise NotImplementedError()


class _OrjsonStrategy(_Serializer):
    """
    uses `orjson` and `zlib` to serialize/deserialize
    """

    name = "orjson"

    def pre_value(self, value):
        return zlib.compress(orjson.dumps(value, option=orjson.OPT_SERIALIZE_NUMPY))

    def post_value(self, value):
        return orjson.loads(zlib.decompress(value))


class _PickleStrategy(_Serializer):
    """
    uses `cloudpickle` and `zlib` to serialize/deserialize
    """

    name = "pickle"

    def pre_value(self, value):
        return zlib.compress(pickle.dumps(value))

    def post_value(self, value):
        return pickle.loads(zlib.decompress(value))


class _FallbackStrategy(_Serializer):
    """
    tries multiple strategies until success
    """

    name = "fallback"

    def __init__(self, strategies):
        self.strategies = strategies

    def pre_value(self, value):
        for strategy in self.strategies:
            try:
                return strategy.pre_value(value)
            except TypeError as te:
                warnings.warn(
                    f"serialization strategy '{strategy.name}' failed on `pre_value`; "
                    f"value: {value}; error: {te}."
                )
        raise RuntimeError("all strategies failed to encode data")

    def post_value(self, value):
        for strategy in self.strategies:
            try:
                return strategy.post_value(value)
            except TypeError as te:
                warnings.warn(
                    f"serialization strategy '{strategy.name}' failed on `post_value`; "
                    f"value: {value}; error: {te}."
                )
        raise RuntimeError("all strategies failed to decode data")


class Strategy(Enum):
    """
    available serialization strategies
    """

    ORJSON = _OrjsonStrategy
    PICKLE = _PickleStrategy
    FALLBACK = _FallbackStrategy


class JsonLmdb(Lmdb):
    """
    custom `Lmdb` implementation with pre- and post-value strategy option
    """

    def __init__(self, strategy_type: Union[Strategy, Sequence[Strategy]], **kw):
        self._strategy_map = {}
        self.strategy = self.init_strategy(strategy_type)
        super().__init__(**kw)

    def _pre_key(self, key):
        return key.encode("utf-8")

    def _post_key(self, key):
        return key.decode("utf-8")

    def _pre_value(self, value):
        return self.strategy.pre_value(value)

    def _post_value(self, value):
        return self.strategy.post_value(value)

    @property
    def strategy_map(self):
        """
        allows access to strategies by str name
        """
        if not self._strategy_map:
            self._strategy_map = {s.value.name: s.value for s in list(Strategy)}
        return self._strategy_map

    def init_strategy(self, strategy_type) -> _Serializer:
        """
        initialize an instance of the named strategy
        """
        if isinstance(strategy_type, Strategy):
            return self._init_single_strategy(strategy_type)

        # strategy with fallback
        strategies = [self._init_single_strategy(typ) for typ in strategy_type]
        return _FallbackStrategy(strategies)

    def _init_single_strategy(self, strategy_type) -> _Serializer:
        if not isinstance(strategy_type, Strategy):
            raise TypeError(f"expected Strategy, not {type(strategy_type.__class__.__name__)}")

        strategy_cls = self.strategy_map.get(strategy_type.value.name)
        if strategy_cls is None:
            raise ValueError(f"unknown database strategy '{strategy_type}'")
        return strategy_cls()

    @classmethod
    def open_with_strategy(
        cls,
        file,
        flag="r",
        mode=0o755,
        map_size=2**20,
        *,
        strategy_name,
        autogrow=True,
    ):
        """
        Custom open classmethod that takes a (new) strategy argument. Mostly
        replicates original `Lmdb.open`, except passing `strategy_name` to initializer.

        Opens the database `file`.
        `flag`: r (read only, existing), w (read and write, existing),
                c (read, write, create if not exists), n (read, write, overwrite existing)
        `map_size`: Initial database size. Defaults to 2**20 (1MB).
        `autogrow`: Automatically grow the database size when `map_size` is exceeded.
                WARNING: Set this to `False` for multi-process write access.
        `strategy_name`: either 'orjson' or 'pickle'
        """

        if flag == "r":  # Open existing database for reading only (default)
            env = lmdb.open(
                file, map_size=map_size, max_dbs=1, readonly=True, create=False, mode=mode
            )
        elif flag == "w":  # Open existing database for reading and writing
            env = lmdb.open(
                file, map_size=map_size, max_dbs=1, readonly=False, create=False, mode=mode
            )
        elif flag == "c":  # Open database for reading and writing, creating it if it doesn't exist
            env = lmdb.open(
                file, map_size=map_size, max_dbs=1, readonly=False, create=True, mode=mode
            )
        elif flag == "n":  # Always create a new, empty database, open for reading and writing
            remove_lmdbm(file)
            env = lmdb.open(
                file, map_size=map_size, max_dbs=1, readonly=False, create=True, mode=mode
            )
        else:
            raise ValueError("Invalid flag")

        return cls(strategy_name, env=env, autogrow=autogrow)
