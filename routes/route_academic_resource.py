from fastapi import APIRouter
from asyncpg.exceptions import ForeignKeyViolationError

from typing import Optional

from util import DBSession
from model import (
    Response,
    Admin,
    AcademicResource,
    GetAllAcademicResourceResponse,
    GetAcademicResourceResponse,
)

academic_resource_router = APIRouter(
    prefix="/academic_resource", tags=["Academic Resource"]
)


@academic_resource_router.get("", response_model=GetAllAcademicResourceResponse)
async def get_all_academic_resource():
    async with DBSession() as db:
        academic_resources_db = await db.fetch(
            """
            SELECT
                ar.id,
                ar.title,
                ar.url,
                adm.id as admin_id,
                adm.name as admin_name, 
                adm.email as admin_email, 
                adm.pass_hash as admin_pass_hash
            FROM 
                academic_resource ar
            LEFT JOIN
                admin adm
            ON 
                ar.admin_id = adm.id
            """
        )

    academic_resources = []
    for academic_resource in academic_resources_db:
        admin = Admin(
            id=academic_resource["admin_id"],
            name=academic_resource["admin_name"],
            email=academic_resource["admin_email"],
            pass_hash=academic_resource["admin_pass_hash"],
        )

        academic_resources.append(
            AcademicResource(
                id=academic_resource["id"],
                admin=admin,
                title=academic_resource["title"],
                url=academic_resource["url"],
            )
        )

    return GetAllAcademicResourceResponse(
        success=True,
        message="Berhasil mengambil data semua academic resources",
        academic_resources=academic_resources,
    )


@academic_resource_router.get("/{admin_id}", response_model=GetAcademicResourceResponse)
async def get_academic_resource(admin_id: int):
    async with DBSession() as db:
        academic_resource = await db.fetchrow(
            """
            SELECT
                ar.id,
                ar.title,
                ar.url,
                adm.id as admin_id,
                adm.name as admin_name, 
                adm.email as admin_email, 
                adm.pass_hash as admin_pass_hash
            FROM 
                academic_resource ar
            LEFT JOIN
                admin adm
            ON 
                ar.admin_id = adm.id
            WHERE
                ar.id = $1
            """,
            admin_id,
        )

    if not academic_resource:
        return GetAcademicResourceResponse(
            success=False,
            message=f"Academic resource dengan id {admin_id} tidak ditemukan",
            academic_resource=None,
        )

    admin = Admin(
        id=academic_resource["admin_id"],
        name=academic_resource["admin_name"],
        email=academic_resource["admin_email"],
        pass_hash=academic_resource["admin_pass_hash"],
    )

    academic_resource_obj = AcademicResource(
        id=academic_resource["id"],
        admin=admin,
        title=academic_resource["title"],
        url=academic_resource["url"],
    )

    return GetAcademicResourceResponse(
        success=True,
        message="Berhasil mengambil data academic resource",
        academic_resource=academic_resource_obj,
    )


@academic_resource_router.post("", response_model=Response)
async def add_academic_resource(admin_id: int, title: str, url: str):
    async with DBSession() as db:
        try:
            await db.execute(
                "INSERT INTO academic_resource(admin_id, title, url) VALUES ($1, $2, $3)",
                admin_id,
                title,
                url,
            )
        except ForeignKeyViolationError:
            return Response(
                success=False, message=f"Admin dengan id {admin_id} tidak ditemukan"
            )

    return Response(success=True, message="Berhasil menambahkan academic resource baru")


@academic_resource_router.put("{admin_id}", response_model=Response)
async def update_academic_resource(
    admin_id: int, title: Optional[str] = None, url: Optional[str] = None
):
    async with DBSession() as db:
        academic_resorce = await db.fetchrow(
            "SELECT * FROM academic_resource WHERE id = $1", admin_id
        )
        if not academic_resorce:
            return Response(
                success=False,
                message=f"Academic resource dengan id {admin_id} tidak ditemukan",
            )

        await db.execute(
            "UPDATE academic_resource SET title = COALESCE($1, title), url = COALESCE($2, url) WHERE id = $3",
            title,
            url,
            admin_id,
        )

    return Response(success=True, message=f"Berhasil menyunting academic resource {admin_id}")


@academic_resource_router.delete("{admin_id}", response_model=Response)
async def delete_academic_resource(admin_id: int):
    async with DBSession() as db:
        academic_resource = await db.fetchrow(
            "SELECT * FROM academic_resource WHERE id = $1", admin_id
        )
        if not academic_resource:
            return Response(
                success=False,
                message=f"Academic resource dengan id {admin_id} tidak ditemukan",
            )

        await db.execute("DELETE FROM academic_resource WHERE id = $1", admin_id)

    return Response(success=True, message=f"Berhasil menghapus academic resource {admin_id}")
