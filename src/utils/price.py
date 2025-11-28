from src.config import logger
from typing import Union, Dict


async def calculate_prices(product: str = None) -> Union[Dict, None]:
    # * here the prices will be calucalated asynrounously for now it's just mock data
    try:
        if product is None:
            return {
                "product_no1": {
                    "v1": 100000,
                    "v2": 200000,
                    "v3": 300000,
                },
                "product_no2": {
                    "v1": 400000,
                    "v2": 500000,
                    "v3": 600000,
                },
                "product_no3": {
                    "v1": 700000,
                    "v2": 800000,
                    "v3": 900000,
                },
            }
        if product == "product_no1":
            return {
                "v1": 100000,
                "v2": 200000,
                "v3": 300000,
            }
        if product == "product_no2":
            return {
                "v1": 400000,
                "v2": 500000,
                "v3": 600000,
            }
        if product == "product_no3":
            return {
                "v1": 700000,
                "v2": 800000,
                "v3": 900000,
            }
        else:
            raise KeyError("no such product")

    except Exception as e:
        logger.error(f"claculate_price failed:{e}")
        raise
