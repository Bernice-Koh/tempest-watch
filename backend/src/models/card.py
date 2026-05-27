"""Canonical Pokémon TCG card metadata, sourced from pokemontcg.io.

One row per card per set. The natural primary key is pokemontcg.io's own card ID
(e.g. `swsh12-1`), which is globally unique and stable upstream.
"""

from datetime import datetime
from typing import Any

from sqlalchemy import ARRAY, DateTime, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from db.base import Base


class Card(Base):
    """A single Pokémon TCG card, mirroring pokemontcg.io's card object."""

    __tablename__ = "cards"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    set_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    set_number: Mapped[str] = mapped_column(String, nullable=False)
    name: Mapped[str] = mapped_column(String, index=True, nullable=False)
    supertype: Mapped[str] = mapped_column(String, nullable=False)
    subtypes: Mapped[list[str]] = mapped_column(
        ARRAY(String), nullable=False, server_default="{}"
    )
    rarity: Mapped[str | None] = mapped_column(String, nullable=True)
    image_small: Mapped[str | None] = mapped_column(String, nullable=True)
    image_large: Mapped[str | None] = mapped_column(String, nullable=True)
    raw: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    first_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    last_updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
