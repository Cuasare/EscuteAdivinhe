from pydantic import BaseModel

class CallBackResponse(BaseModel):
    code: str | None = None
    error: str | None = None
    state: str