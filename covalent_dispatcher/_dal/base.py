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

"""Base classe for server-side analogues of workflow data types"""

from abc import ABC, abstractmethod
from contextlib import contextmanager
from typing import Any, Dict, Generator, List, Tuple, Union

from sqlalchemy import select
from sqlalchemy.orm import Session, load_only

from .._db.datastore import workflow_db
from . import controller
from .asset import Asset


class DispatchedObject(ABC):
    @classmethod
    @property
    def meta_type(cls) -> type(controller.Record):
        raise NotImplementedError

    @classmethod
    @property
    def asset_link_type(cls) -> type(controller.Record):
        raise NotImplementedError

    @classmethod
    @property
    def metadata_keys(cls) -> set:
        raise NotImplementedError

    @property
    @abstractmethod
    def query_keys(self) -> set:
        raise NotImplementedError

    @property
    @abstractmethod
    def metadata(self) -> controller.Record:
        raise NotImplementedError

    @property
    def computed_fields(self) -> Dict:
        return {}

    @classmethod
    @contextmanager
    def session(cls) -> Generator[Session, None, None]:
        with workflow_db.session() as session:
            yield session

    def get_asset_ids(self, session: Session, keys: List[str]) -> Dict[str, int]:
        membership_filters = {"key": keys} if len(keys) > 0 else {}
        records = type(self).asset_link_type.get(
            session,
            fields=[],
            equality_filters={"meta_id": self._id},
            membership_filters=membership_filters,
        )
        return {x.key: x.asset_id for x in records}

    def associate_asset(self, session: Session, key: str, asset_id: int):
        asset_link_kwargs = {
            "meta_id": self._id,
            "asset_id": asset_id,
            "key": key,
        }
        type(self).asset_link_type.insert(session, insert_kwargs=asset_link_kwargs, flush=False)

    @property
    @abstractmethod
    def assets(self) -> Dict[str, Asset]:
        raise NotImplementedError

    @classmethod
    def meta_record_map(cls, key: str) -> str:
        return key

    def _refresh_metadata(self, session: Session):
        fields = {type(self).meta_record_map(k) for k in self.query_keys}
        self.metadata.refresh(session, fields=fields)

    def get_metadata(self, key: str, session: Session, refresh: bool = True):
        attr = type(self).meta_record_map(key)
        if refresh:
            self._refresh_metadata(session)
        return self.metadata.attrs[attr]

    def set_metadata(self, key: str, val: Union[str, int], session: Session):
        record_attr = type(self).meta_record_map(key)
        self.metadata.update(session, values={record_attr: val})

    def incr_metadata(self, key: str, delta: int, session: Session):
        attr = type(self).meta_record_map(key)
        self.metadata.incr(session, increments={attr: delta})

    def get_asset(self, key: str) -> Asset:
        if key not in self.assets:
            with self.session() as session:
                asset_id = self.get_asset_ids(session, [key])[key]
                self.assets[key] = Asset.from_id(asset_id, session)

        return self.assets[key]

    def _get_value(self, key: str, session: Session, refresh: bool = True) -> Any:
        if key in self.computed_fields:
            handler = self.computed_fields[key]
            return handler(self, session)
        elif key in self.metadata_keys:
            return self.get_metadata(key, session, refresh)
        else:
            return self.get_asset(key).load_data()

    def get_value(self, key: str, session: Session = None, refresh: bool = True) -> Any:
        if session is not None:
            return self._get_value(key, session, refresh)
        else:
            with self.session() as session:
                return self._get_value(key, session, refresh)

    def _set_value(self, key: str, val: Any, session: Session) -> None:
        if key in type(self).metadata_keys:
            self.set_metadata(key, val, session)
        else:
            self.get_asset(key).store_data(val)

    def set_value(self, key: str, val: Any, session: Session = None) -> None:
        if session is not None:
            self._set_value(key, val, session)
        else:
            with self.session() as session:
                self._set_value(key, val, session)

    def get_values(self, keys: List[str], session: Session = None, refresh: bool = True) -> Dict:
        return {key: self.get_value(key, session, refresh) for key in keys}

    def set_values(self, keyvals: List[Tuple[str, Any]], session: Session = None):
        for item in keyvals:
            k, v = item
            self.set_value(k, v, session)

    @classmethod
    def get_db_records(
        cls, session: Session, *, keys: list, equality_filters: dict, membership_filters: dict
    ):
        # transform keys to db field names
        fields = list(map(cls.meta_record_map, keys))

        eq_filters_transformed = {}
        member_filters_transformed = {}
        for key, val in equality_filters.items():
            attr = cls.meta_record_map(key)
            eq_filters_transformed[attr] = val
        for key, vals in membership_filters.items():
            attr = cls.meta_record_map(key)
            member_filters_transformed[attr] = vals

        return cls.meta_type.get(
            session,
            fields=fields,
            equality_filters=eq_filters_transformed,
            membership_filters=member_filters_transformed,
        )

    @classmethod
    def get_linked_assets(
        cls, session, *, fields: list, equality_filters: dict, membership_filters: dict
    ) -> List[Asset]:
        link_model = cls.asset_link_type.model
        stmt = (
            select(link_model.meta_id, link_model.key, Asset.model)
            .join(link_model)
            .join(cls.meta_type.model)
        )

        for attr, val in equality_filters.items():
            stmt = stmt.where(getattr(cls.meta_type.model, attr) == val)
        for attr, vals in membership_filters.items():
            stmt = stmt.where(getattr(cls.meta_type.model, attr).in_(vals))
        if len(fields) > 0:
            stmt = stmt.options(load_only(*fields))

        records = session.execute(stmt)

        return [
            {"meta_id": row.meta_id, "key": row.key, "asset": Asset(session, row[2])}
            for row in records
        ]
