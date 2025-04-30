import asyncio
import json
from contextlib import asynccontextmanager

import pydantic
from fastapi import APIRouter, FastAPI, WebSocket, WebSocketDisconnect
from loguru import logger
from redis.asyncio import Redis
from redis.exceptions import (
    ConnectionError as RedisConnectionError,
)
from redis.exceptions import (
    RedisError,
)
from redis.exceptions import (
    TimeoutError as RedisTimeoutError,
)

from app.core.config import get_settings
from app.schemas.chat import ChatMessage

settings = get_settings()


# Set of currently connected clients (local to this FastAPI instance)
connected_clients: set[WebSocket] = set()
redis = Redis.from_url(settings.REDIS_URI, decode_responses=True)


HEARTBEAT_MESSAGE = "ping"
REDIS_CHANNEL = "chat:broadcast"  # Redis pub/sub channel name


async def redis_subscriber() -> None:
    """
    Subscribe to Redis pub/sub channel and forward messages to all connected WebSocket
    clients on this instance.
    Retries on Redis connection issues (while loop).
    """
    while True:
        try:
            pubsub = redis.pubsub()
            await pubsub.subscribe(REDIS_CHANNEL)

            async for message in pubsub.listen():
                if message.get("type") != "message":
                    continue

                payload: str = message["data"]

                for client in connected_clients.copy():
                    try:
                        await client.send_text(payload)
                    except Exception as e:
                        logger.warning(f"Dropping dead WebSocket client: {e}")
                        connected_clients.discard(client)

        except (RedisConnectionError, RedisTimeoutError, RedisError):
            logger.error(f"Redis subscriber error: {e}. Retrying in 2 seconds...")
            await asyncio.sleep(2)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Start the Redis subscriber in background on startup
    asyncio.create_task(redis_subscriber())
    yield  # control is yielded to the FastAPI app


router = APIRouter(prefix="/ws", tags=["WebSockets"], lifespan=lifespan)


@router.websocket("/broadcast-message")
async def broadcast_message(websocket: WebSocket):
    await websocket.accept()
    connected_clients.add(websocket)
    try:
        while True:
            raw = await websocket.receive_text()

            # Handle particular heartbeat message case
            if raw == HEARTBEAT_MESSAGE:
                await websocket.send_text("pong")  # local response, not broadcasted
                logger.debug("Received ping from client, responded with pong")
                continue

            # Check JSON validity first
            try:
                data = json.loads(raw)
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON message: {e} | raw: {raw}")
                continue

            # Check ChatMessage vailidity
            try:
                chat_msg = ChatMessage(**data)
            except pydantic.ValidationError as e:
                logger.error(f"Invalid ChatMessage payload: {e} | data: {data}")
                continue

            # Now, the ChatMessage can be sent to all connected clients
            await redis.publish(REDIS_CHANNEL, chat_msg.model_dump_json())

    except WebSocketDisconnect as e:
        logger.debug(f"WebSocket client disconnected: {e}")
    finally:
        connected_clients.discard(websocket)  # doesn't raise if missing
