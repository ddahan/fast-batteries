import os
import tempfile
from pathlib import Path

import pytest

from app.utils.filesystem import create_directory_if_not_exist, erase


class TestErase:
    def test_erase_existing_file(self) -> None:
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_path: Path = Path(temp_file.name)
        assert temp_path.exists()

        erase(temp_path)
        assert not temp_path.exists()

    def test_erase_existing_directory(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path: Path = Path(temp_dir) / "test_file.txt"
            temp_path.touch()
            assert temp_path.exists()

            erase(Path(temp_dir))
            assert not Path(temp_dir).exists()

    def test_erase_nonexistent_file_missing_ok(self) -> None:
        temp_path: Path = Path(tempfile.gettempdir()) / "nonexistent_file.txt"
        assert not temp_path.exists()

        # Should not raise an exception
        erase(temp_path, missing_ok=True)

    def test_erase_nonexistent_file_missing_not_ok(self) -> None:
        temp_path: Path = Path(tempfile.gettempdir()) / "nonexistent_file.txt"
        assert not temp_path.exists()

        # Should raise FileNotFoundError
        with pytest.raises(FileNotFoundError):
            erase(temp_path, missing_ok=False)

    def test_erase_unexpected_file_type(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            fifo_path: Path = Path(temp_dir) / "test_fifo"
            # Create a FIFO file (named pipe) to simulate unexpected file type
            os.mkfifo(str(fifo_path))
            assert fifo_path.exists()

            with pytest.raises(ValueError):
                erase(fifo_path)


class TestCreateDirectoryIfNotExists:
    def test_create_directory_when_not_exists(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            dir_path = Path(temp_dir) / "new_directory"
            assert not dir_path.exists()  # Ensure directory does not exist

            create_directory_if_not_exist(dir_path)
            assert dir_path.exists() and dir_path.is_dir()  # Verify directory was created

    def test_create_directory_when_already_exists(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            dir_path = Path(temp_dir) / "existing_directory"
            dir_path.mkdir()  # Create directory beforehand
            assert dir_path.exists() and dir_path.is_dir()  # Ensure directory exists

            create_directory_if_not_exist(dir_path)
            assert (
                dir_path.exists() and dir_path.is_dir()
            )  # Ensure directory still exists

    def test_create_directory_invalid_path(self) -> None:
        invalid_path = Path("/invalid/path/to/directory")
        with pytest.raises(OSError):  # Expecting an OSError for invalid paths
            create_directory_if_not_exist(invalid_path)
