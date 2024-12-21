import importlib
import inspect
import pkgutil
from pathlib import Path
from types import ModuleType


def import_package_modules(package: str) -> list[ModuleType]:
    """Import and return all modules from a specified package."""

    package_module = importlib.import_module(package)  # Import the package
    package_dir = Path(str(package_module.__file__)).parent

    modules: list[ModuleType] = []
    for _, module_name, is_pkg in pkgutil.iter_modules([str(package_dir)], f"{package}."):
        if not is_pkg:
            module = importlib.import_module(module_name)  # Import the module
            modules.append(module)

    return modules


def detect_elements(path: str, base_class: type) -> dict[str, type]:
    """
    In the given folder, parse all files and detect items of the given type.
    Returns a dict with item names as keys and model class types as values.
    """
    items: dict[str, type] = {}
    modules = import_package_modules(path)

    # Inspect the module and find all 'type' subclasses
    for module in modules:
        for name, obj in inspect.getmembers(module, inspect.isclass):
            if issubclass(obj, base_class) and obj is not base_class:
                items[name] = obj

    return items
