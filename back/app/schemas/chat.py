from typing import Any

from app.schemas.base import MySchema


class WSBaseMessage(MySchema):
    room: str


class WSChatMessage(WSBaseMessage):
    name: str
    message: str


# ----


class RedisPubSubMessage(MySchema):
    type: str
    pattern: str | None = None
    channel: str
    data: Any
