from fastapi import APIRouter, Request, Form
from fastapi.templating import Jinja2Templates

from util import db, hash_str

import datetime as dt
import pytz

reset_pw_router = APIRouter(prefix="/reset_password", include_in_schema=False)
templates = Jinja2Templates("./templates")


@reset_pw_router.get("")
async def reset_pw_page(request: Request, token: str):
    token_data = await db.pool.fetchrow(
        "SELECT * FROM tokens LEFT JOIN mahasiswa ON tokens.mahasiswa_nim = mahasiswa.nim WHERE token = $1",
        token,
    )

    if not token_data:
        status = "Token is Invalid"
    elif token_data["exp"] < dt.datetime.now(pytz.timezone("Asia/Jakarta")).replace(tzinfo=None):
        await db.pool.execute("DELETE FROM tokens WHERE token = $1", token)

        status = "Token is Expired"
    else:
        status = "valid"
        token_data = dict(token_data)
        names = token_data["name"].split()
        token_data["name"] = " ".join(
            [name[:2] + "*" * (len(name) - 2) for name in names]
        )

    return templates.TemplateResponse(
        "reset_pw.html", {"request": request, "status": status, "data": token_data}
    )


@reset_pw_router.post("")
async def reset_pw_page(request: Request, token: str, password: str = Form(...)):
    token_data = await db.pool.fetchrow(
        "SELECT * FROM tokens LEFT JOIN mahasiswa ON tokens.mahasiswa_nim = mahasiswa.nim WHERE token = $1",
        token,
    )

    if not token_data:
        status = "Token is Invalid"
    elif token_data["exp"] < dt.datetime.now(pytz.timezone("Asia/Jakarta")).replace(tzinfo=None):
        await db.pool.execute("DELETE FROM tokens WHERE token = $1", token)

        status = "Token is Expired"
    else:
        await db.pool.execute(
            "DELETE FROM tokens WHERE token = $1 OR mahasiswa_nim = $2",
            token,
            token_data["nim"],
        )
        status = "Password changed"
        pass_hash = hash_str(password)

        await db.pool.execute(
            "UPDATE mahasiswa SET pass_hash = $1 WHERE nim = $2",
            pass_hash,
            token_data["nim"],
        )

    return templates.TemplateResponse(
        "reset_pw.html", {"request": request, "status": status, "data": None}, 303
    )
