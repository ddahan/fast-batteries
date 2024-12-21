#!/usr/local/bin/python

import datetime
import hashlib
import json
import logging
import os
import pathlib
import random
import re
import shutil
import sys
from collections.abc import Callable
from datetime import timedelta
from typing import Any

from fastapi import FastAPI
from IPython import embed  # type: ignore
from rich import print as rprint
from sqlalchemy import select

from app.core.config import get_settings
from app.core.database import get_session
from app.models.base import MyModel
from app.schemas.base import MySchema
from app.utils.cli import CustomTable
from app.utils.introspection import detect_elements

type ImportDict = dict[str, Any]


def shell():
    """Run a context-aware user interactive shell (similar to Django shell_plus)."""

    # Build dicts of modules to be imported
    main_imports: ImportDict = {
        "app": FastAPI(),
        "session": next(get_session()),  # get the session from the generator with next()
        "select": select,
        "settings": get_settings(),
    }
    python_imports: ImportDict = {
        "os": os,
        "sys": sys,
        "logging": logging,
        "json": json,
        "datetime": datetime,
        "random": random,
        "re": re,
        "hashlib": hashlib,
        "shutil": shutil,
        "pathlib": pathlib,
        "timedelta": timedelta,
    }
    schemas_imports: ImportDict = detect_elements("app.schemas", MySchema)
    models_imports: ImportDict = detect_elements("app.models", MyModel)

    # Display imported elements
    def _print_dict(
        modules_dict: ImportDict,
        title: str,
        show_method: Callable[
            [Any], str
        ] = lambda obj: f"{obj.__class__.__module__}.{obj.__class__.__name__}",
    ) -> None:
        if modules_dict:
            table = CustomTable(title=f"{title} imports")
            for name in sorted(modules_dict):
                obj = modules_dict[name]
                table.add_row(name, show_method(obj))
            rprint(table)

    print("Starting IPython shell with these preloaded variables...\n")
    _print_dict(main_imports, "Main")
    _print_dict(python_imports, "Python built-in")
    _print_dict(schemas_imports, "MySchema", show_method=lambda obj: f"{obj.__module__}")
    _print_dict(models_imports, "MyModel", show_method=lambda obj: f"{obj.__module__}")

    # Start IPython shell with preloaded variables
    all_imports = main_imports | python_imports | schemas_imports | models_imports
    embed(user_ns=all_imports, colors="Neutral")


if __name__ == "__main__":
    shell()
