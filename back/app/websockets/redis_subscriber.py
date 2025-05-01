# pyright: reportUnknownMemberType=false
"""
Listen to Redis pub/sub pattern channel and forward messages to connected clients in
the correct room.
Automatically reconnects on Redis errors.
"""

import asyncio

import pydantic
from loguru import logger
from redis.asyncio import Redis
from redis.exceptions import ConnectionError, RedisError, TimeoutError

from app.core.config import get_settings
from app.websockets.managers import ConnectionManager
from app.websockets.schemas.base import RedisPubSubMessage

settings = get_settings()


redis = Redis.from_url(url=settings.REDIS_URI, decode_responses=True)
manager = ConnectionManager()


async def redis_subscriber() -> None:
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
