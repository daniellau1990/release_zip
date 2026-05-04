from pathlib import Path
import zipfile
from typing import Optional, List, Dict


class ZipBackend:
    @staticmethod
    def extract(archive_path: Path, output_dir: Path, password: Optional[str] = None) -> None:
        with zipfile.ZipFile(archive_path, "r") as zf:
            if password:
                zf.setpassword(password.encode("utf-8"))
            zf.extractall(output_dir)

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
    def compress(source_dir: Path, output_path: Path, password: Optional[str] = None) -> None:
        with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for file_path in source_dir.rglob("*"):
                if file_path.is_file():
                    arcname = str(file_path.relative_to(source_dir))
                    zf.write(file_path, arcname)
