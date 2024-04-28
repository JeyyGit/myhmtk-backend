from fastapi import APIRouter
from asyncpg.exceptions import ForeignKeyViolationError

from typing import Literal, Optional
import datetime as dt

from util import DBSession
from model import Response, Admin, LabPost, GetAllLabPostResponse, GetLabPostResponse


lab_post_router = APIRouter(prefix="/lab_post", tags=["Lab Post"])


@lab_post_router.get("", response_model=GetAllLabPostResponse)
async def get_all_lab_posts():
    async with DBSession() as db:
        lab_posts_db = await db.fetch(
            """
            SELECT 
                lp.id, 
                lp.admin_id, 
                lp.post_date, 
                lp.lab, 
                lp.img_url, 
                lp.content, 
                adm.name as admin_name, 
                adm.email as admin_email, 
                adm.pass_hash as admin_pass_hash
            FROM 
                lab_post lp 
            LEFT JOIN 
                admin adm 
            ON 
                lp.admin_id = adm.id
            """
        )

    lab_posts = []
    for lab_post in lab_posts_db:
        admin = Admin(
            id=lab_post["admin_id"],
            name=lab_post["admin_name"],
            email=lab_post["admin_email"],
            pass_hash=lab_post["admin_pass_hash"],
        )
        lab_posts.append(
            LabPost(
                id=lab_post["id"],
                admin=admin,
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


@lab_post_router.get("/{admin_id}", response_model=GetLabPostResponse)
async def get_lab_post(admin_id: int):
    async with DBSession() as db:
        lab_post = await db.fetchrow(
            """
            SELECT 
                lp.id, 
                lp.admin_id, 
                lp.post_date, 
                lp.lab, 
                lp.img_url, 
                lp.content, 
                adm.name as admin_name, 
                adm.email as admin_email, 
                adm.pass_hash as admin_pass_hash
            FROM 
                lab_post lp 
            LEFT JOIN 
                admin adm 
            ON 
                lp.admin_id = adm.id
            WHERE
                lp.id = $1
            """,
            id,
        )

    if not lab_post:
        return GetLabPostResponse(
            success=False,
            message=f"Lab post dengan id {admin_id} tidak ditemukan",
            lab_post=None,
        )

    admin = Admin(
        id=lab_post["admin_id"],
        name=lab_post["admin_name"],
        email=lab_post["admin_email"],
        pass_hash=lab_post["admin_pass_hash"],
    )
    lab_post_obj = LabPost(
        id=lab_post["id"],
        admin=admin,
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
    admin_id: int,
    post_date: dt.datetime,
    lab: Literal["magics", "sea", "rnest", "security", "evconn"],
    content: str,
    img_url: Optional[str] = None,
):
    async with DBSession() as db:
        try:
            await db.execute(
                "INSERT INTO lab_post(admin_id, post_date, lab, content, img_url) VALUES ($1, $2, $3, $4 , $5)",
                admin_id,
                post_date,
                lab,
                content,
                img_url,
            )
        except ForeignKeyViolationError:
            return Response(
                success=False, message=f"Admin dengan id {admin_id} tidak ditemukan"
            )

    return Response(success=True, message="Berhasil menambahkan lab post baru")


@lab_post_router.put("/{admin_id}", response_model=Response)
async def update_lab_post(
    admin_id: int, content: Optional[str] = None, img_url: Optional[str] = None
):
    async with DBSession() as db:
        lab_post = await db.fetchrow("SELECT * FROM lab_post WHERE id = $1", admin_id)
        if not lab_post:
            return Response(
                success=False, message=f"Lab post dengan id {admin_id} tidak ditemukan"
            )

        await db.execute(
            "UPDATE lab_post SET content = COALESCE($1, content), img_url = COALESCE($2, content) WHERE id = $3",
            content,
            img_url,
            admin_id,
        )

    return Response(success=True, message=f"Berhasil menyunting lab post {admin_id}")


@lab_post_router.delete("/{id}")
async def delete_lab_post(admin_id: int):
    async with DBSession() as db:
        lab_post = await db.fetchrow("SELECT * FROM lab_post WHERE id = $1", admin_id)
        if not lab_post:
            return Response(
                success=False, message=f"Lab post dengan id {admin_id} tidak ditemukan"
            )

        await db.execute("DELETE FROM lab_post WHERE id = $1", admin_id)

    return Response(success=True, message=f"Berhasil menghapus lab post {admin_id}")
