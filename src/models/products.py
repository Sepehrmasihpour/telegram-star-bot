from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Numeric, ForeignKey, Enum as SAEnum, Boolean
from typing import List
from src.db.base import Base
from decimal import Decimal
from enum import Enum


class PricingStrategy(str, Enum):
    FIXED = "fixed"
    MARKET = "market"
    MARKET_PLUS_MARGIN = "market_plus_margin"


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    pricing_strategy: Mapped[PricingStrategy] = mapped_column(
        SAEnum(PricingStrategy), nullable=False, default=PricingStrategy.FIXED
    )
    market_symbol: Mapped[str | None] = mapped_column(String(50), nullable=True)
    display_in_bot: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default="false"
    )
    versions: Mapped[List["ProductVersion"]] = relationship(
        back_populates="product",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class ProductVersion(Base):
    __tablename__ = "product_versions"

    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
    )
    code: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    price: Mapped[Decimal] = mapped_column(Numeric(18, 8), nullable=False)
    version_name: Mapped[str] = mapped_column(String(250), nullable=False)
    margin_bps: Mapped[int | None] = mapped_column(Integer, nullable=True)
    product: Mapped["Product"] = relationship(back_populates="versions")
