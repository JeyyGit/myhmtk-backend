from fastapi import APIRouter, Request

from model import Student, Admin, Auth, AuthResponse, Response
from util import db, hash_str, send_email

import datetime as dt
import secrets
import pytz


auth_router = APIRouter(prefix="/auth", tags=["Auth"])


# @auth_router.get("")
# async def authh(): ...


@auth_router.api_route("/login", methods=["POST", "OPTIONS"])
async def login(request: Request, email: str, password: str):
    pass_hash = hash_str(password)
    user = await db.pool.fetchrow(
        "SELECT * FROM mahasiswa WHERE email = $1 AND pass_hash = $2",
        email,
        pass_hash,
    )

    if not user:
        user = await db.pool.fetchrow(
            "SELECT * FROM admin WHERE email = $1 AND pass_hash = $2",
            email,
            pass_hash,
        )

        if not user:
            return AuthResponse(
                success=False, message="Username atau password salah", auth=None
            )
        else:
            user_type = "admin"
            user_obj = Admin(**user)
    else:
        user_type = "mahasiswa"
        user_obj = Student(**user)

    auth = Auth(user_type=user_type, user=user_obj)
    # payload = {
    #     'user_type': user_type,
    #     'user': user_obj.dict()
    # }
    # jwt_str = encode_jwt(payload)
    return AuthResponse(success=True, message="Login berhasil", auth=auth)


@auth_router.post("/reset_password")
async def reset_password(request: Request, email: str):
    student = await db.pool.fetchrow("SELECT * FROM mahasiswa WHERE email = $1", email)
    if not student:
        return Response(
            success=False, message=f"Mahasiswa dengan email {email} tidak ditemukan"
        )

    token = secrets.token_urlsafe(32)
    send_email(email, student["name"], token)

    exp = dt.datetime.now(pytz.timezone("Asia/Jakarta")) + dt.timedelta(hours=1)

    await db.pool.execute(
        "INSERT INTO tokens (mahasiswa_nim, exp, token) VALUES ($1, $2, $3)",
        student["nim"],
        exp,
        token,
    )

    return Response(success=True, message="Email reset password terkirim")
