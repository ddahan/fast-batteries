from decimal import Decimal
from typing import Annotated

from pydantic import Field, SecretStr

Price = Annotated[Decimal, Field(ge=0, max_digits=8, decimal_places=2)]

Percentage = Annotated[float, Field(ge=0, le=100)]

Password = Annotated[SecretStr, Field(min_length=8, max_length=40)]
