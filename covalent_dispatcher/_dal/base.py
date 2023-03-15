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
from typing import Any, Dict, List, Tuple, Union

from sqlalchemy.orm import Session

from .._db.datastore import workflow_db
from .asset import Asset


class DispatchedObject(ABC):
    @property
    @abstractmethod
    def pure_metadata(self) -> Dict:
        raise NotImplementedError

    @property
    @pure_metadata.setter
    @abstractmethod
    def pure_metadata(self, meta: Dict):
        raise NotImplementedError

    @property
    @abstractmethod
    def db_metadata(self) -> Dict:
        raise NotImplementedError

    @property
    @db_metadata.setter
    @abstractmethod
    def db_metadata(self, meta: Dict):
        raise NotImplementedError

    @property
    def computed_fields(self) -> Dict:
        return {}

    @abstractmethod
    def get_asset_ids(self, session: Session, keys: List[str]) -> Dict[str, int]:
        raise NotImplementedError

    @property
    @abstractmethod
    def assets(self) -> Dict:
        raise NotImplementedError

    @abstractmethod
    def _get_db_record(self, session: Session):
        raise NotImplementedError

    @abstractmethod
    def _to_pure_meta(self, session: Session, record):
        raise NotImplementedError

    @abstractmethod
    def _to_db_meta(self, session: Session, record):
        raise NotImplementedError

    @abstractmethod
    def meta_record_map(self, key: str) -> str:
        raise NotImplementedError

    def _refresh_metadata(self, session: Session):
        record = self._get_db_record(session)
        self.pure_metadata = self._to_pure_meta(session, record)
        self.db_metadata = self._to_db_meta(session, record)

    def get_pure_metadata(self, key: str, session: Session = None, refresh: bool = True):
        if refresh:
            if session:
                self._refresh_metadata(session)
            else:
                with workflow_db.session() as session:
                    self._refresh_metadata(session)
        return self.pure_metadata[key]

    def set_pure_metadata(self, key: str, val: Union[str, int], session: Session = None):
        if session:
            record = self._get_db_record(session)
            record_attr = self.meta_record_map(key)
            setattr(record, record_attr, val)
        else:
            with workflow_db.session() as session:
                record = self._get_db_record(session)
                record_attr = self.meta_record_map(key)
                setattr(record, record_attr, val)

    def get_db_metadata(self, key: str, session: Session = None, refresh: bool = True):
        if refresh:
            if session:
                self._refresh_metadata(session)
            else:
                with workflow_db.session() as session:
                    self._refresh_metadata(session)
        return self.db_metadata[key]

    def set_db_metadata(self, key: str, val: Union[str, int], session: Session = None):
        self.set_pure_metadata(key, val, session)

    def get_asset(self, key: str) -> Asset:
        if key not in self.assets:
            with workflow_db.session() as session:
                asset_id = self.get_asset_ids(session, [key])[key]
                self.assets[key] = Asset.from_asset_id(asset_id, session)

        return self.assets[key]

    def _get_value(self, key: str, session: Session, refresh: bool = True) -> Any:
        if key in self.pure_metadata:
            return self.get_pure_metadata(key, session, refresh)
        elif key in self.db_metadata:
            return self.get_db_metadata(key, session, refresh)
        elif key in self.computed_fields:
            handler = self.computed_fields[key]
            return handler(self, session)
        else:
            return self.get_asset(key).load_data()

    def get_value(self, key: str, session: Session = None, refresh: bool = True) -> Any:
        if session is not None:
            return self._get_value(key, session, refresh)
        else:
            with workflow_db.session() as session:
                return self._get_value(key, session, refresh)

    def _set_value(self, key: str, val: Any, session: Session) -> None:
        if key in self.pure_metadata:
            self.set_pure_metadata(key, val, session)
        elif key in self.db_metadata:
            self.set_db_metadata(key, val, session)
        else:
            self.get_asset(key).store_data(val)

    def set_value(self, key: str, val: Any, session: Session = None) -> None:
        if session is not None:
            self._set_value(key, val, session)
        else:
            with workflow_db.session() as session:
                self._set_value(key, val, session)

    def get_values(self, keys: List[str], session: Session = None, refresh: bool = True) -> Dict:
        return {key: self.get_value(key, session, refresh) for key in keys}

    def set_values(self, keyvals: List[Tuple[str, Any]], session: Session = None):
        for item in keyvals:
            k, v = item
            self.set_value(k, v, session)
