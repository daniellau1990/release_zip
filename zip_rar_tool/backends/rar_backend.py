from pathlib import Path
from typing import Optional, List, Dict, Callable
import rarfile

_script_dir = Path(__file__).resolve().parent
_bin_dir = _script_dir.parents[1] / "bin"
_unrar_exe = str(_bin_dir / "unrar.exe")
if Path(_unrar_exe).exists():
    rarfile.UNRAR_TOOL = _unrar_exe


class RarBackend:
    @staticmethod
    def extract(
        archive_path: Path,
        output_dir: Path,
        password: Optional[str] = None,
        progress_callback: Optional[Callable[[int, int], None]] = None,
    ) -> None:
        with rarfile.RarFile(archive_path) as rf:
            if password:
                rf.setpassword(password)
            members = rf.infolist()
            total = len(members)
            for i, member in enumerate(members, 1):
                rf.extract(member, output_dir)
                if progress_callback:
                    progress_callback(i, total)

    @staticmethod
    def list_files(archive_path: Path) -> List[Dict]:
        result = []
        with rarfile.RarFile(archive_path) as rf:
            for info in rf.infolist():
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
        raise NotImplementedError("RAR compression requires WinRAR to be installed")


def check_winrar() -> Optional[str]:
    import winreg
    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WinRAR") as key:
            path = winreg.QueryValueEx(key, "exe32")[0]
            return path
    except (OSError, FileNotFoundError):
        return None
