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


from __future__ import annotations

from sqlalchemy import select, update
from sqlalchemy.orm import Session, load_only

from .._db import models


class Record:
    @classmethod
    @property
    def model(cls) -> type(models.Base):
        raise NotImplementedError

    def __init__(self, session: Session, record: models.Base, *, fields: set):
        self._id = record.id
        self._attrs = {k: getattr(record, k) for k in fields}

    @property
    def primary_key(self):
        return self._id

    @classmethod
    def get(
        cls, session: Session, *, fields: list, equality_filters: dict, membership_filters: dict
    ):
        stmt = select(cls.model)
        for attr, val in equality_filters.items():
            stmt = stmt.where(getattr(cls.model, attr) == val)
        for attr, vals in membership_filters.items():
            stmt = stmt.where(getattr(cls.model, attr).in_(vals))
        if len(fields) > 0:
            stmt = stmt.options(load_only(*fields))
        return session.scalars(stmt).all()

    @classmethod
    def insert(cls, session: Session, *, insert_kwargs: dict, flush: bool = True) -> models.Base:
        new_record = cls.model(**insert_kwargs)
        session.add(new_record)
        if flush:
            session.flush()
        return new_record

    def update(self, session: Session, *, values: dict):
        cls = type(self)
        stmt = update(cls.model).where(cls.model.id == self.primary_key).values(**values)
        session.execute(stmt)

    def refresh(self, session: Session, *, fields: set):
        records = type(self).get(
            session,
            fields=fields,
            equality_filters={"id": self._id},
            membership_filters={},
        )
        record = records[0]
        self._attrs = {k: getattr(record, k) for k in fields}

    @property
    def attrs(self) -> dict:
        return self._attrs

    def __contains__(self, item: str):
        return item in self._attrs
