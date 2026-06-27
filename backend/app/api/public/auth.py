from fastapi import APIRouter

from app.schemas.auth_schema import CallBackResponse
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["auth"])

@router.get("/login")
async def login():
    return await auth_service.login()

@router.get("/callback")
async def callback(
        body: CallBackResponse
)