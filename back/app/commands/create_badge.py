#!/usr/local/bin/python

import typer

from app.models.badge import Badge
from app.schemas.badge import BadgeCreate
from app.utils.cli import create_object_from_cli

app = typer.Typer()


@app.command()
def create_badge():
    """Create a badge in an interactive way"""
    # Badge has a User relation, that the ORM needs to be aware of
    from app.models.user import User  # noqa: F401  # type: ignore

    create_object_from_cli(
        schema_in=BadgeCreate,
        create_method=Badge.create,
        friendly_name="badge",
    )


if __name__ == "__main__":
    app()
