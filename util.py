import midtransclient
import smtplib
import asyncpg
import hashlib
import jwt
import os
from dotenv import load_dotenv

load_dotenv()


SECRET = os.getenv("SECRET")

from fastapi import Request
from fastapi.security import HTTPBearer
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.security.utils import get_authorization_scheme_param

bearer_scheme = HTTPBearer()
SECRET_KEY = os.getenv("SECRET_KEY")

snap_api = midtransclient.Snap(
    is_production=False,
    server_key=os.getenv("MIDTRANS_SERVER_KEY"),
    client_key=os.getenv("MIDTRANS_CLIENT_KEY")
)


class DBSession:
    def __init__(self):
        self.db = None

    async def __aenter__(self) -> asyncpg.Pool:
        self.db = await asyncpg.create_pool(
            host=os.getenv("DBHOST"),
            database=os.getenv("DBNAME"),
            user=os.getenv("DBUSER"),
            password=os.getenv("DBPASS"),
        )
        return self.db

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.db.close()


class MyHMTKMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, **options):
        self.fastapi_app = options["fastapi_app"]
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        if self.need_auth(request.url.path):
            authorization = request.headers.get("Authorization")
            scheme, credentials = get_authorization_scheme_param(authorization)

            if not (authorization and scheme and credentials):
                return JSONResponse(
                    status_code=403, content={"detail": "Not authenticated"}
                )
            if scheme.lower() != "bearer":
                return JSONResponse(
                    status_code=403,
                    content={"detail": "Invalid authentication credentials"},
                )

            if credentials != SECRET_KEY:
                return JSONResponse(
                    status_code=403,
                    content={"detail": "Invalid authentication credentials"},
                )

        return await call_next(request)

    def need_auth(self, path):
        if any(
            path.startswith(x) for x in ["/docs", "/openapi.json", "/reset_password"]
        ):
            return False
        else:
            return True


def hash_str(string):
    return hashlib.sha256(string.encode()).digest().decode("latin-1")


def encode_jwt(payload):
    return jwt.encode(payload, SECRET, algorithm="HS256")


# def generate_token()


def send_email(email, name, token):
    sender = "no_reply@mail.myhmtk.jeyy.xyz"
    receivers = [email]

    message = f"""From: No Reply <no_reply@mail.myhmtk.jeyy.xyz>
To: {name} <{email}>
Subject: MyHMTK - Reset Password

Open this link to reset your password (valid for 1 hour): 
https://myhmtk.jeyy.xyz/reset_password?token={token}


You can ignore this email if this isn't you.
"""

    try:
        smtpObj = smtplib.SMTP("localhost")
        smtpObj.sendmail(sender, receivers, message)
        print(f"Successfully sent email to {email}")
    except:
        print(f"Error: unable to send email to {email}")


async def create_transaction(payload):
    try:
        snap_url = snap_api.create_transaction_redirect_url(payload)
        return snap_url
    except Exception as e:
        print('midtrans error', e)
        raise HTTPException(status_code=500, detail=f"Midtrans Error: {e}")

