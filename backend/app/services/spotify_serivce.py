import httpx
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import RefreshToken
from app.services import auth_service


async def _spotify_request(
        method: str,
        url: str,
        refresh_token: RefreshToken,
        db: AsyncSession,
        max_try: int = 2,
) -> httpx.Response:
    access_token = refresh_token.spotify_access_token
    tentativa = 0

    while tentativa < max_try:
        async with httpx.AsyncClient() as client:
            response = await client.request(
                method,
                url,
                headers={"Authorization": f"Bearer {access_token}"},
            )

        if response.status_code != 401:
            return response

        access_token = await auth_service.refresh_spotify_token(refresh_token, db)
        tentativa += 1

    raise HTTPException(401, "Não foi possível autenticar com o Spotify")


async def get_user_playlists(
        refresh_token: RefreshToken,
        db: AsyncSession
) -> list[dict]:
    response = await _spotify_request(
        "GET",
        "https://api.spotify.com/v1/me/playlists",
        refresh_token,
        db,
    )

    if response.status_code != 200:
        raise HTTPException(400, "Falha ao buscar playlists do spotify")

    return response.json()["items"]
