"""Append-only daily price observations for cards.

One row per (card, source, variant, price_type, day). Rows are never updated —
a new day yields a new row. This shape is what makes price history queryable
with normal SQL aggregates instead of JSON decoding.
"""

from datetime import date, datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import (
    BigInteger,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Numeric,
    String,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from db.base import Base


class CardPriceSnapshot(Base):
    """A single price observation for a card on a specific day from a specific source."""

    __tablename__ = "card_price_snapshots"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    card_id: Mapped[str] = mapped_column(
        String, ForeignKey("cards.id", ondelete="CASCADE"), nullable=False
    )
    source: Mapped[str] = mapped_column(String, nullable=False)
    variant: Mapped[str | None] = mapped_column(String, nullable=True)
    price_type: Mapped[str] = mapped_column(String, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    value: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    observed_date: Mapped[date] = mapped_column(Date, nullable=False)
    observed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    raw: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)

    __table_args__ = (
        UniqueConstraint(
            "card_id",
            "source",
            "variant",
            "price_type",
            "observed_date",
            name="uq_snapshot_card_source_variant_type_date",
            postgresql_nulls_not_distinct=True,
        ),
        Index(
            "ix_snapshot_card_date_desc",
            "card_id",
            text("observed_date DESC"),
        ),
    )
