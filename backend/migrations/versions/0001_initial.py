"""initial schema: vet, owner, dog, reading

Hand-authored (no database was available to autogenerate against). It mirrors the
SQLModel tables in app/models/ exactly, so a later ``alembic revision
--autogenerate`` against a migrated database should produce no diff.

Revision ID: 0001_initial
Revises:
Create Date: 2026-08-11
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "vet",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("hashed_password", sa.String(), nullable=False),
        sa.Column("full_name", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_vet_email", "vet", ["email"], unique=True)

    op.create_table(
        "owner",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("hashed_password", sa.String(), nullable=True),
        sa.Column("full_name", sa.String(), nullable=True),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("supervising_vet_id", sa.Integer(), nullable=False),
        sa.Column("invited_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("accepted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["supervising_vet_id"], ["vet.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_owner_email", "owner", ["email"], unique=True)
    op.create_index("ix_owner_status", "owner", ["status"], unique=False)
    op.create_index("ix_owner_supervising_vet_id", "owner", ["supervising_vet_id"], unique=False)

    op.create_table(
        "dog",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("breed", sa.String(), nullable=False),
        sa.Column("age", sa.Integer(), nullable=False),
        sa.Column("owner_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["owner_id"], ["owner.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_dog_owner_id", "dog", ["owner_id"], unique=False)

    op.create_table(
        "reading",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("dog_id", sa.Integer(), nullable=False),
        sa.Column("bpm", sa.Integer(), nullable=False),
        sa.Column("recommendation", sa.String(), nullable=False),
        sa.Column("recorded_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["dog_id"], ["dog.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_reading_dog_id", "reading", ["dog_id"], unique=False)
    op.create_index("ix_reading_recorded_at", "reading", ["recorded_at"], unique=False)


def downgrade() -> None:
    op.drop_table("reading")
    op.drop_table("dog")
    op.drop_table("owner")
    op.drop_table("vet")
