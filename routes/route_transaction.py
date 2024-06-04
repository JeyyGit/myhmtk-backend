from fastapi import APIRouter, HTTPException
from fastapi.responses import RedirectResponse

from typing import List, Optional
import datetime as dt
import pytz

from util import create_transaction, db
from model import (
    AddTransactionResponse,
    GetAllTransactionResponse,
    GetTransactionResponse,
    Response,
    Order,
    Transaction,
)


transaction_router = APIRouter(prefix="/student", tags=["Transaction"])


@transaction_router.get("/{nim}/transactions", response_model=GetAllTransactionResponse)
async def get_all_student_transactions(nim: int):
    student = await db.pool.fetchrow("SELECT * FROM mahasiswa WHERE nim = $1", nim)
    if not student:
        return GetAllTransactionResponse(
            success=False,
            message=f"Mahasiswa dengan nim {nim} tidak ditemukan",
            transactions=[],
        )
    transactions_db = await db.pool.fetch(
        """
        SELECT
            t.id AS transaction_id,
            t.transaction_date,
            t.paid,
            t.completed,
            t.payment_url,
            t.status,
            o.id AS order_id,
            o.product_id,
            o.quantity,
            o.size,
            o.information,
            p.name AS product_name,
            p.price AS product_price,
            p.description AS product_description,
            p.img_url AS product_img_url
        FROM
            transaction t
            JOIN "order" o ON t.id = o.transaction_id
            JOIN product p ON o.product_id = p.id
        WHERE
            t.mahasiswa_nim = $1
        ORDER BY transaction_date DESC
    """,
        nim,
    )

    transactions_dict = {}
    for row in transactions_db:
        transaction_id = row["transaction_id"]

        if transaction_id not in transactions_dict:
            transactions_dict[transaction_id] = {
                "transaction_id": transaction_id,
                "transaction_date": row["transaction_date"],
                "paid": row["paid"],
                "completed": row["completed"],
                "payment_url": row["payment_url"],
                "status": row["status"],
                "orders": [],
            }

        order = {
            "id": row["order_id"],
            "product": {
                "id": row["product_id"],
                "name": row["product_name"],
                "price": row["product_price"],
                "description": row["product_description"],
                "img_url": row["product_img_url"],
            },
            "quantity": row["quantity"],
            "size": row["size"],
            "information": row["information"],
        }
        transactions_dict[transaction_id]["orders"].append(order)

    trans_data = []
    ids_need_to_change = []
    for trans_data in transactions_dict.values():
        if trans_data["status"] == "pending" and trans_data[
            "transaction_date"
        ] + dt.timedelta(minutes=5) <= dt.datetime.now(
            pytz.timezone("Asia/Jakarta")
        ).replace(
            tzinfo=None
        ):
            trans_data["status"] = "expire"
            ids_need_to_change.append((trans_data["transaction_id"],))

    if ids_need_to_change:
        await db.pool.executemany(
            "UPDATE transaction SET status = 'expire' WHERE id = $1", ids_need_to_change
        )

    transactions = [
        Transaction(
            id=trans_data["transaction_id"],
            orders=[Order(**order_data) for order_data in trans_data["orders"]],
            transaction_date=trans_data["transaction_date"],
            paid=trans_data["paid"],
            completed=trans_data["completed"],
            payment_url=trans_data["payment_url"],
            status=trans_data["status"],
        )
        for trans_data in transactions_dict.values()
    ]

    return GetAllTransactionResponse(
        success=True,
        message=f"Berhasil mengambil semua transaksi mahasiswa nim {nim}",
        transactions=transactions,
    )


@transaction_router.get(
    "/{nim}/transactions/{transaction_id}", response_model=GetTransactionResponse
)
async def get_student_transaction(nim: int, transaction_id: int):
    student = await db.pool.fetchrow("SELECT * FROM mahasiswa WHERE nim = $1", nim)
    if not student:
        return GetAllTransactionResponse(
            success=False,
            message=f"Mahasiswa dengan nim {nim} tidak ditemukan",
            transactions=[],
        )
    transaction_db = await db.pool.fetch(
        """
        SELECT
            t.id AS transaction_id,
            t.transaction_date,
            t.paid,
            t.completed,
            t.payment_url,
            t.status,
            o.id AS order_id,
            o.product_id,
            o.quantity,
            o.size,
            o.information,
            p.name AS product_name,
            p.price AS product_price,
            p.description AS product_description,
            p.img_url AS product_img_url
        FROM
            transaction t
            JOIN "order" o ON t.id = o.transaction_id
            JOIN product p ON o.product_id = p.id
        WHERE
            t.id = $1
    """,
        transaction_id,
    )

    if not transaction_db:
        return GetTransactionResponse(
            success=False, message=f"Transaksi id {transaction_id} tidak ditemukan"
        )

    transaction_data = {
        "transaction_id": transaction_id,
        "transaction_date": transaction_db[0]["transaction_date"],
        "paid": transaction_db[0]["paid"],
        "completed": transaction_db[0]["completed"],
        "payment_url": transaction_db[0]["payment_url"],
        "status": transaction_db[0]["status"],
        "orders": [],
    }

    for row in transaction_db:
        order = {
            "id": row["order_id"],
            "product": {
                "id": row["product_id"],
                "name": row["product_name"],
                "price": row["product_price"],
                "description": row["product_description"],
                "img_url": row["product_img_url"],
            },
            "quantity": row["quantity"],
            "size": row["size"],
            "information": row["information"],
        }
        transaction_data["orders"].append(order)

    transaction = Transaction(
        id=transaction_data["transaction_id"],
        # mahasiswa=student,
        orders=[Order(**order_data) for order_data in transaction_data["orders"]],
        transaction_date=transaction_data["transaction_date"],
        paid=transaction_data["paid"],
        completed=transaction_data["completed"],
        payment_url=transaction_data["payment_url"],
        status=transaction_data["status"],
    )

    return GetTransactionResponse(
        success=True,
        message=f"Berhasl mendapatkan data transaksi {transaction_id}",
        transaction=transaction,
    )


@transaction_router.post("/{nim}/transactions", response_model=AddTransactionResponse)
async def add_student_transaction(nim: int, cart_ids: List[int]):
    student = await db.pool.fetchrow("SELECT * FROM mahasiswa WHERE nim = $1", nim)
    if not student:
        return AddTransactionResponse(
            success=False,
            message=f"Mahasiswa dengan nim {nim} tidak ditemukan",
            redirect_url=None,
        )

    cart_details = await db.pool.fetch(
        """
        SELECT
            c.id AS cart_id,
            c.product_id,
            c.quantity,
            c.size,
            c.information,
            p.name,
            p.img_url,
            p.price
        FROM
            cart c
        INNER JOIN
            product p ON c.product_id = p.id
        WHERE
            c.id = ANY($1)
        """,
        cart_ids,
    )

    transaction_id = await db.pool.fetchval(
        """
        INSERT INTO transaction (
            mahasiswa_nim,
            transaction_date,
            paid,
            completed,
            status
        )
        VALUES ($1, $2, false, false, 'pending')
        RETURNING id
        """,
        nim,
        dt.datetime.now(pytz.timezone("Asia/Jakarta")).replace(tzinfo=None),
    )

    item_details = [
        {
            "id": cart["product_id"],
            "price": cart["price"],
            "name": cart["name"],
            "quantity": cart["quantity"],
            "merchant_name": "MyHMTK",
            "url": cart["img_url"],
        }
        for cart in cart_details
    ]

    # add tax
    item_details.append(
        {
            "id": 0,
            "price": 5000,
            "name": "Biaya Admin",
            "quantity": 1,
            "merchant_name": "MyHMTK",
        }
    )

    total_price = sum(item["quantity"] * item["price"] for item in item_details)

    midtrans_payload = {
        "transaction_details": {
            "order_id": str(transaction_id),
            "gross_amount": total_price,
        },
        "payment_type": "qris",
        "item_details": item_details,
        "customer_detalils": {
            "first_name": student["name"].split()[0],
            "last_name": student["name"].split()[-1],
            "email": student["email"],
            "phone": str(student["tel"]),
            # "address"
        },
        "page_expiry": {"duration": 5, "unit": "minutes"},
        "expiry": {"duration": 5, "unit": "minutes"},
        # "enabled_payments": ["credit_card", "gopay", "shopeepay", "other_qris"],
    }

    try:
        redirect_url = await create_transaction(midtrans_payload)
    except Exception as e:
        await db.pool.execute("DELETE FROM transaction WHERE id = $1", transaction_id)
        return HTTPException(status_code=400, detail=str(e))

    await db.pool.execute(
        "UPDATE transaction SET payment_url = $1 WHERE id = $2",
        redirect_url,
        transaction_id,
    )

    await db.pool.executemany(
        """
        INSERT INTO \"order\" (
            mahasiswa_nim, product_id, quantity, size, information, transaction_id)
        VALUES
            ($1, $2, $3, $4, $5, $6)
        """,
        [
            (
                student["nim"],
                cart["product_id"],
                cart["quantity"],
                cart["size"],
                cart["information"],
                transaction_id,
            )
            for cart in cart_details
        ],
    )

    await db.pool.execute("DELETE FROM cart WHERE id = ANY($1)", cart_ids)

    return AddTransactionResponse(
        success=True,
        message="Berhasil menambahkan transaksi baru",
        payment_url=redirect_url,
    )


@transaction_router.put("/{nim}/transactions/{transaction_id}", response_model=Response)
async def update_student_transaction(
    nim: int,
    transaction_id: int,
    paid: Optional[bool] = None,
    completed: Optional[bool] = None,
    status: Optional[str] = None,
):
    student = await db.pool.fetchrow("SELECT * FROM mahasiswa WHERE nim = $1", nim)
    if not student:
        return Response(
            success=False, message=f"Mahasiswa dengan nim {nim} tidak ditemukan"
        )

    transaction = await db.pool.fetchrow(
        "SELECT * FROM transaction WHERE id = $1", transaction_id
    )
    if not transaction:
        return Response(
            success=False,
            message=f"Transaksi dengan id {transaction_id} tidak ditemukan",
        )

    await db.pool.execute(
        "UPDATE transaction SET paid = COALESCE($1, paid), completed = COALESCE($2, completed), status = COALESCE($3, status) WHERE id = $4",
        paid,
        completed,
        status,
        transaction_id,
    )

    return Response(
        success=True, message=f"Berhasil menyunting transaksi {transaction_id}"
    )


# can not delete a transaction
# @transaction_router.delete("...")
#   ...
