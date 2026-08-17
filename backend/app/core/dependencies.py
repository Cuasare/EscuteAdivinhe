from datetime import datetime, timezone

from fastapi import Request
from fastapi.params import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.exceptions import HTTPException

from app.core.security import decodificar_token
from app.db.database import get_async_session
from app.models.User import User
from app.models.refresh_token import RefreshToken

bearer = HTTPBearer(auto_error=False)

async def get_current_user(
        request: Request,
        credentials: HTTPAuthorizationCredentials = Depends(bearer),
        db: AsyncSession = Depends(get_async_session)
) -> User:
    token = credentials.credentials if credentials else None

    if not token:
        token = request.cookies.get("access_token")

    if not token:
        raise HTTPException(401, "Não autenticado")

    payload = decodificar_token(token)
    if not payload:
        raise HTTPException(401, "Token inválido!")

    result = await db.execute(select(User).where(User.id == int(payload["sub"])))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(404, "Usuário não encontrado")

    return user

async def get_active_refresh_token(
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_async_session),
) -> RefreshToken:
    query = select(RefreshToken).where(
        RefreshToken.user_id == user.id,
        RefreshToken.is_revoked == False,
    ).order_by(RefreshToken.expires_at.desc())

    refresh_token = (await db.execute(query)).scalars().first()

    if not refresh_token:
        raise HTTPException(401, "Sessão inválida, faça login novamente")

    if datetime.now(timezone.utc) > refresh_token.expires_at:
        refresh_token.is_revoked = True
        await db.commit()
        raise HTTPException(401, "Sessão expirada, faça login novamente")

    return refresh_token