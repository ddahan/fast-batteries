from typing import Literal

from app.schemas.base import MySchema


class WSChatMessage(MySchema):
    room: Literal["chat"]
    name: str
    message: str
