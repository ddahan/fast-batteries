import asyncio
from unittest.mock import AsyncMock, patch

import pytest
from fastapi import WebSocket

from app.websockets.connection import handle_websocket_connection


@pytest.mark.asyncio
async def test_handle_websocket_connection_heartbeat():
    """
    Test that the connection handler responds to heartbeat pings.
    """

    # Mock websocket
    websocket = AsyncMock(spec=WebSocket)
    websocket.receive_text = AsyncMock(side_effect=["PING", asyncio.CancelledError()])
    websocket.accept = AsyncMock()
    websocket.send_text = AsyncMock()

    # Mock manager
    with patch("app.websockets.connection.manager") as manager:
        # Patch settings
        with patch("app.websockets.connection.settings") as settings:
            settings.REDIS_HEARBEAT_PING = "PING"
            settings.REDIS_HEARBEAT_PONG = "PONG"
            # Run
            with pytest.raises(asyncio.CancelledError):
                await handle_websocket_connection(websocket, "room", AsyncMock())
            websocket.accept.assert_called_once()
            websocket.send_text.assert_any_call("PONG")
            manager.add.assert_called_once()
            manager.remove.assert_called_once()
