from fastapi import APIRouter
from fastapi.responses import RedirectResponse

from util import db

midtrans_router = APIRouter(prefix="/transaction", tags=["MIDTRANS"])

@midtrans_router.get("/midtrans_callback")
async def midtrans_callback(order_id: int, status_code: int, transaction_status: str):
    if transaction_status in ["settlement", "capture"]:
        await db.pool.execute(
            "UPDATE transaction SET paid = true WHERE id = $1", order_id
        )

        return RedirectResponse("/transaction/success")
    return RedirectResponse("/transaction/pending")

@midtrans_router.get('/success')
async def payment_success():
    return "Payment Successful"

@midtrans_router.get('/pending')
async def payment_pending():
    return "Payment Pending"