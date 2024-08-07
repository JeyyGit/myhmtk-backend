from fastapi import APIRouter, HTTPException

from typing import Optional

from util import db
from model import Product, Response, GetAllProductResponse, GetProductResponse


product_router = APIRouter(prefix="/product", tags=["Product"])


@product_router.get("", response_model=GetAllProductResponse)
async def get_all_products():
    products_db = await db.pool.fetch("SELECT * FROM product")

    products = []
    for product in products_db:
        products.append(
            Product(
                id=product["id"],
                name=product["name"],
                price=product["price"],
                description=product["description"],
                img_url=product["img_url"],
            )
        )

    return GetAllProductResponse(
        success=True, message="Berhasil mengambil data semua product", products=products
    )


@product_router.get("/{product_id}", response_model=GetProductResponse)
async def get_product(product_id: int):
    product_db = await db.pool.fetchrow(
        "SELECT * FROM product WHERE id = $1", product_id
    )

    if not product_db:
        raise HTTPException(404, f"Product dengan id {product_id} tidak ditemukan")

    product = Product(
        id=product_id,
        name=product_db["name"],
        price=product_db["price"],
        description=product_db["description"],
        img_url=product_db["img_url"],
    )

    return GetProductResponse(
        success=True, message="Berhasil mengambil data product", product=product
    )


@product_router.post("", response_model=Response)
async def add_product(name: str, price: int, description: str, img_url: str):
    await db.pool.execute(
        """
        INSERT INTO product
            (name, price, description, img_url)
        VALUES
            ($1, $2, $3, $4)
        """,
        name,
        price,
        description,
        img_url,
    )

    return Response(success=True, message="Berhasil menambahkan product baru")


@product_router.put("/{product_id}", response_model=Response)
async def update_product(
    product_id: int,
    name: Optional[str] = None,
    price: Optional[int] = None,
    description: Optional[str] = None,
    img_url: Optional[str] = None,
):
    product_db = await db.pool.fetchrow(
        "SELECT * FROM product WHERE id = $1", product_id
    )

    if not product_db:
        raise HTTPException(404, f"Product dengan id {product_id} tidak ditemukan")

    await db.pool.execute(
        """
        UPDATE product SET 
            name = COALESCE($1, name), 
            price = COALESCE($2, price), 
            description = COALESCE($3, description), 
            img_url = COALESCE($4, img_url) 
        WHERE id = $5
        """,
        name,
        price,
        description,
        img_url,
        product_id,
    )

    return Response(
        success=True, message=f"Berhasil menyunting product {product_id}"
    )


@product_router.delete("/{product_id}", response_model=Response)
async def delete_product(product_id: int):
    product_db = await db.pool.fetchrow(
        "SELECT * FROM product WHERE id = $1", product_id
    )

    if not product_db:
        raise HTTPException(404, f"Product dengan id {product_id} tidak ditemukan")

    await db.pool.execute("DELETE FROM product WHERE id = $1", product_id)

    return Response(success=True, message=f"Berhasil menghapus product {product_id}")
