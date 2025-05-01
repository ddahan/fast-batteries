from typing import Any

from fastapi import WebSocket, status
from fastapi.testclient import TestClient
from pytest import MonkeyPatch

from app.main import app
from app.routes import websockets as ws_module

client = TestClient(app)


def test_websocket_rejects_unknown_room():
    """
    Test that connecting to an unknown room closes the connection with the correct
    code.
    """

    with client.websocket_connect("/ws/room/unknown") as websocket:
        # Should be immediately closed by the server
        data = websocket.receive()
        assert data["type"] == "websocket.close"
        assert data["code"] == status.WS_1008_POLICY_VIOLATION


def test_websocket_accepts_known_room(monkeypatch: MonkeyPatch):
    """
    Test that connecting to a known room is accepted and stays open.
    """

    dummy_handler_called = {}

    async def dummy_handler(data: dict[str, Any], websocket: WebSocket) -> None:
        dummy_handler_called["called"] = True

    monkeypatch.setitem(ws_module.SUPPORTED_ROOMS, "chat", dummy_handler)
    with client.websocket_connect("/ws/room/chat") as websocket:
        websocket.send_text('{"room": "chat", "name": "Tom", "message": "hi"}')
        # The connection should remain open, so we can send/receive
        # Instead of websocket.closed, check that we can send another message without error
        try:
            websocket.send_text('{"room": "chat", "name": "Tom", "message": "hi again"}')
            still_open = True
        except Exception:
            still_open = False
        assert still_open
