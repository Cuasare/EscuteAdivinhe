from typing import Annotated

from fastapi import APIRouter, Depends, Response
from fastapi.params import Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.db.database import get_async_session
from app.models import User
from app.schemas.auth_schema import SpotifyCallbackQuery
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["auth"])

@router.get("/login")
async def login():
    return await auth_service.login()

@router.get("/callback")
async def callback(
    response: Response,
    params: Annotated[SpotifyCallbackQuery, Query()],
    db: AsyncSession = Depends(get_async_session)
):
    result = await auth_service.callback(params, db)

    response.set_cookie(
        key="access_token",
        value=result.access_token,
        samesite="lax",
        httponly=True,
        secure=False,
        max_age=result.max_age_rt,
        path="/",
        domain=None
    )

    response.set_cookie(
        key="refresh_token",
        value=result.refresh_token,
        samesite="lax",
        httponly=True,
        secure=False,
        max_age=result.max_age_rt,
        path="/",
        domain=None
    )

    return {"message": "Login bem sucedido! Redirecionando..."}
