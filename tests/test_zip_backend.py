from pathlib import Path

from zip_rar_tool.backends.zip_backend import ZipBackend


def test_zip_roundtrip(tmp_path):
    src = tmp_path / "src"
    src.mkdir()
    (src / "hello.txt").write_text("world", encoding="utf-8")
    archive = tmp_path / "test.zip"
    out = tmp_path / "out"

    ZipBackend.compress(src, archive)
    ZipBackend.extract(archive, out)

    assert (out / "hello.txt").read_text(encoding="utf-8") == "world"


def test_zip_list(tmp_path):
    src = tmp_path / "src"
    src.mkdir()
    (src / "a.txt").write_text("a")
    archive = tmp_path / "test.zip"

    ZipBackend.compress(src, archive)
    files = ZipBackend.list_files(archive)

    assert isinstance(files, list)
    assert len(files) == 1
    assert files[0]["filename"] == "a.txt"
