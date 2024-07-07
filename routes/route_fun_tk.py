from fastapi import APIRouter, HTTPException
from asyncpg.exceptions import ForeignKeyViolationError

from typing import Optional
import datetime as dt

from util import db
from model import Response, Admin, FunTK, GetAllFunTKResponse, GetFunTKResponse

fun_tk_router = APIRouter(prefix="/fun_tk", tags=["Fun TK"])


@fun_tk_router.get("", response_model=GetAllFunTKResponse)
async def get_all_fun_tk():
    fun_tks_db = await db.pool.fetch('SELECT * FROM fun_tk order by "date" DESC')

    fun_tks = []
    for fun_tk in fun_tks_db:
        fun_tks.append(
            FunTK(
                id=fun_tk["id"],
                title=fun_tk["title"],
                description=fun_tk["description"],
                post_date=fun_tk["post_date"],
                img_url=fun_tk["img_url"],
                date=fun_tk["date"],
                time=fun_tk["time"],
                location=fun_tk["location"],
                map_url=fun_tk["map_url"],
            )
        )

    return GetAllFunTKResponse(
        success=True, message="Berhasil mengambil data semua fun tks", fun_tks=fun_tks
    )


@fun_tk_router.get("/{fun_tk_id}", response_model=GetFunTKResponse)
async def get_fun_tk(fun_tk_id: int):
    fun_tk = await db.pool.fetchrow("SELECT * FROM fun_tk WHERE id = $1", fun_tk_id)

    if not fun_tk:
        raise HTTPException(404, f"Fun TK dengan id {fun_tk_id} tidak ditemukan")

    fun_tk_obj = FunTK(
        id=fun_tk["id"],
        title=fun_tk["title"],
        description=fun_tk["description"],
        post_date=fun_tk["post_date"],
        img_url=fun_tk["img_url"],
        date=fun_tk["date"],
        time=fun_tk["time"],
        location=fun_tk["location"],
        map_url=fun_tk["map_url"],
    )

    return GetFunTKResponse(
        success=True, message="Berhasil mengambil data fun tk", fun_tk=fun_tk_obj
    )


@fun_tk_router.post("", response_model=Response)
async def add_fun_tk(
    post_date: dt.datetime,
    title: str,
    description: str,
    img_url: str,
    date: dt.date,
    time: dt.time,
    location: str,
    map_url: Optional[str] = None,
):
    await db.pool.execute(
        "INSERT INTO fun_tk(post_date, title, description, img_url, date, time, location, map_url) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)",
        post_date,
        title,
        description,
        img_url,
        date,
        time,
        location,
        map_url,
    )

    return Response(success=True, message="Berhasil menambahkan fun tk baru")


@fun_tk_router.put("/{fun_tk_id}", response_model=Response)
async def update_fun_tk(
    fun_tk_id: int,
    title: Optional[str] = None,
    description: Optional[str] = None,
    img_url: Optional[str] = None,
    date: Optional[dt.date] = None,
    time: Optional[dt.time] = None,
    location: Optional[str] = None,
    map_url: Optional[str] = None,
):
    fun_tk = await db.pool.fetchrow("SELECT * FROM fun_tk WHERE id = $1", fun_tk_id)
    if not fun_tk:
        raise HTTPException(404, f"Fun TK dengan id {fun_tk_id} tidak ditemukan")

    await db.pool.execute(
        """
        UPDATE fun_tk 
        SET 
            img_url = COALESCE($1, img_url), 
            date = COALESCE($2, date), 
            time = COALESCE($3, time), 
            location = COALESCE($4, location), 
            map_url = COALESCE($5, map_url), 
            title = COALESCE($6, title), 
            description = COALESCE($7, description) 
        WHERE id = $8
        """,
        img_url,
        date,
        time,
        location,
        map_url,
        title,
        description,
        fun_tk_id,
    )

    return Response(success=True, message=f"Berhasil menyunting fun tk {fun_tk_id}")


@fun_tk_router.delete("/{fun_tk_id}", response_model=Response)
async def delete_fun_tk(fun_tk_id: int):
    fun_tk = await db.pool.fetchrow("SELECT * FROM fun_tk WHERE id = $1", fun_tk_id)
    if not fun_tk:
        raise HTTPException(404, f"Fun TK dengan id {fun_tk_id} tidak ditemukan")

    await db.pool.execute("DELETE FROM fun_tk WHERE id = $1", fun_tk_id)

    return Response(success=True, message=f"Berhasil menghapus fun tk {fun_tk_id}")
