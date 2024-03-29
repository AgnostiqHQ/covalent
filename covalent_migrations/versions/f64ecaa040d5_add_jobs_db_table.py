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

"""Add jobs db table

Revision ID: f64ecaa040d5
Revises: 97202f5f47cb
Create Date: 2023-02-07 14:52:43.475708

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
# pragma: allowlist nextline secret
revision = "f64ecaa040d5"
# pragma: allowlist nextline secret
down_revision = "97202f5f47cb"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "jobs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("cancel_requested", sa.Boolean(), nullable=False),
        sa.Column("cancel_successful", sa.Boolean(), nullable=False),
        sa.Column("job_handle", sa.Text(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    with op.batch_alter_table("electron_dependency", schema=None) as batch_op:
        batch_op.create_foreign_key("electron_link", "electrons", ["parent_electron_id"], ["id"])

    with op.batch_alter_table("electrons", schema=None) as batch_op:
        batch_op.add_column(sa.Column("job_id", sa.Integer(), nullable=False))
        batch_op.create_foreign_key("job_id_link", "jobs", ["job_id"], ["id"])

    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("electrons", schema=None) as batch_op:
        batch_op.drop_constraint("job_id_link", type_="foreignkey")
        batch_op.drop_column("job_id")

    with op.batch_alter_table("electron_dependency", schema=None) as batch_op:
        batch_op.drop_constraint("electron_link", type_="foreignkey")

    op.drop_table("jobs")
    # ### end Alembic commands ###
