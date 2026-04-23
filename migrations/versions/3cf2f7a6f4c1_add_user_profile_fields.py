"""add user profile fields

Revision ID: 3cf2f7a6f4c1
Revises: 68be12bcfdd0
Create Date: 2026-04-23 15:20:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "3cf2f7a6f4c1"
down_revision = "68be12bcfdd0"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("users", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column("password_hash", sa.String(length=255), nullable=True)
        )
        batch_op.add_column(
            sa.Column(
                "image",
                sa.String(length=255),
                nullable=True,
                server_default="profile_default.jpg",
            )
        )
        batch_op.add_column(
            sa.Column("about_me", sa.Text(), nullable=True, server_default="")
        )
        batch_op.add_column(sa.Column("last_seen", sa.DateTime(), nullable=True))

    op.execute("UPDATE users SET password_hash = password")

    with op.batch_alter_table("users", schema=None) as batch_op:
        batch_op.drop_column("password")


def downgrade():
    with op.batch_alter_table("users", schema=None) as batch_op:
        batch_op.add_column(sa.Column("password", sa.String(length=255), nullable=True))

    op.execute("UPDATE users SET password = password_hash")

    with op.batch_alter_table("users", schema=None) as batch_op:
        batch_op.drop_column("last_seen")
        batch_op.drop_column("about_me")
        batch_op.drop_column("image")
        batch_op.drop_column("password_hash")
