from fastapi import APIRouter, HTTPException

from typing import Literal, Optional
import datetime as dt

from util import db
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
async def get_all_posts(user_id: Optional[int] = None):
    if user_id is None:
        posts_db = await db.pool.fetch(
            """
            SELECT 
                post.id, 
                post.poster_id, 
                post.post_date,
                post.img_url,
                post.content,
                post.can_comment,
                mahasiswa.name AS mahasiswa_name,
                mahasiswa.tel AS mahasiswa_tel,
                mahasiswa.email AS mahasiswa_email,
                mahasiswa.avatar_url AS mahasiswa_avatar_url,
                mahasiswa.address AS mahasiswa_address,
                mahasiswa.pass_hash AS mahasiswa_pass_hash,
                COUNT(DISTINCT l.liker_id) AS current_like_count
            FROM post
            LEFT JOIN mahasiswa ON post.poster_id = mahasiswa.nim
            LEFT JOIN "like" l ON post.id = l.post_id
            GROUP BY
                post.id,
                mahasiswa.name,
                mahasiswa.tel,
                mahasiswa.email,
                mahasiswa.avatar_url,
                mahasiswa.address,
                mahasiswa.pass_hash
            ORDER BY post.post_date DESC
        """
        )
    else:
        posts_db = await db.pool.fetch(
            """
            SELECT 
                post.id, 
                post.poster_id, 
                post.post_date,
                post.img_url,
                post.content,
                post.can_comment,
                mahasiswa.name AS mahasiswa_name,
                mahasiswa.tel AS mahasiswa_tel,
                mahasiswa.email AS mahasiswa_email,
                mahasiswa.avatar_url AS mahasiswa_avatar_url,
                mahasiswa.address AS mahasiswa_address,
                mahasiswa.pass_hash AS mahasiswa_pass_hash,
                COUNT(l.liker_id) AS current_like_count,
                EXISTS (
                    SELECT 1
                    FROM "like"
                    WHERE "like".post_id = post.id AND "like".liker_id = $1
                ) AS is_liked
            FROM post
            LEFT JOIN mahasiswa ON post.poster_id = mahasiswa.nim
            LEFT JOIN "like" l ON post.id = l.post_id
            GROUP BY
                post.id,
                mahasiswa.name,
                mahasiswa.tel,
                mahasiswa.email,
                mahasiswa.avatar_url,
                mahasiswa.address,
                mahasiswa.pass_hash
            ORDER BY post.post_date DESC
        """,
            user_id,
        )

    posts = []
    for post in posts_db:
        poster = Student(
            nim=post["poster_id"],
            name=post["mahasiswa_name"],
            tel=post["mahasiswa_tel"],
            email=post["mahasiswa_email"],
            avatar_url=post["mahasiswa_avatar_url"],
            address=post["mahasiswa_address"],
            pass_hash=post["mahasiswa_pass_hash"],
        )

        if user_id is None:
            posts.append(
                Post(
                    id=post["id"],
                    poster=poster,
                    post_date=post["post_date"],
                    img_url=post["img_url"],
                    content=post["content"],
                    current_like_count=post["current_like_count"],
                    can_comment=post["can_comment"],
                )
            )
        else:
            posts.append(
                Post(
                    id=post["id"],
                    poster=poster,
                    post_date=post["post_date"],
                    img_url=post["img_url"],
                    content=post["content"],
                    current_like_count=post["current_like_count"],
                    can_comment=post["can_comment"],
                    is_liked=post["is_liked"],
                )
            )

    return GetAllPostResponse(
        success=True, message="Berhasil mengambil data semua post", posts=posts
    )


@post_router.get("/{post_id}", response_model=GetPostResponse)
async def get_post(post_id: int, user_id: Optional[int] = None):
    if user_id is None:
        post = await db.pool.fetchrow(
            """
            SELECT 
                post.id, 
                post.poster_id, 
                post.post_date,
                post.img_url,
                post.content,
                post.can_comment,
                mahasiswa.name AS mahasiswa_name,
                mahasiswa.tel AS mahasiswa_tel,
                mahasiswa.email AS mahasiswa_email,
                mahasiswa.avatar_url AS mahasiswa_avatar_url,
                mahasiswa.address AS mahasiswa_address,
                mahasiswa.pass_hash AS mahasiswa_pass_hash,
                COUNT("like".liker_id) AS current_like_count
            FROM post
            LEFT JOIN mahasiswa ON post.poster_id = mahasiswa.nim
            LEFT JOIN "like" ON post.id = "like".post_id
            WHERE post.id = $1
            GROUP BY
                post.id,
                mahasiswa.name,
                mahasiswa.tel,
                mahasiswa.email,
                mahasiswa.avatar_url,
                mahasiswa.address,
                mahasiswa.pass_hash
            ORDER BY post.post_date DESC
        """,
            post_id,
        )
    else:
        post = await db.pool.fetchrow(
            """
            SELECT 
                post.id, 
                post.poster_id, 
                post.post_date,
                post.img_url,
                post.content,
                post.can_comment,
                mahasiswa.name AS mahasiswa_name,
                mahasiswa.tel AS mahasiswa_tel,
                mahasiswa.email AS mahasiswa_email,
                mahasiswa.avatar_url AS mahasiswa_avatar_url,
                mahasiswa.address AS mahasiswa_address,
                mahasiswa.pass_hash AS mahasiswa_pass_hash,
                COUNT("like".liker_id) AS current_like_count,
                EXISTS (
                    SELECT 1
                    FROM "like"
                    WHERE "like".post_id = post.id AND "like".liker_id = $1
                ) AS is_liked
            FROM post
            LEFT JOIN mahasiswa ON post.poster_id = mahasiswa.nim
            LEFT JOIN "like" ON post.id = "like".post_id
            WHERE post.id = $2
            GROUP BY
                post.id,
                mahasiswa.name,
                mahasiswa.tel,
                mahasiswa.email,
                mahasiswa.avatar_url,
                mahasiswa.address,
                mahasiswa.pass_hash
            ORDER BY post.post_date DESC
        """,
            user_id,
            post_id,
        )

    if not post:
        raise HTTPException(404, f"Post dengan id {post_id} tidak ditemukan")

    poster = Student(
        nim=post["poster_id"],
        name=post["mahasiswa_name"],
        tel=post["mahasiswa_tel"],
        email=post["mahasiswa_email"],
        avatar_url=post["mahasiswa_avatar_url"],
        address=post["mahasiswa_address"],
        pass_hash=post["mahasiswa_pass_hash"],
    )

    if user_id is None:
        post_obj = Post(
            id=post["id"],
            poster=poster,
            post_date=post["post_date"],
            img_url=post["img_url"],
            content=post["content"],
            current_like_count=post["current_like_count"],
            can_comment=post["can_comment"],
        )
    else:
        post_obj = Post(
            id=post["id"],
            poster=poster,
            post_date=post["post_date"],
            img_url=post["img_url"],
            content=post["content"],
            current_like_count=post["current_like_count"],
            can_comment=post["can_comment"],
            is_liked=post["is_liked"],
        )

    return GetPostResponse(
        success=True, message="Berhasil mengambil data post", post=post_obj
    )


@post_router.post("", response_model=Response)
async def add_post(
    poster_id: int,
    post_date: dt.datetime,
    content: str,
    can_comment: bool,
    img_url: str = None,
):
    poster = await db.pool.fetchrow("SELECT * FROM mahasiswa WHERE nim = $1", poster_id)
    if not poster:
        raise HTTPException(404, f"Mahasiswa dengan nim {poster_id} tidak ditemukan")

    await db.pool.execute(
        """
        INSERT INTO post 
            (poster_id, post_date, img_url, content, can_comment) 
        VALUES 
            ($1, $2, $3, $4, $5)
        """,
        poster_id,
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
    post = await db.pool.fetchrow("SELECT * FROM post WHERE id = $1", post_id)
    if not post:
        raise HTTPException(404, f"Post dengan id {post_id} tidak ditemukan")

    await db.pool.execute(
        "UPDATE post SET img_url = COALESCE($1, img_url), content = COALESCE($2, content), can_comment = COALESCE($3, can_comment) WHERE id = $4",
        img_url,
        content,
        can_comment,
        post_id,
    )

    return Response(success=True, message=f"Berhasil menyunting post {post_id}")


@post_router.delete("/{post_id}", response_model=Response)
async def delete_post(post_id: int):
    post = await db.pool.fetchrow("SELECT * FROM post WHERE id = $1", post_id)
    if not post:
        raise HTTPException(404, f"Post dengan id {post_id} tidak ditemukan")

    await db.pool.execute("DELETE FROM post WHERE id = $1", post_id)

    return Response(success=True, message=f"Berhasil menghapus post {post_id}")


# likes
@post_router.post("/{post_id}/like", response_model=Response)
async def toggle_post_like(post_id: int, user_id: int):
    post = await db.pool.fetchrow("SELECT * FROM post WHERE id = $1", post_id)
    if not post:
        raise HTTPException(404, f"Post dengan id {post_id} tidak ditemukan")
    
    user = await db.pool.fetchrow("SELECT * FROM mahasiswa WHERE nim = $1", user_id)
    if not user:
        raise HTTPException(404, f"Mahasiswa dengan nim {user_id} tidak ditemukan")

    like_exists = await db.pool.fetchval(
        'SELECT 1 FROM "like" WHERE post_id = $1 AND liker_id = $2', post_id, user_id
    )
    if like_exists:
        await db.pool.execute(
            'DELETE FROM "like" WHERE post_id = $1 AND liker_id = $2', post_id, user_id
        )
    else:
        await db.pool.execute(
            'INSERT INTO "like" (post_id, liker_id) VALUES ($1, $2)', post_id, user_id
        )

    return Response(success=True, message="Berhasil menambahkan like baru")


# comment
@post_router.get("/{post_id}/comment", response_model=GetAllCommentResponse)
async def get_all_post_comments(post_id: int):
    post = await db.pool.fetchrow("SELECT * FROM post WHERE id = $1", post_id)
    if not post:
        raise HTTPException(404, f"Post dengan id {post_id} tidak ditemukan")

    comments_db = await db.pool.fetch(
        """
        SELECT
            cm.id,
            cm.comment_date,
            cm.content,
            cm.post_id,
            m.nim AS student_nim, 
            m.name AS student_name, 
            m.tel AS student_tel, 
            m.email AS student_email, 
            m.avatar_url AS student_avatar_url, 
            m.address AS student_address, 
            m.pass_hash AS student_pass_hash 
        FROM comment cm
        LEFT JOIN mahasiswa m
        ON cm.commenter_id = m.nim
        WHERE cm.post_id = $1
        ORDER BY cm.post_id
        """,
        post_id,
    )

    comments = []
    for cm in comments_db:
        student = Student(
            nim=cm["student_nim"],
            name=cm["student_name"],
            tel=cm["student_tel"],
            email=cm["student_email"],
            avatar_url=cm["student_avatar_url"],
            address=cm["student_address"],
            pass_hash=cm["student_pass_hash"],
        )
        comments.append(
            Comment(
                id=cm["id"],
                post_id=cm["post_id"],
                commenter=student,
                comment_date=cm["comment_date"],
                content=cm["content"],
            )
        )

    return GetAllCommentResponse(
        success=True, message="Berhasil mengambil data semua comment", comments=comments
    )


@post_router.post("/{post_id}/comment", response_model=Response)
async def add_comment(
    post_id: int, commenter_id: int, comment_date: dt.datetime, content: str
):
    post = await db.pool.fetchrow("SELECT * FROM post WHERE id = $1", post_id)
    if not post:
        raise HTTPException(404, f"Post dengan id {post_id} tidak ditemukan")

    await db.pool.execute(
        "INSERT INTO comment (post_id, commenter_id, comment_date, content) VALUES ($1, $2, $3, $4)",
        post_id,
        commenter_id,
        comment_date,
        content,
    )

    return Response(success=True, message="Berhasil menambahkan comment baru")


@post_router.delete("/{post_id}/comment/{comment_id}", response_model=Response)
async def delete_comment(post_id: int, comment_id: int):
    post = await db.pool.fetchrow("SELECT * FROM post WHERE id = $1", post_id)
    if not post:
        raise HTTPException(404, f"Post dengan id {post_id} tidak ditemukan")
    
    comment = await db.pool.fetchrow("SELECT * FROM comment WHERE id = $1", comment_id)
    if not comment:
        
        raise HTTPException(404, f"Comment dengan id {comment_id} tidak ditemuka")
    
    await db.pool.execute("DELETE FROM comment WHERE id = $1", comment_id)

    return Response(success=True, message="Berhasil menghapus comment")
    
