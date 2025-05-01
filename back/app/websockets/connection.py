import json
from collections.abc import Awaitable, Callable
from typing import Any

from fastapi import WebSocket, WebSocketDisconnect
from loguru import logger

from app.core.config import get_settings
from app.websockets.redis_subscriber import manager

settings = get_settings()


async def handle_websocket_connection(
    websocket: WebSocket,
    room: str,
    on_message: Callable[[dict[str, Any], WebSocket], Awaitable[None]],
):
    """
    Accepts a WebSocket, assigns it to a room, and listens for messages.
    Supports local heartbeat replies. Dispatches messages to the on_message handler.
    """

    await websocket.accept()
    manager.add(room, websocket)

    try:
        while True:
            raw = await websocket.receive_text()

            # Handle particular heartbeat message case (not JSON)
            if raw == settings.REDIS_HEARBEAT_PING:
                # local response, not broadcasted
                await websocket.send_text(settings.REDIS_HEARBEAT_PONG)
                logger.debug(
                    f"Received {settings.REDIS_HEARBEAT_PING} from client,"
                    f"responded with {settings.REDIS_HEARBEAT_PONG}"
                )
                continue

            # Now we're sure message should be in JSON
            try:
                data = json.loads(raw)
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON message in room '{room}': {e} | raw: {raw}")
                continue

            try:
                await on_message(data, websocket)
            except Exception as e:
                logger.exception(f"Unexpected error in on_message: {e}")

    except WebSocketDisconnect as e:
        logger.debug(f"WebSocket client disconnected from room '{room}': {e}")
    finally:
        manager.remove(room, websocket)
