#!/usr/local/bin/python

from app.models.badge import Badge
from app.schemas.badge import BadgeCreate
from app.utils.cli import create_object_from_cli

if __name__ == "__main__":
    # Badge has a User relation, that the ORM needs to be aware of
    from app.models.user import User  # noqa: F401  # type: ignore

    create_object_from_cli(
        schema_in=BadgeCreate,
        create_method=Badge.create,
        friendly_name="badge",
    )
