from fastapi import APIRouter
from asyncpg.exceptions import ForeignKeyViolationError

from typing import Optional


from util import DBSession
from model import (
    Response,
    Comment,
    Admin,
    Student,
    GetAllCommentResponse,
    GetCommentResponse,
)


comment_router = APIRouter(prefix="/comments")
