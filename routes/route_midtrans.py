from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse

from util import db, verify_signature

import datetime as dt

midtrans_router = APIRouter(prefix="/transaction", tags=["MIDTRANS"])


@midtrans_router.get("/midtrans_callback")
async def midtrans_callback(order_id: int, status_code: int, transaction_status: str):
    if transaction_status in ["settlement", "capture"]:
        # await db.pool.execute(
        #     "UPDATE transaction SET paid = true WHERE id = $1", order_id
        # )

        return RedirectResponse("/transaction/success")
    return RedirectResponse("/transaction/pending")


@midtrans_router.post("/midtrans_notification")
async def midtrans_notification(request: Request):
    body = await request.json()
    print(
        verify_signature(
            body["order_id"],
            body["status_code"],
            body["gross_amount"],
            body["signature_key"],
        )
    )

    if verify_signature(
        body["order_id"],
        body["status_code"],
        body["gross_amount"],
        body["signature_key"],
    ):
        print(
            f"Transaction Notification: Time={body['transaction_time']} Status={body['transaction_status']} Amount={body['gross_amount']}"
        )

        status = body["transaction_status"]
        if status in ["settlement", "capture"]:
            await db.pool.execute(
                "UPDATE transaction SET paid = true, status = $1 WHERE id = $2",
                status,
                int(body["order_id"]),
            )
        elif status in ["expire", "deny", "cancel", "failure"]:
            await db.pool.execute(
                "UPDATE transaction SET status = $1 WHERE id = $2",
                status,
                int(body["order_id"]),
            )
        return "Notification received"
    else:
        return "Invalid signature"


@midtrans_router.get("/success")
async def payment_success():
    return "Payment Successful"


@midtrans_router.get("/pending")
async def payment_pending():
    return "Payment Pending"
