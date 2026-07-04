from pydantic import BaseModel

class SpotifyCallbackQuery(BaseModel):
    error: str | None = None
    code: str
    state: str