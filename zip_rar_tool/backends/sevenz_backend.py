from pathlib import Path
from typing import Optional, List, Dict
import py7zr


class SevenzBackend:
    @staticmethod
    def extract(archive_path: Path, output_dir: Path, password: Optional[str] = None) -> None:
        with py7zr.SevenZipFile(archive_path, mode="r", password=password) as sz:
            sz.extractall(output_dir)

    @staticmethod
    def list_files(archive_path: Path) -> List[Dict]:
        result = []
        with py7zr.SevenZipFile(archive_path, mode="r") as sz:
            for info in sz.list():
                result.append({
                    "filename": info.filename,
                    "size": info.uncompressed,
                    "compressed_size": info.compressed,
                })
        return result

    @staticmethod
    def compress(source_dir: Path, output_path: Path, password: Optional[str] = None) -> None:
        with py7zr.SevenZipFile(output_path, mode="w", password=password) as sz:
            sz.writeall(source_dir, arcname=source_dir.name)
