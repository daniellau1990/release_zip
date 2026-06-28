from pathlib import Path
from typing import Optional, List, Dict, Callable
import py7zr


class SevenzBackend:
    @staticmethod
    def extract(
        archive_path: Path,
        output_dir: Path,
        password: Optional[str] = None,
        progress_callback: Optional[Callable[[int, int], None]] = None,
    ) -> None:
        with py7zr.SevenZipFile(archive_path, mode="r", password=password) as sz:
            members = sz.list()
            total = len(members)
            for i, member in enumerate(members, 1):
                sz.extract(output_dir, targets=[member.filename])
                if progress_callback:
                    progress_callback(i, total)

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
    def compress(
        source_dir: Path,
        output_path: Path,
        password: Optional[str] = None,
        progress_callback: Optional[Callable[[int, int], None]] = None,
    ) -> None:
        file_paths = [p for p in source_dir.rglob("*") if p.is_file()]
        total = len(file_paths)
        with py7zr.SevenZipFile(output_path, mode="w", password=password) as sz:
            for i, file_path in enumerate(file_paths, 1):
                arcname = f"{source_dir.name}/{file_path.relative_to(source_dir)}"
                sz.write(file_path, arcname)
                if progress_callback:
                    progress_callback(i, total)
