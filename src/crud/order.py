from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from src.config import logger
from src.models.order import Order, OrderItem, OrderStatus
from src.models.products import ProductVersion


# --- Small input DTOs (optional but clean) ---


@dataclass(frozen=True)
class CreateOrderItemIn:
    product_version_id: int
    quantity: Decimal


# --- Helpers ---


def _utcnow() -> datetime:
    # match DateTime(timezone=True) style if you later switch models
    return datetime.now(timezone.utc)


def _as_decimal(x) -> Decimal:
    # Guard against float input accidentally sneaking in
    if isinstance(x, Decimal):
        return x
    return Decimal(str(x))


# --- CRUD ---


def create_order(
    db: Session,
    *,
    user_id: int,
    status: OrderStatus = OrderStatus.WAITING_FOR_PAYMENT,
    created_at: datetime | None = None,
    commit: bool = True,
) -> Order:
    """
    Create an empty order (no items yet). Use create_order_with_items() if you want items too.
    """
    try:
        order = Order(
            user_id=user_id,
            status=status,
            created_at=created_at or _utcnow(),
            total_amount=None,  # will be set once items exist
            paid_at=None,
        )
        db.add(order)
        db.flush()  # ensures order.id is available

        if commit:
            db.commit()
            db.refresh(order)

        return order
    except SQLAlchemyError as e:
        db.rollback()
        logger.error("create_order failed: %s", e)
        raise


def create_order_item(
    db: Session,
    *,
    order: Order,
    product_version: ProductVersion,
    quantity: Decimal,
    unit_price: Decimal | None = None,
    commit: bool = True,
) -> OrderItem:
    """
    Create one OrderItem linked to an existing Order.
    unit_price defaults to product_version.price if not provided.
    """
    try:
        qty = _as_decimal(quantity)
        if qty <= 0:
            raise ValueError("quantity must be > 0")

        price = _as_decimal(
            unit_price if unit_price is not None else product_version.price
        )
        if price is None:
            raise ValueError("unit_price is required (product_version.price is None)")

        item = OrderItem(
            order_id=order.id,
            product_version_id=product_version.id,
            unit_price=price,
            quantity=qty,
        )
        db.add(item)
        db.flush()

        # keep order.total_amount consistent
        line_total = price * qty
        order.total_amount = (
            _as_decimal(order.total_amount or Decimal("0")) + line_total
        )

        if commit:
            db.commit()
            db.refresh(item)
            db.refresh(order)

        return item
    except SQLAlchemyError as e:
        db.rollback()
        logger.error("create_order_item failed: %s", e)
        raise
