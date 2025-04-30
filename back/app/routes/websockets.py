import asyncio
import json
from collections.abc import Awaitable, Callable
from contextlib import asynccontextmanager
from typing import Any

import pydantic
from fastapi import APIRouter, FastAPI, WebSocket, WebSocketDisconnect
from loguru import logger
from redis.asyncio import Redis
from redis.exceptions import ConnectionError, RedisError, TimeoutError

from app.core.config import get_settings
from app.schemas.chat import ChatMessage

settings = get_settings()


# Set of currently connected clients (local to this FastAPI instance)
connected_clients: set[WebSocket] = set()
redis = Redis.from_url(settings.REDIS_URI, decode_responses=True)


HEARTBEAT_MESSAGE = "ping"
REDIS_CHANNEL = "chat:broadcast"  # Redis pub/sub channel name
REDIS_RETRY_TIME_SEC = 3


class ConnectionManager:
    def __init__(self) -> None:
        self.active_connections: set[WebSocket] = set()

    def add(self, websocket: WebSocket) -> None:
        self.active_connections.add(websocket)

    def remove(self, websocket: WebSocket) -> None:
        self.active_connections.discard(websocket)  # doesn't raise if missing

    def all(self) -> set[WebSocket]:
        return self.active_connections.copy()  # copy prevents from error in co-routine

    async def broadcast(self, message: str) -> None:
        for client in self.all():
            try:
                await client.send_text(message)
            except Exception as e:
                logger.warning(f"Dropping dead WebSocket client: {e}")
                self.remove(client)


manager = ConnectionManager()


async def redis_subscriber() -> None:
    """
    Listen to Redis channel and forward messages to all connected clients.
    Reconnects automatically on Redis errors.
    """

    while True:
        try:
            pubsub = redis.pubsub()
            await pubsub.subscribe(REDIS_CHANNEL)

            async for message in pubsub.listen():
                if message.get("type") != "message":
                    continue

                await manager.broadcast(message["data"])  # type: ignore

        except (ConnectionError, TimeoutError, RedisError) as e:
            logger.error(
                f"Redis subscriber error: {e}. Retrying in {REDIS_RETRY_TIME_SEC} seconds..."
            )
            await asyncio.sleep(REDIS_RETRY_TIME_SEC)


async def handle_chat_message(data: dict[str, Any], _: WebSocket) -> None:
    """
    Handle a message received over WebSocket: parse, validate and publish to Redis.
    """

    # Check ChatMessage validity
    try:
        chat_msg = ChatMessage(**data)
    except pydantic.ValidationError as e:
        logger.error(f"Invalid ChatMessage payload: {e} | data: {data}")
        return

    # Now, the ChatMessage can be sent to all connected clients
    await redis.publish(REDIS_CHANNEL, chat_msg.model_dump_json())


async def handle_websocket_connection(
    websocket: WebSocket,
    on_message: Callable[[dict[str, Any], WebSocket], Awaitable[None]],
):
    """
    Accepts a WebSocket, handles heartbeat and forwards messages to a custom handler.
    """

    await websocket.accept()
    manager.add(websocket)
    try:
        while True:
            raw = await websocket.receive_text()

            # Handle particular heartbeat message case (not JSON)
            if raw == HEARTBEAT_MESSAGE:
                await websocket.send_text("pong")  # local response, not broadcasted
                logger.debug("Received ping from client, responded with pong")
                continue

            # Now we're sure message should be in JSON
            try:
                data = json.loads(raw)
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON message: {e} | raw: {raw}")
                continue

            await on_message(data, websocket)

    except WebSocketDisconnect as e:
        logger.debug(f"WebSocket client disconnected: {e}")
    finally:
        manager.remove(websocket)


@asynccontextmanager
async def lifespan(_: FastAPI):
    # Start the Redis subscriber in background on startup
    asyncio.create_task(redis_subscriber())
    yield  # control is yielded to the FastAPI app


router = APIRouter(prefix="/ws", tags=["WebSockets"], lifespan=lifespan)


@router.websocket("/broadcast-message")
async def broadcast_message(websocket: WebSocket) -> None:
    await handle_websocket_connection(websocket, handle_chat_message)
