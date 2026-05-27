"""SQLAlchemy ORM models.

Importing this package registers every model with Base.metadata, which is what
Alembic and the engine use as the source of truth for schema. New model modules
must be imported here.
"""

from models.card import Card
from models.card_price_snapshot import CardPriceSnapshot

__all__ = ["Card", "CardPriceSnapshot"]
