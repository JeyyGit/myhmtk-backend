from fastapi import APIRouter

from typing import Optional

from util import DBSession, hash_str
from model import Response, GetAllAdminResponse, GetAdminResponse

admin_router = APIRouter(prefix="/admin", tags=["Admin"])


@admin_router.get("", response_model=GetAllAdminResponse)
async def get_all_admin():
    async with DBSession() as db:
        admins = await db.fetch("SELECT * FROM admin")

    return GetAllAdminResponse(
        success=True,
        message="Berhasil mengambil data semua mahasiswa",
        admins=admins,
    )


@admin_router.get("/{admin_id}", response_model=GetAdminResponse)
async def get_admin(admin_id: int):
    async with DBSession() as db:
        admin = await db.fetchrow("SELECT * FROM admin WHERE id = $1", admin_id)
        if not admin:
            return GetAdminResponse(
                success=False,
                message=f"Admin dengan id {admin_id} tidak ditemukan",
                admin=None,
            )

    return GetAdminResponse(
        success=True, message="Berhasil mengambil data admin", admin=admin
    )


@admin_router.post("", response_model=Response)
async def add_admin(name: str, email: str, password: str):
    pass_hash = hash_str(password)

    async with DBSession() as db:
        await db.execute(
            "INSERT INTO admin(name, email, pass_hash) VALUES ($1, $2, $3)",
            name,
            email,
            pass_hash,
        )

    return Response(success=True, message="Berhasil menambahkan admin baru")


@admin_router.put("/{admin_id}", response_model=Response)
async def update_admin(
    admin_id: int,
    name: Optional[str] = None,
    email: Optional[str] = None,
    password: Optional[str] = None,
):
    if password:
        pass_hash = hash_str(password)
    else:
        pass_hash = None

    async with DBSession() as db:
        student = await db.fetchrow("SELECT * FROM admin WHERE id = $1", admin_id)
        if not student:
            return Response(
                success=False, message=f"Admin dengan id {admin_id} tidak ditemukan"
            )

        await db.execute(
            "UPDATE admin SET name = COALESCE($1, name), email = COALESCE($2, email), pass_hash = COALESCE($3, pass_hash) WHERE id = $4",
            name,
            email,
            pass_hash,
            admin_id,
        )

    return Response(success=True, message=f"Berhasil menyunting admin {admin_id}")


@admin_router.delete("/{admin_id}", response_model=Response)
async def delete_admin(admin_id: int):
    async with DBSession() as db:
        admin = await db.fetchrow("SELECT * FROM admin WHERE id = $1", admin_id)
        if not admin:
            return Response(
                success=False, message=f"Admin dengan id {admin_id} tidak ditemukan"
            )

        await db.execute(
            "DELETE FROM post WHERE poster_id = $1 AND poster_type = $2", admin_id, "admin"
        )
        await db.execute("DELETE FROM admin WHERE id = $1", admin_id)

    return Response(success=True, message=f"Berhasil menghapus admin {admin_id}")
