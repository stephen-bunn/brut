"""Create content table.

Revision ID: 9fff3a650708
Revises:
Create Date: 2021-04-07 11:54:33.225599
"""

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "9fff3a650708"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "content",
        sa.Column(
            "id",
            sa.BigInteger().with_variant(sa.Integer, "sqlite"),
            primary_key=True,
        ),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("source", sa.String(256)),
        sa.Column("source_id", sa.String(256)),
        sa.Column("fingerprint", sa.String(64), unique=True),
        sa.Column("url", sa.String(2048)),
        sa.Column("data", sa.Text),
        sa.Column("processed_at", sa.DateTime, nullable=True, default=None),
        sa.Column("processed_message", sa.Text, nullable=True, default=None),
    )


def downgrade():
    op.drop_table("content")
