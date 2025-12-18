from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from src.models import Product
from src.config import logger


def get_products(
    db: Session, display_in_bot: Optional[bool] = True
) -> List[Product] | None:
    try:
        return db.query(Product).filter(Product.display_in_bot == display_in_bot).all()
    except SQLAlchemyError as e:
        logger.error(f"get_products at crud/products failed:{e}")
        raise e


def get_product_by_id(db: Session, id: int) -> Product | None:
    try:
        return db.get(Product, id)
    except SQLAlchemyError as e:
        logger.error(f"get_product_by_id failed:{e}")
        raise
