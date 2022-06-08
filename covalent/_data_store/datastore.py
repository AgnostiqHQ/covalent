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

from contextlib import contextmanager
from typing import BinaryIO, Generator, List, Union

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from ..shared_files.config import get_config
from . import models
from .storage_backends import LocalStorageBackend, StorageBackend

default_backend_map = {"local": LocalStorageBackend(base_dir=get_config("workflow_data.base_dir"))}


class DataStore:
    def __init__(
        self,
        db_URL,
        storage_backend_map: dict[str, StorageBackend] = default_backend_map,
        initialize_db: bool = False,
        **kwargs,
    ):
        if db_URL:
            self.db_URL = db_URL
        else:
            self.db_URL = "sqlite+pysqlite://" + get_config("workflow_data.db_path")

        self.storage_backend_map = storage_backend_map

        self.engine = create_engine(self.db_URL, **kwargs)

        if initialize_db:
            models.Base.metadata.create_all(self.engine)

    @contextmanager
    def begin_session(self):
        with Session(self.engine) as session:
            session.begin()
            ds_session = DataStoreSession(session)
            try:
                yield ds_session

                session.commit()
                for arg in ds_session.pending_uploads:
                    self.upload_file(*arg)
                for arg in ds_session.pending_deletes:
                    self.delete_file(*arg)

            except Exception as ex:
                session.rollback()
                raise ex

            finally:
                pass

    def upload_file(self, data: BinaryIO, storage_type: str, storage_path: str, file_name: str):

        raise NotImplementedError

    def delete_file(self, storage_type: str, storage_path: str, file_name: str):

        raise NotImplementedError

    def download_file(self, storage_type: str, storage_path: str, file_name: str):

        raise NotImplementedError


class DataStoreSession:
    def __init__(self, session: Session):
        self.db_session = session
        self.pending_uploads = []
        self.pending_deletes = []

    def queue_upload(self, data: BinaryIO, storage_type: str, storage_path: str, file_name: str):
        self.pending_uploads.append((data, storage_type, storage_path, file_name))

    def queue_delete(self, storage_type: str, storage_path: str, file_name: str):
        self.pending_deletes.append((storage_type, storage_path, file_name))
