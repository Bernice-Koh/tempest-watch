"""add cards and card_price_snapshots tables

Revision ID: a1b2c3d4e5f6
Revises:
Create Date: 2026-05-27 00:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "a1b2c3d4e5f6"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "cards",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("set_id", sa.String(), nullable=False),
        sa.Column("set_number", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("supertype", sa.String(), nullable=False),
        sa.Column(
            "subtypes",
            postgresql.ARRAY(sa.String()),
            nullable=False,
            server_default="{}",
        ),
        sa.Column("rarity", sa.String(), nullable=True),
        sa.Column("image_small", sa.String(), nullable=True),
        sa.Column("image_large", sa.String(), nullable=True),
        sa.Column("raw", postgresql.JSONB(), nullable=False),
        sa.Column(
            "first_seen_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "last_updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )
    op.create_index("ix_cards_set_id", "cards", ["set_id"])
    op.create_index("ix_cards_name", "cards", ["name"])

    op.create_table(
        "card_price_snapshots",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column(
            "card_id",
            sa.String(),
            sa.ForeignKey("cards.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("source", sa.String(), nullable=False),
        sa.Column("variant", sa.String(), nullable=True),
        sa.Column("price_type", sa.String(), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column("value", sa.Numeric(12, 2), nullable=False),
        sa.Column("observed_date", sa.Date(), nullable=False),
        sa.Column(
            "observed_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column("raw", postgresql.JSONB(), nullable=False),
        sa.UniqueConstraint(
            "card_id",
            "source",
            "variant",
            "price_type",
            "observed_date",
            name="uq_snapshot_card_source_variant_type_date",
            postgresql_nulls_not_distinct=True,
        ),
    )
    op.create_index(
        "ix_snapshot_card_date_desc",
        "card_price_snapshots",
        ["card_id", sa.text("observed_date DESC")],
    )


def downgrade() -> None:
    op.drop_index("ix_snapshot_card_date_desc", table_name="card_price_snapshots")
    op.drop_table("card_price_snapshots")
    op.drop_index("ix_cards_name", table_name="cards")
    op.drop_index("ix_cards_set_id", table_name="cards")
    op.drop_table("cards")
