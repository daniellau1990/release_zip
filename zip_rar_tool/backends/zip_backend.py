from pathlib import Path
import zipfile
from typing import Optional, List, Dict, Callable


class ZipBackend:
    @staticmethod
    def extract(
        archive_path: Path,
        output_dir: Path,
        password: Optional[str] = None,
        progress_callback: Optional[Callable[[int, int], None]] = None,
    ) -> None:
        with zipfile.ZipFile(archive_path, "r") as zf:
            if password:
                zf.setpassword(password.encode("utf-8"))
            members = zf.infolist()
            total = len(members)
            for i, member in enumerate(members, 1):
                zf.extract(member, output_dir)
                if progress_callback:
                    progress_callback(i, total)

    @staticmethod
    def list_files(archive_path: Path) -> List[Dict]:
        result = []
        with zipfile.ZipFile(archive_path, "r") as zf:
            for info in zf.infolist():
                result.append({
                    "filename": info.filename,
                    "size": info.file_size,
                    "compressed_size": info.compress_size,
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
        with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for i, file_path in enumerate(file_paths, 1):
                arcname = str(file_path.relative_to(source_dir))
                zf.write(file_path, arcname)
                if progress_callback:
                    progress_callback(i, total)
