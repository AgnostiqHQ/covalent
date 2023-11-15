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

"""add qelectron_db_filename to electrons table

Revision ID: 692b18f7b7de
Revises: 1142d81b29b8
Create Date: 2023-11-14 01:53:30.701678

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
# pragma: allowlist nextline secret
revision = "692b18f7b7de"
# pragma: allowlist nextline secret
down_revision = "1142d81b29b8"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("electron_dependency", schema=None) as batch_op:
        batch_op.create_foreign_key("child_electron_link", "electrons", ["electron_id"], ["id"])

    # ### end Alembic commands ###

    with op.batch_alter_table("electrons", schema=None) as batch_op:
        batch_op.add_column(sa.Column("qelectron_db_filename", sa.Text(), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table("electrons", schema=None) as batch_op:
        batch_op.drop_column("qelectron_db_filename")

    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("electron_dependency", schema=None) as batch_op:
        batch_op.drop_constraint("child_electron_link", type_="foreignkey")

    # ### end Alembic commands ###