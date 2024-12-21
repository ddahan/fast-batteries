from typing import Any

from app.models.base import MyModel


def model_to_dict(instance: MyModel) -> dict[str, Any]:
    """
    Converts a SQLAlchemy instance to a dictionary, excluding `_sa_instance_state`.
    Useful if we don't want to use a Pydantic Schema.
    """
    return {
        key: value
        for key, value in instance.__dict__.items()
        if key != "_sa_instance_state"
    }
