from pathlib import Path

from zip_rar_tool.backends.sevenz_backend import SevenzBackend


def test_sevenz_roundtrip(tmp_path):
    src = tmp_path / "src"
    src.mkdir()
    (src / "hello.txt").write_text("world", encoding="utf-8")
    archive = tmp_path / "test.7z"
    out = tmp_path / "out"

    SevenzBackend.compress(src, archive)
    SevenzBackend.extract(archive, out)

    assert (out / "src" / "hello.txt").read_text(encoding="utf-8") == "world"


def test_sevenz_list(tmp_path):
    src = tmp_path / "src"
    src.mkdir()
    (src / "a.txt").write_text("a")
    archive = tmp_path / "test.7z"

    SevenzBackend.compress(src, archive)
    files = SevenzBackend.list_files(archive)

    assert isinstance(files, list)
