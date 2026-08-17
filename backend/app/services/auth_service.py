import base64
import secrets
from dataclasses import dataclass
from datetime import datetime, timezone, timedelta

import httpx
from urllib.parse import urlencode

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import RedirectResponse

from app.core.security import gerar_refresh_token, gerar_access_token
from app.core.settings import settings
from app.models import User, RefreshToken
from app.schemas.auth_schema import SpotifyCallbackQuery

SCOPES = " ".join([
    "user-read-private",
    "user-read-email",
    "playlist-read-private"
])

@dataclass
class LoginResponse:
    access_token: str
    refresh_token: str
    max_age_rt: int

async def _get_spotify_user_data(access_token):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://api.spotify.com/v1/me",
            headers={
                "authorization": f"Bearer {access_token}"
            }
        )

    return response.json()

async def login():

    state = secrets.token_hex(16)

    params = urlencode({
        "response_type": "code",
        "client_id": settings.SPOTIFY_CLIENT_ID,
        "scope": SCOPES,
        "redirect_uri": settings.SPOTIFY_REDIRECT_URI,
        "state": state
    })

    return RedirectResponse(f"https://accounts.spotify.com/authorize?{params}")

async def callback(
    params: SpotifyCallbackQuery,
    db: AsyncSession
):
    if params.error:
        raise HTTPException(400, f"Erro de autenticação do spotify: {params.error}")

    credentials = f"{settings.SPOTIFY_CLIENT_ID}:{settings.SPOTIFY_CLIENT_SECRET}"
    enconded = base64.b64encode(credentials.encode()).decode()

    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://accounts.spotify.com/api/token",
            headers={
                "Authorization": f"Basic {enconded}",
                "Content-Type": "application/x-www-form-urlencoded"
            },
            data={
                "grant_type": "authorization_code",
                "code": params.code,
                "redirect_uri": settings.SPOTIFY_REDIRECT_URI,
            },
        )

    if response.status_code != 200:
        raise HTTPException(400, "Falha em obter token de acesso do spotify")

    response_json = response.json()

    spotify_user_data = await _get_spotify_user_data(response_json["access_token"])

    refresh_token = gerar_refresh_token()

    existing_user = await db.scalar(
        select(User).where(User.spotify_id == spotify_user_data["id"])
    )

    if existing_user:
        user = existing_user
        user.username = spotify_user_data["display_name"]
        user.email = spotify_user_data["email"]
    else:
        user = User(
            spotify_id=spotify_user_data["id"],
            username=spotify_user_data["display_name"],
            email=spotify_user_data["email"],
        )
        db.add(user)

    await db.flush()

    access_token = gerar_access_token(user.id, user.email)

    refresh_token_entity = RefreshToken(
        user_id=user.id,
        user_token=refresh_token,
        spotify_token=response_json["refresh_token"],
        spotify_access_token=response_json["access_token"],
        spotify_expires_at=datetime.now(timezone.utc) + timedelta(seconds=response_json["expires_in"]),
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_EXPIRE_MINUTES),
        is_revoked=False,
        remember_me=True,
    )

    db.add(refresh_token_entity)
    await db.commit()

    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        max_age_rt=settings.REFRESH_TOKEN_EXPIRE_MINUTES
    )
async def refresh_spotify_token(
        refresh_token: RefreshToken,
        db: AsyncSession,
) -> str:
    credentials = f"{settings.SPOTIFY_CLIENT_ID}:{settings.SPOTIFY_CLIENT_SECRET}"
    encoded = base64.b64encode(credentials.encode()).decode()

    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://accounts.spotify.com/api/token",
            headers={
                "Authorization": f"Basic {encoded}",
                "Content-type": "application/x-www-form-urlencoded"
            },
            data={
                "grant_type": "refresh_token",
                "refresh_token": refresh_token.spotify_token,
            },
        )

    if response.status_code != 200:
        raise HTTPException(400, "Falha ao renovar token do spotify!")

    response_json = response.json()

    refresh_token.spotify_access_token = response_json["access_token"]
    refresh_token.spotify_expires_at = (datetime.now(timezone.utc) + timedelta(seconds=response_json["expires_in"]))

    if "refresh_token" in response_json:
        refresh_token.spotify_token = response_json["refresh_token"]

    await db.commit()

    return response_json["access_token"]