import asyncio
from unittest.mock import AsyncMock, patch

import pytest

from app.websockets.redis_subscriber import redis_subscriber


@pytest.mark.asyncio
async def test_redis_subscriber_handles_invalid_and_valid_messages():
    """
    Test that the Redis subscriber skips invalid messages and broadcasts valid ones.
    """

    # Patch Redis pubsub and manager
    with (
        patch("app.websockets.redis_subscriber.redis.pubsub") as mock_pubsub,
        patch(
            "app.websockets.redis_subscriber.manager.broadcast", new_callable=AsyncMock
        ) as mock_broadcast,
        patch("app.websockets.redis_subscriber.settings") as settings,
    ):
        # Setup settings
        settings.REDIS_CHANNEL_PREFIX = "room:"
        settings.REDIS_RETRY_DELAY.total_seconds.return_value = 0.01

        # Mock pubsub.listen to yield messages
        class DummyPubSub:
            async def psubscribe(self, *_):
                pass

            async def listen(self):
                # First: invalid message (should be skipped)
                yield {"type": "other", "channel": "room:test", "data": "{}"}
                # Second: valid pmessage
                yield {"type": "pmessage", "channel": "room:test", "data": '{"msg":1}'}
                # Stop after two
                raise asyncio.CancelledError()

        mock_pubsub.return_value = DummyPubSub()
        # Patch RedisPubSubMessage to just return the dict as an object
        with patch(
            "app.websockets.redis_subscriber.RedisPubSubMessage",
            side_effect=lambda **kwargs: type("Msg", (), kwargs),  # type: ignore
        ):
            with pytest.raises(asyncio.CancelledError):
                await redis_subscriber()
            # Only the valid pmessage should trigger broadcast
            mock_broadcast.assert_awaited_once_with("test", '{"msg":1}')
