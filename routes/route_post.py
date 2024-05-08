from fastapi import APIRouter

from typing import Literal, Optional
import datetime as dt

from util import DBSession
from model import (
    Response,
    Post,
    Admin,
    Student,
    Comment,
    GetAllCommentResponse,
    GetCommentResponse,
    GetAllPostResponse,
    GetPostResponse,
)

post_router = APIRouter(prefix="/post", tags=["Post"])


@post_router.get("", response_model=GetAllPostResponse)
async def get_all_posts():
    async with DBSession() as db:
        posts_db = await db.fetch(
            """
            SELECT 
                post.id, 
                post.poster_id, 
                post.poster_type,
                post.post_date,
                post.img_url,
                post.content,
                post.can_comment,
                mahasiswa.name AS mahasiswa_name,
                mahasiswa.tel AS mahasiswa_tel,
                mahasiswa.email AS mahasiswa_email,
                mahasiswa.pass_hash AS mahasiswa_pass_hash
            FROM post
            LEFT JOIN mahasiswa ON post.poster_id = mahasiswa.nim AND post.poster_type = 'mahasiswa';
        """
        )

    posts = []
    for post in posts_db:
        poster = Student(
            nim=post["poster_id"],
            name=post["mahasiswa_name"],
            tel=post["mahasiswa_tel"],
            email=post["mahasiswa_email"],
            pass_hash=post["mahasiswa_pass_hash"],
        )

        posts.append(
            Post(
                id=post["id"],
                poster_type=post["poster_type"],
                poster=poster,
                post_date=post["post_date"],
                img_url=post["img_url"],
                content=post["content"],
                can_comment=post["can_comment"],
            )
        )

    return GetAllPostResponse(
        success=True, message="Berhasil mengambil data semua post", posts=posts
    )


@post_router.get("/{post_id}", response_model=GetPostResponse)
async def get_post(post_id: int):
    async with DBSession() as db:
        post = await db.fetchrow(
            """
            SELECT 
                post.id, 
                post.poster_id, 
                post.poster_type,
                post.post_date,
                post.img_url,
                post.content,
                post.can_comment,
                admin.name AS admin_name,
                admin.email AS admin_email,
                admin.pass_hash AS admin_pass_hash,
                mahasiswa.name AS mahasiswa_name,
                mahasiswa.tel AS mahasiswa_tel,
                mahasiswa.email AS mahasiswa_email,
                mahasiswa.pass_hash AS mahasiswa_pass_hash
            FROM post
            LEFT JOIN admin ON post.poster_id = admin.id AND post.poster_type = 'admin'
            LEFT JOIN mahasiswa ON post.poster_id = mahasiswa.nim AND post.poster_type = 'mahasiswa'
            
            WHERE post.id = $1
        """,
            post_id,
        )

    if not post:
        return GetPostResponse(
            success=False,
            message=f"Post dengan id {post_id} tidak ditemukan",
            post=None,
        )

    if post["poster_type"] == "admin":
        poster = Admin(
            id=post["poster_id"],
            name=post["admin_name"],
            email=post["admin_email"],
            pass_hash=post["admin_pass_hash"],
        )
    elif post["poster_type"] == "mahasiswa":
        poster = Student(
            nim=post["poster_id"],
            name=post["mahasiswa_name"],
            tel=post["mahasiswa_tel"],
            email=post["mahasiswa_email"],
            pass_hash=post["mahasiswa_pass_hash"],
        )

    post_obj = Post(
        id=post["id"],
        poster_type=post["poster_type"],
        poster=poster,
        post_date=post["post_date"],
        img_url=post["img_url"],
        content=post["content"],
        can_comment=post["can_comment"],
    )

    return GetPostResponse(
        success=True, message="Berhasil mengambil data post", post=post_obj
    )


@post_router.post("", response_model=Response)
async def add_post(
    poster_id: int,
    poster_type: Literal["admin", "mahasiswa"],
    post_date: dt.datetime,
    content: str,
    can_comment: bool,
    img_url: str = None,
):
    async with DBSession() as db:
        if poster_type == "admin":
            poster = await db.fetchrow("SELECT * FROM admin WHERE id = $1", poster_id)
            if not poster:
                return Response(
                    success=False,
                    message=f"Admin dengan id {poster_id} tidak ditemukan",
                )
        elif poster_type == "mahasiswa":
            poster = await db.fetchrow(
                "SELECT * FROM mahasiswa WHERE nim = $1", poster_id
            )
            if not poster:
                return Response(
                    success=False,
                    message=f"Mahasiswa dengan nim {poster_id} tidak ditemukan",
                )

        await db.execute(
            """
            INSERT INTO post 
                (poster_id, poster_type, post_date, img_url, content, can_comment) 
            VALUES 
                ($1, $2, $3, $4, $5, $6)
            """,
            poster_id,
            poster_type,
            post_date,
            img_url,
            content,
            can_comment,
        )

    return Response(success=True, message="Berhasil menambahkan post baru")


@post_router.put("/{post_id}", response_model=Response)
async def update_post(
    post_id: int,
    img_url: Optional[str] = None,
    content: Optional[str] = None,
    can_comment: Optional[bool] = None,
):
    async with DBSession() as db:
        post = await db.fetchrow("SELECT * FROM post WHERE id = $1", post_id)
        if not post:
            return Response(
                success=False, message=f"Post dengan id {post_id} tidak ditemukan"
            )

        await db.execute(
            "UPDATE post SET img_url = COALESCE($1, img_url), content = COALESCE($2, content), can_comment = COALESCE($3, can_comment) WHERE id = $4",
            img_url,
            content,
            can_comment,
            post_id,
        )

    return Response(success=True, message=f"Berhasil menyunting post {post_id}")


@post_router.delete("/{post_id}")
async def delete_post(post_id: int):
    async with DBSession() as db:
        post = await db.fetchrow("SELECT * FROM post WHERE id = $1", post_id)
        if not post:
            return Response(
                success=False, message=f"Post dengan id {post_id} tidak ditemukan"
            )

        await db.execute("DELETE FROM post WHERE id = $1", post_id)

    return Response(success=True, message=f"Berhasil menghapus post {post_id}")


# comment
@post_router.get("/{post_id}/comments")
async def get_all_post_comments(post_id: int):
    async with DBSession() as db:
        post = await db.fetchrow("SELECT * FROM post WHERE id = $1", post_id)
        if not post:
            return GetAllCommentResponse(
                success=False, message=f"Post dengan id {post_id} tidak ditemukan"
            )

        comments_db = await db.fetch(
            """
            SELECT 
                cm.id,
                cm.commenter_id,
                cm.commenter_type,
                cm.comment_date,
                cm.content,
                admin.name AS admin_name,
                admin.email AS admin_email,
                admin.pass_hash AS admin_pass_hash,
                mahasiswa.name AS mahasiswa_name,
                mahasiswa.tel AS mahasiswa_tel,
                mahasiswa.email AS mahasiswa_email,
                mahasiswa.pass_hash AS mahasiswa_pass_hash
            FROM 
                comment
            LEFT JOIN 
                admin 
            ON 
                cm.commenter_id = admin.id AND cm.commenter_type = 'admin'
            LEFT JOIN 
                mahasiswa 
            ON 
                comment.poster_id = mahasiswa.nim AND comment.poster_type = 'mahasiswa'
            WHERE 
                cm.post_id = $1
            """,
            post_id,
        )

    comments = []
    for comment in comments_db:
        comment = Comment(
            id=comment[""],
        )
