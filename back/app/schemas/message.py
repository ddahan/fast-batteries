from app.schemas.base import MySchema


class Message(MySchema):
    """Generic message for API responses"""

    message: str
