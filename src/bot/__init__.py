from pydantic import BaseModel, ConfigDict
from typing import Optional


class NotPrivateChat(ValueError):
    pass


class UnsuportedTextInput(ValueError):
    pass


class ChatNotCreated(SystemError):
    pass


class TgChat(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)
    id: int
    type: str
    first_name: Optional[str] = None
    username: Optional[str] = None
