from fastapi import APIRouter

import datetime as dt

from model import Response, GetAllAspirationResponse, Aspiration, Student
from util import db

aspiration_router = APIRouter(prefix="/aspiration", tags=["Aspiration"])


@aspiration_router.get("", response_model=GetAllAspirationResponse)
async def get_all_aspirations():
    aspirations_db = await db.pool.fetch(
        "SELECT * FROM aspiration asp LEFT JOIN mahasiswa ma ON asp.mahasiswa_nim = ma.nim ORDER BY asp.id"
    )

    aspirations = []
    for aspiration in aspirations_db:
        student = Student(
            nim=aspiration["nim"],
            name=aspiration["name"],
            tel=aspiration["tel"],
            email=aspiration["email"],
            pass_hash=aspiration["pass_hash"],
        )
        aspirations.append(
            Aspiration(
                id=aspiration["id"],
                mahasiswa=student,
                post_date=aspiration["post_date"],
                title=aspiration["title"],
                content=aspiration["content"],
            )
        )

    return GetAllAspirationResponse(
        success=True,
        message="Berhasil mengambil data semua aspirasi",
        aspirations=aspirations,
    )


@aspiration_router.post("", response_model=Response)
async def add_aspiration(mahasiswa_nim: int, title: str, content: str):
    post_date = dt.datetime.now()

    student = await db.pool.fetchrow(
        "SELECT * FROM mahasiswa WHERE nim = $1", mahasiswa_nim
    )
    if not student:
        return Response(
            success=False,
            message=f"Mahasiswa dengan nim {mahasiswa_nim} tidak ditemukan",
        )

    await db.pool.execute(
        "INSERT INTO aspiration(mahasiswa_nim, post_date, title, content) VALUES ($1, $2, $3, $4)",
        mahasiswa_nim,
        post_date,
        title,
        content,
        )

    return Response(success=True, message="Berhasil menambahkan aspirasi baru")
