from fastapi import FastAPI

from app.api.public.auth import router as auth_router

app = FastAPI(docs_url="/docs")
app.include_router(auth_router, prefix="/api", tags=["Authentication"])