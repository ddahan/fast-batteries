import shutil
from pathlib import Path

from loguru import logger


def erase(path: Path, missing_ok: bool = True) -> None:
    """
    Erase the given file or directory (and its content).
    - confirm_prompt: if True, the user is asked a confirmation
    - missing_ok: raise an Error if the file is not found.
    """

    if path.exists():
        try:
            if path.is_file():
                path.unlink()
                logger.info(f"{path} file has been deleted.")
            elif path.is_dir():
                shutil.rmtree(path)  # path.rmdir can't delete a non empty directory
                logger.info(f"{path} directory (and its content) has been deleted.")
            else:
                raise ValueError("Unexpected type of file.")
        except OSError as e:
            logger.error(f"Error deleting {path}: {e}")
            raise
    else:
        if missing_ok:
            logger.info(f"No file or directory {path} has been found for deletion.")
        else:
            msg = f"File or directory {path} not found."
            logger.error(msg)
            raise FileNotFoundError(msg)


def create_directory_if_not_exist(path: Path) -> None:
    """Create a given directory of the given path_name if it does not exist yet."""
    if not path.exists():
        path.mkdir()
        logger.info(f"{path.name} directory has been created.")
