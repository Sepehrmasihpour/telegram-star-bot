# src/db/seed.py
from sqlalchemy.orm import Session
from src.models import Product, ProductVersion
from src.config import logger
from typing import Dict
from src.crud.chat_outpus import (
    create_button,
    create_button_index,
    create_chat_output,
    create_placeholder,
    get_button_by_name,
    get_chat_output_by_name,
    get_placeholder_by_name,
)


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
def seed_initial_chat_outputs(db: Session, seed_data: Dict) -> None:
    try:
        buttons = seed_data.get("buttons")
        for button in buttons:
            name = button.get("name")
            button_exists = get_button_by_name(db=db, name=name)
            if button_exists is None:
                create_button(
                    db=db,
                    name=name,
                    text=button.get("text"),
                    callback_data=button.get("callback_data"),
                )
        chat_outputs = seed_data.get("chat_outputs")
        for chat_output in chat_outputs:
            name = chat_output.get("name")
            chat_output_exists = get_chat_output_by_name(db=db, name=name)
            if chat_output_exists is not None:
                pass
            chat_output_data = create_chat_output(
                db=db, name=name, text=chat_output.get("text")
            )
            placeholders = chat_output.get("placeholders")
            for placeholder in placeholders:
                placeholder_exists = get_placeholder_by_name(
                    db=db, name=placeholder.get("name")
                )
                if placeholder_exists is not None:
                    pass
                create_placeholder(
                    db=db,
                    chat_output_id=chat_output_data.id,
                    name=placeholder.get("name"),
                    type=placeholder.get("type"),
                )
            buttons = chat_output.get("buttons")
            for button in buttons:
                button_data = get_button_by_name(db=db, name=button.get("name"))
                create_button_index(
                    db=db,
                    chat_output_id=chat_output_data.id,
                    button_id=button_data.id,
                    number=button.get("number"),
                )

    except Exception as e:
        logger.error(f"seed_initial_chat_outputs failed:{e}")
