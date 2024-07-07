from fastapi import APIRouter, HTTPException
from asyncpg.exceptions import ForeignKeyViolationError

from typing import Optional
import datetime as dt

from util import db
from model import Response, Activity, GetAllActivitiesResponse, GetActivityResponse

activity_router = APIRouter(prefix="/activity", tags=["Activity"])


@activity_router.get("", response_model=GetAllActivitiesResponse)
async def get_all_activity():
    acitivity_db  = await db.pool.fetch("SELECT * FROM activity order by post_date")

    acitivities = []
    for activity in acitivity_db:
        acitivities.append(
            Activity(
                id=activity["id"],
                title=activity["title"],
                content=activity["content"],
                post_date=activity["post_date"],
                img_url=activity["img_url"],
            )
        )

    return GetAllActivitiesResponse(
        success=True, message="Berhasil mengambil data semua activities", activities=acitivities
    )


@activity_router.get("/{activity_id}", response_model=GetActivityResponse)
async def get_activity(activity_id: int):
    activity = await db.pool.fetchrow("SELECT * FROM activity WHERE id = $1", activity_id)

    if not activity:
        raise HTTPException(404, f"Activity dengan id {activity_id} tidak ditemukan")

    activity_obj = Activity(
        id=activity["id"],
        title=activity["title"],
        content=activity["content"],
        post_date=activity["post_date"],
        img_url=activity["img_url"],
    )

    return GetActivityResponse(
        success=True, message="Berhasil mengambil data activity", activity=activity_obj
    )


@activity_router.post("", response_model=Response)
async def add_activity(
    post_date: dt.datetime,
    title: str,
    content: str,
    img_url: str,
):
    await db.pool.execute(
        "INSERT INTO activity(post_date, title, content, img_url) VALUES ($1, $2, $3, $4)",
        post_date,
        title,
        content,
        img_url,
    )

    return Response(success=True, message="Berhasil menambahkan activity baru")


@activity_router.put("/{activity_id}", response_model=Response)
async def update_activity(
    activity_id: int,
    title: Optional[str] = None,
    content: Optional[str] = None,
    img_url: Optional[str] = None,
):
    activity = await db.pool.fetchrow("SELECT * FROM activity WHERE id = $1", activity_id)
    if not activity:
        raise HTTPException(404, f"Activity dengan id {activity_id} tidak ditemukan")

    await db.pool.execute(
        """
        UPDATE activity 
        SET 
            img_url = COALESCE($1, img_url), 
            title = COALESCE($2, title), 
            content = COALESCE($3, content) 
        WHERE id = $4
        """,
        img_url,
        title,
        content,
        activity_id,
    )

    return Response(success=True, message=f"Berhasil menyunting activity {activity_id}")


@activity_router.delete("/{activity_id}", response_model=Response)
async def delete_activity(activity_id: int):
    activity = await db.pool.fetchrow("SELECT * FROM activity WHERE id = $1", activity_id)
    if not activity:
        raise HTTPException(404, f"Activity dengan id {activity_id} tidak ditemukan")

    await db.pool.execute("DELETE FROM activity WHERE id = $1", activity_id)

    return Response(success=True, message=f"Berhasil menghapus activity {activity_id}")
