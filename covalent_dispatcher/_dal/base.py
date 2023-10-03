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

"""Base class for server-side analogues of workflow data types"""

from abc import abstractmethod
from typing import Any, Dict, Generator, Generic, List, Type, TypeVar, Union

from sqlalchemy import select
from sqlalchemy.orm import Session, load_only

from .._db.datastore import workflow_db
from . import controller
from .asset import FIELDS, Asset

# Metadata
MetaType = TypeVar("MetaType", bound=controller.Record)

# Asset links
AssetLinkType = TypeVar("AssetLinkType", bound=controller.Record)


class DispatchedObject(Generic[MetaType, AssetLinkType]):
    """Base class for types with both metadata and assets.

    Each subclass must define two properties:
    - `meta_type`: The controller class for the type's "pure metadata" table
    - `asset_link_type`: The controller class for the type's asset-links table

    """

    @classmethod
    @property
    def meta_type(cls) -> Type[MetaType]:
        """Returns the metadata controller class."""
        raise NotImplementedError

    @classmethod
    @property
    def asset_link_type(cls) -> Type[AssetLinkType]:
        """Returns the asset link controller class"""
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
    def metadata(self) -> MetaType:
        raise NotImplementedError

    @property
    def computed_fields(self) -> Dict:
        return {}

    @classmethod
    def session(cls) -> Generator[Session, None, None]:
        return workflow_db.session()

    def get_asset_ids(self, session: Session, keys: List[str]) -> Dict[str, int]:
        membership_filters = {"key": keys} if len(keys) > 0 else {}
        records = type(self).asset_link_type.get(
            session,
            fields=[],
            equality_filters={"meta_id": self._id},
            membership_filters=membership_filters,
        )
        return {x.key: x.asset_id for x in records}

    def associate_asset(
        self, session: Session, key: str, asset_id: int, flush: bool = False
    ) -> AssetLinkType:
        asset_link_kwargs = {
            "meta_id": self._id,
            "asset_id": asset_id,
            "key": key,
        }
        return type(self).asset_link_type.create(
            session, insert_kwargs=asset_link_kwargs, flush=flush
        )

    @property
    @abstractmethod
    def assets(self) -> Dict[str, Asset]:
        raise NotImplementedError

    @classmethod
    def meta_record_map(cls, key: str) -> str:
        return key

    def _refresh_metadata(self, session: Session, *, for_update: bool = False):
        fields = {type(self).meta_record_map(k) for k in self.query_keys}
        self.metadata.refresh(session, fields=fields, for_update=for_update)

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

    def get_asset(self, key: str, session: Session) -> Asset:
        if key not in self.assets:
            if session:
                asset_id = self.get_asset_ids(session, [key])[key]
                self.assets[key] = Asset.from_id(asset_id, session)
            else:
                with self.session() as session:
                    asset_id = self.get_asset_ids(session, [key])[key]
                    self.assets[key] = Asset.from_id(asset_id, session)

        return self.assets[key]

    def populate_asset_map(self, session: Session):
        """Load and cache all asset records"""
        asset_links = self.get_asset_ids(session=session, keys=[])
        for key, asset_id in asset_links.items():
            self.assets[key] = Asset.from_id(asset_id, session)

    def update_assets(self, updates: Dict[str, Dict], session: Session = None):
        """Bulk update associated assets"""
        if session:
            for key, values in updates.items():
                asset = self.get_asset(key, session)
                asset.update(session, values=values)
        else:
            with self.session() as session:
                for key, values in updates.items():
                    asset = self.get_asset(key, session)
                    asset.update(session, values=values)

    def _get_value(self, key: str, session: Session, refresh: bool = True) -> Any:
        if key in self.computed_fields:
            handler = self.computed_fields[key]
            return handler(self, session)
        elif key in self.metadata_keys:
            return self.get_metadata(key, session, refresh)
        else:
            return self.get_asset(key, session).load_data()

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
            self.get_asset(key, session).store_data(val)

    def set_value(self, key: str, val: Any, session: Session = None) -> None:
        if session is not None:
            self._set_value(key, val, session)
        else:
            with self.session() as session:
                self._set_value(key, val, session)

    def get_values(self, keys: List[str], session: Session = None, refresh: bool = True) -> Dict:
        return {key: self.get_value(key, session, refresh) for key in keys}

    @classmethod
    def get_db_records(
        cls,
        session: Session,
        *,
        keys: list,
        equality_filters: dict,
        membership_filters: dict,
        for_update: bool = False,
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
            for_update=for_update,
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
        if len(fields) == 0:
            fields = FIELDS
        for attr, val in equality_filters.items():
            stmt = stmt.where(getattr(cls.meta_type.model, attr) == val)
        for attr, vals in membership_filters.items():
            stmt = stmt.where(getattr(cls.meta_type.model, attr).in_(vals))

        attrs = [getattr(Asset.model, f) for f in fields]
        stmt = stmt.options(load_only(*attrs))

        records = session.execute(stmt)

        return [
            {"meta_id": row.meta_id, "key": row.key, "asset": Asset(session, row[2], keys=fields)}
            for row in records
        ]
