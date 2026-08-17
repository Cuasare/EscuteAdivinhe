from fastapi import FastAPI

from app.api.public.auth import router as auth_router
from app.api.private.spotify import router as spotify_router

app = FastAPI(docs_url="/docs")
app.include_router(auth_router, prefix="/api", tags=["Authentication"])
app.include_router(spotify_router, prefix="/api", tags=["Spotify"])