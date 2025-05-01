# pyright: reportUnknownMemberType=false
import asyncio
import json
from collections import defaultdict
from collections.abc import Awaitable, Callable
from contextlib import asynccontextmanager
from typing import Any

import pydantic
from fastapi import APIRouter, FastAPI, WebSocket, WebSocketDisconnect, status
from loguru import logger
from redis.asyncio import Redis
from redis.exceptions import ConnectionError, RedisError, TimeoutError

from app.core.config import get_settings
from app.schemas.chat import RedisPubSubMessage, WSChatMessage

settings = get_settings()

redis = Redis.from_url(url=settings.REDIS_URI, decode_responses=True)


class ConnectionManager:
    def __init__(self) -> None:
        self.rooms: dict[str, set[WebSocket]] = defaultdict(set)

    def add(self, room: str, websocket: WebSocket) -> None:
        self.rooms[room].add(websocket)

    def remove(self, room: str, websocket: WebSocket) -> None:
        self.rooms[room].discard(websocket)  # doesn't raise if missing
        if not self.rooms[room]:
            del self.rooms[room]

    def get_room(self, room: str) -> set[WebSocket]:
        return self.rooms.get(room, set()).copy()

    async def broadcast(self, room: str, message: str) -> None:
        for client in self.get_room(room):
            try:
                await client.send_text(message)
            except Exception as e:
                logger.warning(f"Dropping dead WebSocket client in room '{room}': {e}")
                self.remove(room, client)


manager = ConnectionManager()


async def redis_subscriber() -> None:
    """
    Listen to Redis pub/sub pattern channel and forward messages to connected clients in
    the correct room.
    Automatically reconnects on Redis errors.
    """

    while True:
        try:
            pubsub = redis.pubsub()
            await pubsub.psubscribe(f"{settings.REDIS_CHANNEL_PREFIX}*")

            async for message in pubsub.listen():  # type: ignore
                try:
                    parsed = RedisPubSubMessage(**message)  # type: ignore
                except pydantic.ValidationError as e:
                    logger.warning(
                        f"Skipping invalid Redis message: {e} | raw: {message}"
                    )
                    continue

                # Redis pubsub can emit various message types,
                # we only want to handle actual published messages matching our pattern.
                if parsed.type != "pmessage":
                    continue

                # Extract room name from channel
                room = parsed.channel.removeprefix(settings.REDIS_CHANNEL_PREFIX)
                await manager.broadcast(room, parsed.data)

        except (ConnectionError, TimeoutError, RedisError) as e:
            retry_delay_in_sec = settings.REDIS_RETRY_DELAY.total_seconds()
            logger.error(
                f"Redis subscriber error: {e}. Retrying in {retry_delay_in_sec} seconds..."
            )
            await asyncio.sleep(retry_delay_in_sec)


async def handle_chat_message(data: dict[str, Any], _: WebSocket) -> None:
    """
    Validates and publishes a chat message to the Redis channel of the specified room.
    The frontend must send { room, name, message } as payload.
    """

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


# Registry of supported rooms and their associated message handlers
SUPPORTED_ROOMS: dict[str, Callable[[dict[str, Any], WebSocket], Awaitable[None]]] = {
    "chat": handle_chat_message,
    # You can add more handlers here later ...
}


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

            await on_message(data, websocket)

    except WebSocketDisconnect as e:
        logger.debug(f"WebSocket client disconnected from room '{room}': {e}")
    finally:
        manager.remove(room, websocket)


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Start the Redis subscriber in background on startup"""

    asyncio.create_task(redis_subscriber())
    yield  # control is yielded to the FastAPI app


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
        return

    await handle_websocket_connection(websocket=websocket, room=room, on_message=handler)
