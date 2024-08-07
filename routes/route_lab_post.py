from fastapi import APIRouter, HTTPException
from asyncpg.exceptions import ForeignKeyViolationError

from typing import Literal, Optional
import datetime as dt

from util import db
from model import Response, Admin, LabPost, GetAllLabPostResponse, GetLabPostResponse


lab_post_router = APIRouter(prefix="/lab_post", tags=["Lab Post"])


@lab_post_router.get("", response_model=GetAllLabPostResponse)
async def get_all_lab_posts(lab: Optional[Literal["magics", "sea", "rnest", "security", "evconn", "ismile"]] = None):
    if not lab:
        lab_posts_db = await db.pool.fetch("SELECT * FROM lab_post ORDER BY post_date DESC")
    else:
        lab_posts_db = await db.pool.fetch("SELECT * FROM lab_post WHERE lab = $1 ORDER BY post_date DESC", lab)

    lab_posts = []
    for lab_post in lab_posts_db:
        lab_posts.append(
            LabPost(
                id=lab_post["id"],
                post_date=lab_post["post_date"],
                lab=lab_post["lab"],
                img_url=lab_post["img_url"],
                content=lab_post["content"],
            )
        )

    return GetAllLabPostResponse(
        success=True,
        message="Berhasil mengambil data semua lab posts",
        lab_posts=lab_posts,
    )


@lab_post_router.get("/{lab_post_id}", response_model=GetLabPostResponse)
async def get_lab_post(lab_post_id: int):
    lab_post = await db.pool.fetchrow("SELECT * FROM lab_post WHERE id = $1", lab_post_id)

    if not lab_post:
        raise HTTPException(404, f"Lab post dengan id {lab_post_id} tidak ditemukan")

    lab_post_obj = LabPost(
        id=lab_post["id"],
        post_date=lab_post["post_date"],
        lab=lab_post["lab"],
        img_url=lab_post["img_url"],
        content=lab_post["content"],
    )

    return GetLabPostResponse(
        success=True, message="Berhasil mengambil data lab post", lab_post=lab_post_obj
    )


@lab_post_router.post("", response_model=Response)
async def add_lab_post(
    post_date: dt.datetime,
    lab: Literal["magics", "sea", "rnest", "security", "evconn", "ismile"],
    content: str,
    img_url: Optional[str] = None,
):
    await db.pool.execute(
        "INSERT INTO lab_post(post_date, lab, content, img_url) VALUES ($1, $2, $3, $4)",
        post_date,
        lab,
        content,
        img_url,
    )

    return Response(success=True, message="Berhasil menambahkan lab post baru")


@lab_post_router.put("/{lab_post_id}", response_model=Response)
async def update_lab_post(
    lab_post_id: int, content: Optional[str] = None, img_url: Optional[str] = None
):
    lab_post = await db.pool.fetchrow(
        "SELECT * FROM lab_post WHERE id = $1", lab_post_id
    )
    if not lab_post:
        raise HTTPException(404, f"Lab post dengan id {lab_post_id} tidak ditemukan")

    await db.pool.execute(
        "UPDATE lab_post SET content = COALESCE($1, content), img_url = COALESCE($2, img_url) WHERE id = $3",
        content,
        img_url,
        lab_post_id,
    )

    return Response(success=True, message=f"Berhasil menyunting lab post {lab_post_id}")


@lab_post_router.delete("/{lab_post_id}", response_model=Response)
async def delete_lab_post(lab_post_id: int):
    lab_post = await db.pool.fetchrow(
        "SELECT * FROM lab_post WHERE id = $1", lab_post_id
    )
    if not lab_post:
        raise HTTPException(404, f"Lab post dengan id {lab_post_id} tidak ditemukan")

    await db.pool.execute("DELETE FROM lab_post WHERE id = $1", lab_post_id)

    return Response(success=True, message=f"Berhasil menghapus lab post {lab_post_id}")
