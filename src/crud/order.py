from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from sqlalchemy import select

from src.config import logger
from src.models.order import Order, OrderItem, OrderStatus
from src.models.products import ProductVersion
from typing import Sequence, Union, Any
from src.services.pricing import get_version_price


# --- Small input DTOs (optional but clean) ---


@dataclass(frozen=True)
class CreateOrderItemIn:
    product_version_id: int
    quantity: int = 1


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
    try:
        qty = quantity
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


def create_order_with_items(
    db: Session,
    *,
    user_id: int,
    items: Sequence[CreateOrderItemIn],
    status: OrderStatus = OrderStatus.WAITING_FOR_PAYMENT,
    created_at: datetime | None = None,
    commit: bool = True,
) -> Order:
    """
    Atomic creation:
      - creates Order
      - validates product versions
      - creates OrderItems
      - computes total_amount
    """
    try:
        if not items:
            raise ValueError("items must not be empty")

        # 1) Fetch all requested ProductVersions in one query
        pv_ids = [i.product_version_id for i in items]
        stmt = select(ProductVersion).where(ProductVersion.id.in_(pv_ids))
        versions = db.execute(stmt).scalars().all()

        versions_by_id = {v.id: v for v in versions}
        missing = [pv_id for pv_id in pv_ids if pv_id not in versions_by_id]
        if missing:
            raise ValueError(f"Unknown product_version_id(s): {missing}")

        # 2) Create the order
        order = Order(
            user_id=user_id,
            status=status,
            created_at=created_at or _utcnow(),
            total_amount=Decimal("0"),
            paid_at=None,
        )
        db.add(order)
        db.flush()  # order.id available now

        # 3) Create items + compute total
        total = Decimal("0")
        for req in items:
            pv = versions_by_id[req.product_version_id]
            qty = req.quantity
            if qty <= 0:
                raise ValueError("quantity must be > 0")

            unit_price = get_version_price(version=pv, db=db)
            db.add(
                OrderItem(
                    order_id=order.id,
                    product_version_id=pv.id,
                    unit_price=unit_price,
                    quantity=qty,
                )
            )
            total += unit_price * qty

        order.total_amount = total

        if commit:
            db.commit()
            db.refresh(order)
            # items are relationship-loaded lazily unless you eager load later

        return order
    except (SQLAlchemyError, ValueError) as e:
        db.rollback()
        logger.error("create_order_with_items failed: %s", e)
        raise


def delete_order(db: Session, order_id: Union[str, int]) -> bool:
    try:
        order = db.get(Order, int(order_id))
        if not order:
            logger.info("delete_order: no order with id=%s", order_id)
            return False

        db.delete(order)
        db.commit()
        return True

    except SQLAlchemyError:
        db.rollback()
        logger.exception("failed to delete order by id=%s", order_id)
        return False


def update_order(db: Session, order_id: Union[str, int], **fields: Any) -> Order | None:
    try:
        order = db.get(Order, int(order_id))

        if order is None:
            logger.info("update_chat_by_chat_id: no chat with chat_id=%s", order_id)
            return None

        for key, value in fields.items():
            if hasattr(order, key):
                setattr(order, key, value)
            else:
                raise AttributeError(f"order has no attribute '{key}'")

        db.commit()
        db.refresh(order)
        return order

    except SQLAlchemyError as e:
        db.rollback()
        logger.error("failed to update order by order_id: %s", e)
        raise
