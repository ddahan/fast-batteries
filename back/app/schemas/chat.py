from app.schemas.base import MySchema


class ChatMessage(MySchema):
    name: str
    message: str
