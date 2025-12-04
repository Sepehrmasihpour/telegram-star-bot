from sqlalchemy import DateTime, String, Numeric
from decimal import Decimal
from sqlalchemy.orm import Mapped, mapped_column
from src.db.base import Base
from datetime import datetime


class MarketFeed(Base):
    __tablename__ = "market_feed"

    id: Mapped[int] = mapped_column(primary_key=True)
    market_symbol: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    price: Mapped[Decimal] = mapped_column(Numeric(18, 8), nullable=False)
    last_updated: Mapped[datetime] = mapped_column(DateTime, nullable=False)
