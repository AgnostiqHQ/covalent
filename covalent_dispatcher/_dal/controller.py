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


from sqlalchemy import select
from sqlalchemy.orm import Session, load_only


def get(
    model, session: Session, *, fields: list, equality_filters: dict, membership_filters: dict
):
    stmt = select(model)
    for attr, val in equality_filters.items():
        stmt = stmt.where(getattr(model, attr) == val)
    for attr, vals in membership_filters.items():
        stmt = stmt.where(getattr(model, attr).in_(vals))
    if len(fields) > 0:
        stmt = stmt.options(load_only(*fields))
    return session.scalars(stmt).all()
