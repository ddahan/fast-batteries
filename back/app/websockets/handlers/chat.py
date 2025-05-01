# pyright: reportUnknownMemberType=false
"""
Validates and publishes a chat message to the Redis channel of the specified room.
The frontend must send { room, name, message } as payload.
"""

from typing import Any

import pydantic
from fastapi import WebSocket
from loguru import logger
from redis.asyncio import Redis

from app.core.config import get_settings
from app.websockets.schemas.chat import WSChatMessage

settings = get_settings()
redis = Redis.from_url(settings.REDIS_URI, decode_responses=True)


async def handle_chat_message(data: dict[str, Any], _: WebSocket) -> None:
    # Check WSChatMessage validity
    try:
        chat_msg = WSChatMessage(**data)
    except pydantic.ValidationError as e:
        logger.error(f"Invalid WSChatMessage payload: {e} | data: {data}")
        return

    # Now, the WSChatMessage can be sent to connected clients of the right room
    await redis.publish(
        f"{settings.REDIS_CHANNEL_PREFIX}{data['room']}", chat_msg.model_dump_json()
    )
