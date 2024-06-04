from fastapi import APIRouter
from asyncpg.exceptions import UniqueViolationError

from model import (
    Response,
    GetAllStudentResponse,
    GetStudentResponse,
)
from util import db, hash_str
from typing import Optional


student_router = APIRouter(prefix="/student", tags=["Student"])


@student_router.get("", response_model=GetAllStudentResponse)
async def get_all_student():
    students = await db.pool.fetch("SELECT * FROM mahasiswa")

    return GetAllStudentResponse(
        success=True,
        message="Berhasil mengambil data semua mahasiswa",
        mahasiswa=students,
    )


@student_router.get("/{nim}", response_model=GetStudentResponse)
async def get_student(nim: int):
    student = await db.pool.fetchrow("SELECT * FROM mahasiswa WHERE nim = $1", nim)
    if not student:
        return GetStudentResponse(
            success=False,
            message=f"Mahasiswa dengan nim {nim} tidak ditemukan",
            mahasiswa=None,
        )

    return GetStudentResponse(
        success=True, message="Berhasil mengambil data mahasiswa", mahasiswa=student
    )


@student_router.post("", response_model=Response)
async def add_student(
    nim: int,
    name: str,
    tel: int,
    email: str,
    avatar_url: str,
    address: str,
    password: str,
):
    pass_hash = hash_str(password)
    try:
        await db.pool.execute(
            "INSERT INTO mahasiswa(nim, name, tel, email, pass_hash) VALUES ($1, $2, $3, $4, $5)",
            nim,
            name,
            tel,
            email,
            pass_hash,
        )
    except UniqueViolationError:
        return Response(
            success=False, message=f"Data mahasiswa dengan NIM {nim} sudah ada"
        )

    return Response(success=True, message="Berhasil menambahkan mahasiswa baru")


@student_router.put("/{nim}", response_model=Response)
async def update_student(
    nim: int,
    name: Optional[str] = None,
    tel: Optional[int] = None,
    email: Optional[str] = None,
    avatar_url: Optional[str] = None,
    address: Optional[str] = None,
    password: Optional[str] = None,
):
    if password:
        pass_hash = hash_str(password)
    else:
        pass_hash = None

    student = await db.pool.fetchrow("SELECT * FROM mahasiswa WHERE nim = $1", nim)
    if not student:
        return Response(
            success=False, message=f"Mahasiswa dengan nim {nim} tidak ditemukan"
        )

    await db.pool.execute(
        "UPDATE mahasiswa SET name = COALESCE($1, name), tel = COALESCE($2, tel), email = COALESCE($3, email), pass_hash = COALESCE($4, pass_hash), avatar_url = COALESCE($5, avatar_url), address = COALESCE($6, address) WHERE nim = $7",
        name,
        tel,
        email,
        pass_hash,
        avatar_url,
        address,
        nim,
    )

    return Response(success=True, message=f"Berhasil menyunting mahasiswa {nim}")


@student_router.delete("/{nim}", response_model=Response)
async def delete_student(nim: int):
    student = await db.pool.fetchrow("SELECT * FROM mahasiswa WHERE nim = $1", nim)
    if not student:
        return Response(
            success=False, message=f"Mahasiswa dengan nim {nim} tidak ditemukan"
        )

    await db.pool.execute(
        "DELETE FROM post WHERE poster_id = $1 AND poster_type = $2",
        nim,
        "mahasiswa",
    )
    await db.pool.execute("DELETE FROM mahasiswa WHERE nim = $1", nim)

    return Response(success=True, message=f"Berhasil menghapus mahasiswa {nim}")
