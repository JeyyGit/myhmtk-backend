from fastapi import APIRouter
from asyncpg.exceptions import ForeignKeyViolationError

from typing import Optional
import datetime as dt

from util import DBSession
from model import Response, Admin, FunTK, GetAllFunTKResponse, GetFunTKResponse

fun_tk_router = APIRouter(prefix="/fun_tk", tags=["Fun TK"])


@fun_tk_router.get("", response_model=GetAllFunTKResponse)
async def get_all_fun_tk():
    async with DBSession() as db:
        fun_tks_db = await db.fetch(
            """
            SELECT 
                ftk.id, 
                ftk.post_date, 
                ftk.img_url, 
                ftk.date, 
                ftk.time, 
                ftk.location,
                ftk.map_url,
                adm.id as admin_id,
                adm.name as admin_name, 
                adm.email as admin_email, 
                adm.pass_hash as admin_pass_hash
            FROM 
                fun_tk ftk
            LEFT JOIN 
                admin adm
            ON 
                ftk.admin_id = adm.id
            """
        )

    fun_tks = []
    for fun_tk in fun_tks_db:
        admin = Admin(
            id=fun_tk["admin_id"],
            name=fun_tk["admin_name"],
            email=fun_tk["admin_email"],
            pass_hash=fun_tk["admin_pass_hash"],
        )

        fun_tks.append(
            FunTK(
                id=fun_tk["id"],
                admin=admin,
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


@fun_tk_router.get("/{admin_id}", response_model=GetFunTKResponse)
async def get_fun_tk(admin_id: int):
    async with DBSession() as db:
        fun_tk = await db.fetchrow(
            """
            SELECT 
                ftk.id, 
                ftk.post_date, 
                ftk.img_url, 
                ftk.date, 
                ftk.time, 
                ftk.location,
                ftk.map_url,
                adm.id as admin_id,
                adm.name as admin_name, 
                adm.email as admin_email, 
                adm.pass_hash as admin_pass_hash
            FROM 
                fun_tk ftk
            LEFT JOIN 
                admin adm
            ON 
                ftk.admin_id = adm.id
            WHERE
                ftk.id = $1
            """,
            admin_id,
        )

    if not fun_tk:
        return GetFunTKResponse(
            success=False, message=f"Fun TK dengan id {admin_id} tidak ditemukan", fun_tk=None
        )

    admin = Admin(
        id=fun_tk["admin_id"],
        name=fun_tk["admin_name"],
        email=fun_tk["admin_email"],
        pass_hash=fun_tk["admin_pass_hash"],
    )

    fun_tk_obj = FunTK(
        id=fun_tk["id"],
        admin=admin,
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
    admin_id: int,
    post_date: dt.datetime,
    img_url: str,
    date: dt.date,
    time: dt.time,
    location: str,
    map_url: Optional[str] = None,
):
    async with DBSession() as db:
        try:
            await db.execute(
                "INSERT INTO fun_tk(admin_id, post_date, img_url, date, time, location, map_url) VALUES ($1, $2, $3, $4, $5, $6, $7)",
                admin_id,
                post_date,
                img_url,
                date,
                time,
                location,
                map_url,
            )
        except ForeignKeyViolationError:
            return Response(
                success=False, message=f"Admin dengan id {admin_id} tidak ditemukan"
            )

    return Response(success=True, message="Berhasil menambahkan fun tk baru")


@fun_tk_router.put("/{admin_admin_id}")
async def update_fun_tk(
    admin_admin_id: int,
    img_url: Optional[str] = None,
    date: Optional[dt.date] = None,
    time: Optional[dt.time] = None,
    location: Optional[str] = None,
    map_url: Optional[str] = None,
):
    async with DBSession() as db:
        fun_tk = await db.fetchrow("SELECT * FROM fun_tk WHERE id = $1", admin_admin_id)
        if not fun_tk:
            return Response(
                success=False, message=f"Fun tk dengan id {admin_admin_id} tidak ditemukan"
            )

        await db.execute(
            "UPDATE fun_tk SET img_url = COALESCE($1, img_url), date = COALESCE($2, date), time = COALESCE($3, time), location = COALESCE($4, location), map_url = COALESCE($5, map_url) WHERE id = $6",
            img_url,
            date,
            time,
            location,
            map_url,
            admin_admin_id,
        )

    return Response(success=True, message=f"Berhasil menyunting fun tk {admin_admin_id}")


@fun_tk_router.delete("/{admin_id}")
async def delete_fun_tk(admin_id: int):
    async with DBSession() as db:
        fun_tk = await db.fetchrow("SELECT * FROM fun_tk WHERE id = $1", admin_id)
        if not fun_tk:
            return Response(
                success=False, message=f"Fun tk dengan id {admin_id} tidak ditemukan"
            )
        
        await db.execute("DELETE FROM fun_tk WHERE id = $1", admin_id)

    return Response(success=True, message=f"Berhasil menghapus fun tk {admin_id}")