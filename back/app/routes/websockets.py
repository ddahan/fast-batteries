# pyright: reportUnknownMemberType=false
import asyncio
from collections.abc import Awaitable, Callable
from contextlib import asynccontextmanager
from typing import Any

from fastapi import APIRouter, FastAPI, WebSocket, status
from loguru import logger

from app.core.config import get_settings
from app.websockets.connection import handle_websocket_connection
from app.websockets.handlers.chat import handle_chat_message
from app.websockets.redis_subscriber import redis_subscriber

settings = get_settings()


# Registry of supported rooms and their associated message handlers
SUPPORTED_ROOMS: dict[str, Callable[[dict[str, Any], WebSocket], Awaitable[None]]] = {
    "chat": handle_chat_message,
    # add more handlers here ...
}


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Start the Redis subscriber in background on startup"""
    asyncio.create_task(redis_subscriber())
    yield


router = APIRouter(prefix="/ws", tags=["WebSockets"], lifespan=lifespan)


@router.websocket("/room/{room}")
async def websocket_room(room: str, websocket: WebSocket) -> None:
    """
    Entry endpoint able to redirect to any handler based on given room.
    Unknown rooms are not allowed.
    """
    handler = SUPPORTED_ROOMS.get(room)
    if handler is None:
        await websocket.accept()
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        logger.warning(f"Rejected WebSocket connection to unsupported room: '{room}'")
    else:
        await handle_websocket_connection(
            websocket=websocket, room=room, on_message=handler
        )
