from typing import Any

from app.schemas.base import MySchema


class RedisPubSubMessage(MySchema):
    type: str
    pattern: str | None = None
    channel: str
    data: Any
