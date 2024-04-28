from fastapi import APIRouter
from asyncpg.exceptions import UniqueViolationError

from model import (
    Response,
    GetAllStudentResponse,
    GetStudentResponse,
)
from util import DBSession, hash_str
from typing import Optional


student_router = APIRouter(prefix="/student", tags=["Student"])


@student_router.get("", response_model=GetAllStudentResponse)
async def get_all_student():
    async with DBSession() as db:
        students = await db.fetch("SELECT * FROM mahasiswa")

    return GetAllStudentResponse(
        success=True,
        message="Berhasil mengambil data semua mahasiswa",
        mahasiswa=students,
    )


@student_router.get("/{nim}", response_model=GetStudentResponse)
async def get_student(nim: int):
    async with DBSession() as db:
        student = await db.fetchrow("SELECT * FROM mahasiswa WHERE nim = $1", nim)
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
async def add_student(nim: int, name: str, tel: int, email: str, password: str):
    pass_hash = hash_str(password)

    async with DBSession() as db:
        try:
            await db.execute(
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
    password: Optional[str] = None,
):
    if password:
        pass_hash = hash_str(password)
    else:
        pass_hash = None

    async with DBSession() as db:
        student = await db.fetchrow("SELECT * FROM mahasiswa WHERE nim = $1", nim)
        if not student:
            return Response(
                success=False, message=f"Mahasiswa dengan nim {nim} tidak ditemukan"
            )

        await db.execute(
            "UPDATE mahasiswa SET name = COALESCE($1, name), tel = COALESCE($2, tel), email = COALESCE($3, email), pass_hash = COALESCE($4, pass_hash) WHERE nim = $5",
            name,
            tel,
            email,
            pass_hash,
            nim,
        )

    return Response(success=True, message=f"Berhasil menyunting mahasiswa {nim}")


@student_router.delete("/{nim}", response_model=Response)
async def delete_student(nim: int):
    async with DBSession() as db:
        student = await db.fetchrow("SELECT * FROM mahasiswa WHERE nim = $1", nim)
        if not student:
            return Response(
                success=False, message=f"Mahasiswa dengan nim {nim} tidak ditemukan"
            )

        await db.execute(
            "DELETE FROM post WHERE poster_id = $1 AND poster_type = $2",
            nim,
            "mahasiswa",
        )
        await db.execute("DELETE FROM mahasiswa WHERE nim = $1", nim)

    return Response(success=True, message=f"Berhasil menghapus mahasiswa {nim}")
