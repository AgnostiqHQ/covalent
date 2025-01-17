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


from __future__ import annotations

from typing import Generic, List, Optional, Sequence, Type, TypeVar, Union

from sqlalchemy import select, update
from sqlalchemy.engine import Row
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import Select, desc

from .._db import models

T = TypeVar("T", bound=models.Base)


class Record(Generic[T]):
    """
    Thin wrapper for a SQLALchemy record
    """

    @classmethod
    @property
    def model(cls) -> Type[T]:
        raise NotImplementedError

    def __init__(self, session: Session, record: models.Base, *, fields: list):
        self._id = record.id
        self._attrs = {k: getattr(record, k) for k in fields}

    @property
    def primary_key(self):
        return self._id

    @classmethod
    def get(
        cls,
        session: Session,
        *,
        stmt: Optional[Select] = None,
        fields: list,
        equality_filters: dict,
        membership_filters: dict,
        for_update: bool = False,
        sort_fields: List[str] = [],
        reverse: bool = True,
        offset: int = 0,
        max_items: Optional[int] = None,
    ) -> Union[Sequence[Row], Sequence[T]]:
        """Bulk ORM-enabled SELECT.

        Args:
            session: SQLalchemy session
            fields: List of columns to select
            equality_filters: Dict{field_name: value}
            membership_filters: Dict{field_name: value_list}
            for_update: Whether to lock the selected rows

        Returns:
            A list of SQLAlchemy Rows or whole ORM entities depending
        on whether only a subset of fields is specified.

        """
        if stmt is None:
            if len(fields) > 0:
                entities = [getattr(cls.model, attr) for attr in fields]
                stmt = select(*entities)
            else:
                stmt = select(cls.model)

        for attr, val in equality_filters.items():
            stmt = stmt.where(getattr(cls.model, attr) == val)
        for attr, vals in membership_filters.items():
            stmt = stmt.where(getattr(cls.model, attr).in_(vals))
        if for_update:
            stmt = stmt.with_for_update()
        for attr in sort_fields:
            if reverse:
                stmt = stmt.order_by(desc(getattr(cls.model, attr)))
            else:
                stmt = stmt.order_by(getattr(cls.model, attr))

        stmt = stmt.offset(offset)
        if max_items:
            stmt = stmt.limit(max_items)

        if len(fields) == 0:
            # Return whole ORM entities
            return session.scalars(stmt).all()
        else:
            # Return a named tuple containing the selected cols
            return session.execute(stmt).all()

    @classmethod
    def get_by_primary_key(
        cls, session: Session, primary_key: int, *, for_update: bool = False
    ) -> T:
        return session.get(cls.model, primary_key, with_for_update=for_update)

    @classmethod
    def create(cls, session: Session, *, insert_kwargs: dict, flush: bool = True) -> T:
        """Create a new record.

        Args:
            session: SQLalchemy session
            insert_kwargs: kwargs to pass to the model constructor
            flush: Whether to flush the session immediately

        Returns: A SQLAlchemy model of type T. If `flush=False`, the
            model will need to be added to the session manually.

        """

        new_record = cls.model(**insert_kwargs)
        session.add(new_record)
        if flush:
            session.flush()
        return new_record

    @classmethod
    def update_bulk(
        cls, session: Session, *, values: dict, equality_filters: dict, membership_filters: dict
    ):
        """Bulk update.

        Args:
            session: SQLAlchemy session
            values: dictionary of values to pass to UPDATE
            equality_filters: Dict{field_name: value}
            membership_filters: Dict{field_name: value_list}
        """

        stmt = update(cls.model).values(**values)
        for attr, val in equality_filters.items():
            stmt = stmt.where(getattr(cls.model, attr) == val)
        for attr, vals in membership_filters.items():
            stmt = stmt.where(getattr(cls.model, attr).in_(vals))
        session.execute(stmt)

    @classmethod
    def incr_bulk(
        cls,
        session: Session,
        *,
        increments: dict,
        equality_filters: dict,
        membership_filters: dict,
    ):
        """Bulk increment numerical fields

        Args:
            session: SQLAlchemy session
            increment: dictionary {field: delta}
            equality_filters: Dict{field_name: value}
            membership_filters: Dict{field_name: value_list}
        """

        kwargs = {}
        for field, delta in increments.items():
            col = getattr(cls.model, field)
            kwargs[field] = col + delta

        stmt = update(cls.model).values(**kwargs)
        for attr, val in equality_filters.items():
            stmt = stmt.where(getattr(cls.model, attr) == val)
        for attr, vals in membership_filters.items():
            stmt = stmt.where(getattr(cls.model, attr).in_(vals))
        session.execute(stmt)

    def update(self, session: Session, *, values: dict):
        """Update the corresponding DB record."""

        type(self).update_bulk(
            session,
            values=values,
            equality_filters={"id": self.primary_key},
            membership_filters={},
        )
        for k, v in values.items():
            self._attrs[k] = v

    def incr(self, session: Session, *, increments: dict):
        """Increment the fields of the corresponding record."""
        type(self).incr_bulk(
            session,
            increments=increments,
            equality_filters={"id": self.primary_key},
            membership_filters={},
        )

    def refresh(self, session: Session, *, fields: set, for_update: bool = False):
        """Sync with DB"""
        records = type(self).get(
            session,
            fields=fields,
            equality_filters={"id": self._id},
            membership_filters={},
            for_update=for_update,
        )
        record = records[0]
        self._attrs = {k: getattr(record, k) for k in fields}

    @property
    def attrs(self) -> dict:
        return self._attrs

    def __contains__(self, item: str):
        return item in self._attrs
