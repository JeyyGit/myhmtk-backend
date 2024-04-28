from fastapi import APIRouter

from model import (
    Response,
    Cart,
    Product,
    GetStudentCartResponse,
    GetAllStudentCartResponse,
)
from util import DBSession
from typing import Literal, Optional

cart_router = APIRouter(prefix="/student", tags=["Cart"])


@cart_router.get("/{nim}/cart", response_model=GetAllStudentCartResponse)
async def get_all_student_carts(nim: int):
    async with DBSession() as db:
        student = await db.fetchrow("SELECT * FROM mahasiswa WHERE nim = $1", nim)
        if not student:
            return GetAllStudentCartResponse(
                success=False, message=f"Mahasiswa dengan nim {nim} tidak ditemukan"
            )

        carts_db = await db.fetch(
            """
            SELECT 
                c.id AS cart_id,
                c.quantity,
                c.size,
                c.information,
                c.mahasiswa_nim,
                p.id AS product_id,
                p.name AS product_name, 
                p.price AS product_price,
                p.description as product_desc,
                p.img_url as product_img_url
            FROM cart c
            LEFT JOIN product p ON
                c.product_id = p.id       
            WHERE mahasiswa_nim = $1
        """,
            nim,
        )

    carts = []
    for cart in carts_db:
        product = Product(
            id=cart["product_id"],
            name=cart["product_name"],
            price=cart["product_price"],
            description=cart["product_desc"],
            img_url=cart["product_img_url"],
        )
        carts.append(
            Cart(
                id=cart["cart_id"],
                product=product,
                quantity=cart["quantity"],
                size=cart["size"],
                information=cart["information"],
            )
        )

    return GetAllStudentCartResponse(
        success=True,
        message=f"Berhasil mengambil data cart untuk mahasiswa {nim}",
        carts=carts,
    )


@cart_router.get("/{nim}/cart/{cart_id}", response_model=GetStudentCartResponse)
async def get_student_cart(nim: int, cart_id: int):
    async with DBSession() as db:
        cart_db = await db.fetchrow(
            """
            SELECT 
                c.id AS cart_id,
                c.quantity,
                c.size,
                c.information,
                c.mahasiswa_nim,
                p.id AS product_id,
                p.name AS product_name, 
                p.price AS product_price,
                p.description as product_desc,
                p.img_url as product_img_url
            FROM cart c
            LEFT JOIN product p ON
                c.product_id = p.id
            WHERE mahasiswa_nim = $1 AND c.id = $2
            """,
            nim,
            cart_id,
        )

    if not cart_db:
        return GetStudentCartResponse(
            success=False,
            message=f"Mahasiswa dengan nim {nim} atau cart dengan id {cart_id} tidak ditemukan",
        )

    product = Product(
        id=cart_db["product_id"],
        name=cart_db["product_name"],
        price=cart_db["product_price"],
        description=cart_db["product_desc"],
        img_url=cart_db["product_img_url"],
    )

    cart = Cart(
        id=cart_id,
        product=product,
        quantity=cart_db["quantity"],
        size=cart_db["size"],
        information=cart_db["information"],
    )

    return GetStudentCartResponse(
        success=True, message="Berhasil mengambil data cart", cart=cart
    )


@cart_router.post("/{nim}/cart", response_model=Response)
async def add_student_cart(
    nim: int,
    product_id: int,
    quantity: int,
    size: Literal["xs", "s", "m", "l", "xl", "xxl"],
    information: str = None,
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
            INSERT INTO cart 
                (mahasiswa_nim, product_id, quantity, size, information)
            VALUES
                ($1, $2, $3, $4, $5)
            """,
            nim,
            product_id,
            quantity,
            size,
            information,
        )

    return Response(success=True, message="Berhasil menambahkan cart baru")


@cart_router.put("/{nim}/cart/{cart_id}", response_model=Response)
async def update_student_cart(
    nim: int,
    cart_id: int,
    quantity: Optional[int] = None,
    size: Optional[Literal["xs", "s", "m", "l", "xl", "xxl"]] = None,
    information: Optional[str] = None,
):
    async with DBSession() as db:
        student = await db.fetchrow("SELECT * FROM mahasiswa WHERE nim = $1", nim)
        if not student:
            return Response(
                success=False, message=f"Mahasiswa dengan nim {nim} tidak ditemukan"
            )

        cart = await db.fetchrow("SELECT * FROM cart WHERE id = $1", cart_id)
        if not cart:
            return Response(
                success=False, message=f"Cart dengan id {cart_id} tidak ditemukan"
            )

        await db.execute(
            """
            UPDATE cart SET
                quantity = COALESCE($1, quantity),
                size = COALESCE($2, size),
                information = COALESCE($3, information)
            WHERE id = $4
            """,
            quantity,
            size,
            information,
            cart_id,
        )

    return Response(success=True, message=f"Berhasil menyunting cart {cart_id}")


@cart_router.delete("/{nim}/cart/{cart_id}", response_model=Response)
async def delete_student_cart(nim: int, cart_id: int):
    async with DBSession() as db:
        student = await db.fetchrow("SELECT * FROM mahasiswa WHERE nim = $1", nim)
        if not student:
            return Response(
                success=False, message=f"Mahasiswa dengan nim {nim} tidak ditemukan"
            )

        cart = await db.fetchrow("SELECT * FROM cart WHERE id = $1", cart_id)
        if not cart:
            return Response(
                success=False, message=f"Cart dengan id {cart_id} tidak ditemukan"
            )

        await db.execute("DELETE FROM cart WHERE id = $1", cart_id)

    return Response(success=True, message=f"Berhasil menghapus cart {cart_id}")
