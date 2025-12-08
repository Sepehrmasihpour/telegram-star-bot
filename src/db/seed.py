# src/db/seed.py
from sqlalchemy.orm import Session
from src.models.products import Product, ProductVersion
from src.config import logger


def seed_initial_products(db: Session) -> None:
    """
    Seeds the database with dummy Product + ProductVersion data for testing.
    Will NOT insert anything if products already exist.
    """
    # avoid accidental duplicates
    existing_count = db.query(Product).count()
    if existing_count > 0:
        logger.info("Seed skipped: products already exist.")
        return

    logger.info("Seeding dummy product data...")

    # ------------------------
    # Example dummy data block
    # ------------------------
    dummy_data = [
        {
            "name": "Premium Stars Pack",
            "display_in_bot": True,
            "versions": [
                {"version_code": "v1", "price": 15000},
                {"version_code": "v2", "price": 30000},
            ],
        },
        {
            "name": "Telegram Premium Upgrade",
            "display_in_bot": True,
            "versions": [
                {"version_code": "1_month", "price": 120000},
                {"version_code": "12_months", "price": 1100000},
            ],
        },
        {
            "name": "Special Offer Bundle",
            "display_in_bot": False,
            "versions": [
                {"version_code": "std", "price": 9999},
                {"version_code": "plus", "price": 15999},
            ],
        },
    ]

    # Insert products and their versions
    for p in dummy_data:
        product = Product(
            name=p["name"],
            display_in_bot=p["display_in_bot"],
        )
        db.add(product)
        db.flush()  # get product.id before adding versions

        for v in p["versions"]:
            version = ProductVersion(
                product_id=product.id,
                version_code=v["version_code"],
                # you can add price here if you have a price field
            )
            db.add(version)

    db.commit()
    logger.info("Dummy product data seeded successfully.")
