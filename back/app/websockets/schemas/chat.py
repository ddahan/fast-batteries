from app.websockets.schemas.base import WSBaseMessage


class WSChatMessage(WSBaseMessage):
    name: str
    message: str
