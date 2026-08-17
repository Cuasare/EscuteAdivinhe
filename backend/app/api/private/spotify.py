from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_active_refresh_token
from app.db.database import get_async_session
from app.models.refresh_token import RefreshToken
from app.services import spotify_serivce

router = APIRouter(prefix='/spotify', tags=["Spotify"])

@router.get("/playlists")
async def get_user_playlists(
        refresh_token: RefreshToken = Depends(get_active_refresh_token),
        db: AsyncSession = Depends(get_async_session),
):
    return await spotify_serivce.get_user_playlists(refresh_token, db)
