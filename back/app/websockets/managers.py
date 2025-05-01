"""
Maintains the ConnectionManager with per-room WebSocket sets and broadcasting logic.
"""

from collections import defaultdict

from fastapi import WebSocket
from loguru import logger


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
