# src/db/seed.py
from sqlalchemy.orm import Session
from src.models import Product, ProductVersion, ChatOutput, Placeholder, Button
from src.config import logger
from src.crud.chat_outpus import create_chat_output_instance_with_placeholder_and_button


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
                {"code": "v1", "price": 15000, "version_name": "version 1"},
                {"code": "v2", "price": 30000, "version_name": "version 2"},
            ],
        },
        {
            "name": "Telegram Premium Upgrade",
            "display_in_bot": True,
            "versions": [
                {"code": "1_month", "price": 120000, "version_name": "one month"},
                {"code": "12_months", "price": 1100000, "version_name": "12 month"},
            ],
        },
        {
            "name": "Special Offer Bundle",
            "display_in_bot": False,
            "versions": [
                {"code": "std", "price": 9999, "version_name": "special"},
                {"code": "plus", "price": 15999, "version_name": "super special"},
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
                code=v["code"],
                price=v["price"],
                version_name=v["version_name"],
            )
            db.add(version)

    db.commit()
    logger.info("Dummy product data seeded successfully.")


# TODO
# it should chech weather the instance exists or not if yes skip
def seed_initial_chat_outputs(
    db: Session,
) -> None: ...
