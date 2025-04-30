import json

import pydantic
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from loguru import logger

from app.schemas.chat import ChatMessage

router = APIRouter(prefix="/ws", tags=["WebSockets"])


# ⚠️ in-memory Python set works fine for a single-process, single-server dev environment
# In production: use a shared pub/sub backend like Redis
connected_clients: set[WebSocket] = set()


HEARTBEAT_MESSAGE = "ping"


@router.websocket("/broadcast-message")
async def broadcast_message(websocket: WebSocket):
    await websocket.accept()
    connected_clients.add(websocket)
    try:
        while True:
            raw = await websocket.receive_text()

            # Handle particular heartbeat message case
            if raw == HEARTBEAT_MESSAGE:
                logger.debug(f"Websocket {HEARTBEAT_MESSAGE} message sent")
                await websocket.send_text("pong")
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
            for client in connected_clients.copy():
                try:
                    await client.send_json(chat_msg.model_dump())
                except Exception as e:
                    logger.warning(f"Dropping unresponsive WebSocket client: {e}")
                    connected_clients.discard(client)
    except WebSocketDisconnect as e:
        logger.debug(f"WebSocket client disconnected: {e}")
    finally:
        connected_clients.discard(websocket)  # doesn't raise if missing
