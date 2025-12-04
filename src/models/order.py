from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, DateTime, Numeric, Enum as SAEnum
from src.db.base import Base
from datetime import datetime
from decimal import Decimal
from enum import Enum
from src.models.products import ProductVersion


class OrderStatus(str, Enum):
    PAID = "paid"
    WAITING_FOR_PAYMENT = "waiting_for_payment"
    EXPIRED = "expired"


class Order(Base):
    __tablename__ = "orders"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    total_amount: Mapped[Decimal] = mapped_column(Numeric(18, 8), nullable=True)
    status: Mapped[OrderStatus] = mapped_column(
        SAEnum(OrderStatus), nullable=False, default=OrderStatus.WAITING_FOR_PAYMENT
    )
    paid_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    items: Mapped[list["OrderItem"]] = relationship(
        back_populates="order", cascade="all, delete-orphan"
    )


class OrderItem(Base):
    __tablename__ = "order_items"
    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(
        ForeignKey("orders.id", ondelete="CASCADE"), nullable=False
    )
    product_version_id: Mapped[int] = mapped_column(
        ForeignKey("product_versions.id"), nullable=False
    )
    unit_price: Mapped[Decimal] = mapped_column(Numeric(18, 8), nullable=False)
    quantity: Mapped[Decimal] = mapped_column(Numeric(18, 8), nullable=False)

    order: Mapped["Order"] = relationship(back_populates="items")
    product_version: Mapped["ProductVersion"] = relationship()
