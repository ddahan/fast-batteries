#!/usr/local/bin/python

import typer

from app.models.user import User
from app.schemas.user import UserClassicIn
from app.utils.cli import create_object_from_cli

app = typer.Typer()


@app.command()
def create_superuser():
    # User has a Badge relation, that the ORM needs to be aware of
    from app.models.badge import Badge  # noqa: F401  # type: ignore

    create_object_from_cli(
        schema_in=UserClassicIn,
        create_method=User.register_super_user,
        friendly_name="super user",
    )


if __name__ == "__main__":
    app()
