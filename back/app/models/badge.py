from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import (
    DeactivateModel,
    ExpireModel,
    MyModel,
    SecretIdModel,
    TimeStampModel,
)
from app.utils.strings import SecretId

if TYPE_CHECKING:
    from app.models.user import User


class Badge(SecretIdModel, TimeStampModel, ExpireModel, DeactivateModel, MyModel):
    owner_id: Mapped[SecretId] = mapped_column(ForeignKey("tb_user.id"))
    owner: Mapped[User] = relationship(back_populates="badges", lazy="selectin")
