from fastapi import APIRouter

from typing import Optional, Literal
import datetime as dt

from util import DBSession
from model import (
    Response,
    Order,
    Product,
    Student,
    GetOrderResponse,
    GetAllOrderResponse,
)


order_router = APIRouter(prefix="/order", tags=["Order"])


@order_router.get("", response_model=GetAllOrderResponse)
async def get_all_orders(nim: int = None):
    async with DBSession() as db:
        if nim:
            student = await db.fetchrow("SELECT * FROM mahasiswa WHERE nim = $1", nim)
            if not student:
                return GetAllOrderResponse(
                    success=False, message=f"Mahasiswa dengan nim {nim} tidak ditemukan"
                )
            orders_db = await db.fetch(
                """
                SELECT
                    o.id AS order_id,
                    o.product_id,
                    o.quantity,
                    o.size,
                    o.information,
                    o.order_date,
                    o.paid,
                    o.completed,
                    p.name AS product_name,
                    p.price AS product_price,
                    p.description as product_desc,
                    p.img_url as product_img_url,
                    m.nim as mhs_nim,
                    m.name as mhs_name,
                    m.tel as mhs_tel,
                    m.email as mhs_email,
                    m.pass_hash as mhs_pass_hash
                FROM "order" o
                LEFT JOIN product p ON
                    o.product_id = p.id
                LEFT JOIN mahasiswa m ON
                    o.mahasiswa_nim = m.nim
                WHERE mahasiswa_nim = $1
                """,
                nim,
            )
        else:
            orders_db = await db.fetch(
                """
                SELECT
                    o.id AS order_id,
                    o.product_id,
                    o.quantity,
                    o.size,
                    o.information,
                    o.order_date,
                    o.paid,
                    o.completed,
                    p.name AS product_name,
                    p.price AS product_price,
                    p.description as product_desc,
                    p.img_url as product_img_url,
                    m.nim as mhs_nim,
                    m.name as mhs_name,
                    m.tel as mhs_tel,
                    m.email as mhs_email,
                    m.pass_hash as mhs_pass_hash
                FROM "order" o
                LEFT JOIN product p ON
                    o.product_id = p.id
                LEFT JOIN mahasiswa m ON
                    o.mahasiswa_nim = m.nim
                """
            )

    orders = []
    for order in orders_db:
        product = Product(
            id=order["product_id"],
            name=order["product_name"],
            price=order["product_price"],
            description=order["product_desc"],
            img_url=order["product_img_url"],
        )
        mahasiswa = Student(
            nim=order["mhs_nim"],
            name=order["mhs_name"],
            tel=order["mhs_tel"],
            email=order["mhs_email"],
            pass_hash=order["mhs_pass_hash"],
        )
        orders.append(
            Order(
                id=order["order_id"],
                mahasiswa=mahasiswa,
                product=product,
                quantity=order["quantity"],
                size=order["size"],
                information=order["information"],
                order_date=order["order_date"],
                paid=order["paid"],
                completed=order["completed"],
            )
        )

    return GetAllOrderResponse(
        success=True, message="Berhasil mengambil data semua order", orders=orders
    )


@order_router.get("/{order_id}", response_model=GetOrderResponse)
async def get_order(order_id: int):
    async with DBSession() as db:
        order_db = await db.fetchrow(
            """
            SELECT
                o.id AS order_id,
                o.product_id,
                o.quantity,
                o.size,
                o.information,
                o.order_date,
                o.paid,
                o.completed,
                p.name AS product_name,
                p.price AS product_price,
                p.description as product_desc,
                p.img_url as product_img_url,
                m.nim as mhs_nim,
                m.name as mhs_name,
                m.tel as mhs_tel,
                m.email as mhs_email,
                m.pass_hash as mhs_pass_hash
            FROM "order" o
            LEFT JOIN product p ON
                o.product_id = p.id
            LEFT JOIN mahasiswa m ON
                o.mahasiswa_nim = m.nim
            WHERE o.id = $1
            """,
            order_id,
        )

    if not order_db:
        return GetOrderResponse(
            success=False, message=f"Order dengan id {order_id} tidak ditemukan"
        )

    product = Product(
        id=order_db["product_id"],
        name=order_db["product_name"],
        price=order_db["product_price"],
        description=order_db["product_desc"],
        img_url=order_db["product_img_url"],
    )
    mahasiswa = Student(
        nim=order_db["mhs_nim"],
        name=order_db["mhs_name"],
        tel=order_db["mhs_tel"],
        email=order_db["mhs_email"],
        pass_hash=order_db["mhs_pass_hash"],
    )

    order = Order(
        id=order_db["order_id"],
        mahasiswa=mahasiswa,
        product=product,
        quantity=order_db["quantity"],
        size=order_db["size"],
        information=order_db["information"],
        order_date=order_db["order_date"],
        paid=order_db["paid"],
        completed=order_db["completed"],
    )

    return GetOrderResponse(
        success=True, message="Berhasil mengambil data order", order=order
    )


@order_router.post("", response_model=Response)
async def add_order(
    nim: int,
    product_id: int,
    quantity: int,
    size: Literal["xs", "s", "m", "l", "xl", "xxl"],
    order_date: dt.datetime,
    paid: bool,
    completed: bool,
    information: Optional[str] = None,
):
    async with DBSession() as db:
        student = await db.fetchrow("SELECT * FROM mahasiswa WHERE nim = $1", nim)
        if not student:
            return Response(
                success=False, message=f"Mahasiswa dengan nim {nim} tidak ditemukan"
            )

        product = await db.fetchrow("SELECT * FROM product WHERE id = $1", product_id)
        if not product:
            return Response(
                success=False, message=f"Product dengan id {product_id} tidak ditemukan"
            )

        await db.execute(
            """
            INSERT INTO "order"
                (mahasiswa_nim, product_id, quantity, size, information, order_date, paid, completed)
            VALUES
                ($1, $2, $3, $4, $5, $6, $7, $8)
        """,
            nim,
            product_id,
            quantity,
            size,
            information,
            order_date,
            paid,
            completed,
        )

        return Response(success=True, message="Berhasil menambahkan order baru")


@order_router.put("/{order_id}", response_model=Response)
async def update_order(
    order_id: int, paid: Optional[bool] = None, completed: Optional[bool] = None
):
    async with DBSession() as db:
        order = await db.fetchrow('SELECT * FROM "order" WHERE id = $1', order_id)
        if not order:
            return Response(
                success=False, message=f"Order dengan id {order_id} tidak ditemukan"
            )

        await db.execute(
            """
            UPDATE "order" SET
                paid = COALESCE($1, paid),
                completed = COALESCE($2, completed)
            WHERE id = $3
        """,
            paid,
            completed,
            order_id,
        )

    return Response(success=True, message=f"Berhasil menyunting order {order_id}")


@order_router.delete("/{order_id}", response_model=Response)
async def delete_order(order_id: int):
    async with DBSession() as db:
        order = await db.fetchrow('SELECT * FROM "order" WHERE id = $1', order_id)
        if not order:
            return Response(
                success=False, message=f"Order dengan id {order_id} tidak ditemukan"
            )

        await db.execute('DELETE FROM "order" WHERE id = $1', order_id)

    return Response(success=True, message=f"Berhasil menghapus order {order_id}")
