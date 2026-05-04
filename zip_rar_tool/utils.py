from pathlib import Path


def safe_path(destination: Path, filename: str) -> Path:
    cleaned = Path(filename).name
    return destination / cleaned


def guess_format(path: str) -> str:
    ext = Path(path).suffix.lower()
    if ext == ".zip":
        return "zip"
    elif ext == ".rar":
        return "rar"
    elif ext == ".7z":
        return "7z"
    raise ValueError(f"Unsupported format: {ext}")
