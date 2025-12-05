from sqlalchemy.orm import Session
from decimal import Decimal
from src.models import ProductVersion, MarketFeed
from src.models.products import PricingStrategy


def get_version_price(version: ProductVersion, db: Session) -> Decimal:
    product = version.product

    if product.pricing_strategy == PricingStrategy.FIXED:
        return version.price

    if product.market_symbol is None:
        raise ValueError("market_symbol is required for MARKET pricing strategies")

    feed = db.query(MarketFeed).filter(MarketFeed.symbol == product.market_symbol).one()
    market_price_per_unit: Decimal = feed.price
    base_price: Decimal = market_price_per_unit * Decimal(version.units)

    if product.pricing_strategy == PricingStrategy.MARKET:
        return base_price

    if product.pricing_strategy == PricingStrategy.MARKET_PLUS_MARGIN:
        margin_bps = version.margin_bps or 0
        multiplier = Decimal("1") + (Decimal(margin_bps) / Decimal("10000"))
        return base_price * multiplier

    raise ValueError(f"Unsupported pricing strategy: {product.pricing_strategy}")
