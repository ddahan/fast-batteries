from unittest.mock import AsyncMock, patch

import pytest
from fastapi import WebSocket

from app.websockets.handlers.chat import handle_chat_message


@pytest.mark.asyncio
async def test_handle_chat_message_valid():
    """
    Test that a valid chat message is published to Redis.
    """

    data = {"room": "test", "name": "user", "message": "hello"}
    websocket = AsyncMock(spec=WebSocket)
    with (
        patch("app.websockets.handlers.chat.WSChatMessage") as WSChatMessage,
        patch(
            "app.websockets.handlers.chat.redis.publish", new_callable=AsyncMock
        ) as mock_publish,
    ):
        WSChatMessage.return_value.model_dump_json.return_value = (
            '{"room":"test","name":"user","message":"hello"}'
        )
        await handle_chat_message(data, websocket)
        WSChatMessage.assert_called_once_with(**data)
        mock_publish.assert_awaited_once()
