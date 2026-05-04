"""Integration test: full roundtrip for all formats"""
from pathlib import Path

from zip_rar_tool import extract, list_files, compress


def test_zip_roundtrip_integration(tmp_path):
    src = tmp_path / "src"
    src.mkdir()
    (src / "data.txt").write_text("hello", encoding="utf-8")

    archive = str(tmp_path / "output.zip")
    out = str(tmp_path / "out")

    compress(str(src), archive)
    files = list_files(archive)
    assert len(files) == 1

    extract(archive, out)
    assert (Path(out) / "data.txt").read_text(encoding="utf-8") == "hello"


def test_sevenz_roundtrip_integration(tmp_path):
    src = tmp_path / "src"
    src.mkdir()
    (src / "data.txt").write_text("hello", encoding="utf-8")

    archive = str(tmp_path / "output.7z")
    out = str(tmp_path / "out")

    compress(str(src), archive)
    files = list_files(archive)
    assert len(files) >= 1

    extract(archive, out)
    assert (Path(out) / "src" / "data.txt").read_text(encoding="utf-8") == "hello"
