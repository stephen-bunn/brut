"""Create artifact table.

Revision ID: 513518a9decd
Revises: 9fff3a650708
Create Date: 2021-04-07 15:19:10.170850
"""

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "513518a9decd"
down_revision = "9fff3a650708"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "artifact",
        sa.Column(
            "id",
            sa.BigInteger().with_variant(sa.Integer, "sqlite"),
            primary_key=True,
        ),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("fingerprint", sa.String(64), unique=True),
        sa.Column("content_id", sa.BigInteger, sa.ForeignKey("content.id")),
    )


def downgrade():
    op.drop_table("artifact")
