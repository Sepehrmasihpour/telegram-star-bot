from fastapi import HTTPException, Depends, Form, status
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.routing import APIRouter

from src.config import logger
from src.crud.order import update_order
from src.db import get_db

from sqlalchemy.orm import Session

router = APIRouter()


@router.get("/pay", response_class=HTMLResponse)
async def payment_page(order_id: int):
    return f"""
    <html>
        <body>
            <h2>Simulated Payment</h2>
            <p>Order ID: {order_id}</p>
            <form action="/confirm-payment" method="post">
                <input type="hidden" name="order_id" value="{order_id}">
                <button type="submit">Pay</button>
            </form>
        </body>
    </html>
    """


@router.post("/confirm-payment", response_class=HTMLResponse)
async def confirm_payment(order_id: int = Form(...), db: Session = Depends(get_db)):
    order = update_order(db=db, order_id=order_id, status="paid")
    if order.status != "paid":
        logger.error(f"order payment failed:{order_id}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    if order.status == "paid":
        logger.info(f"order payment succeded:{order_id}")
        return {"ok": True}
    return RedirectResponse(url="/success", status_code=303)


@router.get("/success", response_class=HTMLResponse)
async def success():
    return "<h2>Payment Successful ✅</h2>"
