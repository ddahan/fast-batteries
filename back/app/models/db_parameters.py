from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Mapped

from app.core.database import SessionDep
from app.models.base import MyModel, SingletonModel


class DBParameters(SingletonModel, MyModel):
    """Since its a singleton, use load() method to get or create the object"""

    APP_TAGLINE: Mapped[str | None]
    # more parameters here ...


def get_db_parameters(session: SessionDep) -> DBParameters:
    return DBParameters.load(session)


DBParametersDep = Annotated[DBParameters, Depends(get_db_parameters)]
