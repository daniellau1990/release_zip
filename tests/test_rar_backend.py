import os
import sys
from pathlib import Path

# Add bin/ to PATH so rarfile finds unrar.exe
_bin = str(Path(__file__).resolve().parents[1] / "bin")
os.environ["PATH"] = _bin + os.pathsep + os.environ.get("PATH", "")

import pytest

pytest.importorskip("rarfile")

from zip_rar_tool.backends.rar_backend import RarBackend, check_winrar

FIXTURE_DIR = Path(__file__).parent / "fixtures"


def test_rar_check_winrar():
    result = check_winrar()
    assert result is None or isinstance(result, str)


def test_rar_list():
    archive = FIXTURE_DIR / "test.rar"
    files = RarBackend.list_files(archive)
    assert len(files) >= 2
    names = [f["filename"] for f in files]
    assert "UnRAR.exe" in names
    assert "license.txt" in names


def test_rar_extract(tmp_path):
    archive = FIXTURE_DIR / "test.rar"
    RarBackend.extract(archive, tmp_path)
    assert (tmp_path / "license.txt").exists()
