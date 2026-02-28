from pydantic import BaseModel


class ErrorMessage(BaseModel):
    ok: bool = False
    error: str
