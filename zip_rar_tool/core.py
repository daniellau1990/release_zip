from pathlib import Path

from zip_rar_tool.utils import guess_format
from zip_rar_tool.backends.zip_backend import ZipBackend
from zip_rar_tool.backends.rar_backend import RarBackend
from zip_rar_tool.backends.sevenz_backend import SevenzBackend

BACKENDS = {
    "zip": ZipBackend,
    "rar": RarBackend,
    "7z": SevenzBackend,
}


def extract(archive_path: str, output_dir: str, password: str = None) -> None:
    fmt = guess_format(archive_path)
    backend = BACKENDS[fmt]
    backend.extract(Path(archive_path), Path(output_dir), password)


def list_files(archive_path: str) -> list:
    fmt = guess_format(archive_path)
    backend = BACKENDS[fmt]
    return backend.list_files(Path(archive_path))


def compress(source_dir: str, output_path: str, password: str = None) -> None:
    fmt = guess_format(output_path)
    backend = BACKENDS[fmt]
    backend.compress(Path(source_dir), Path(output_path), password)
