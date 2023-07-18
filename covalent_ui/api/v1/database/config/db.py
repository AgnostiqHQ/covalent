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

"""DB Config"""

from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from covalent_dispatcher._db.datastore import DataStore


# Base = declarative_base()
class Base(AsyncAttrs, DeclarativeBase):
    pass


engine = DataStore.factory().engine
async_session = async_sessionmaker(DataStore.factory().async_engine, expire_on_commit=False)


def init_db(db_path: str = None):
    global engine
    global async_session
    engine = (
        DataStore(db_URL=db_path, initialize_db=True).engine
        if db_path is not None
        else DataStore().engine
    )
    async_session = (
        async_sessionmaker(
            DataStore(db_URL=db_path, initialize_db=True).async_engine, expire_on_commit=False
        )
        if db_path
        else async_sessionmaker(DataStore().async_engine, expire_on_commit=False)
    )
