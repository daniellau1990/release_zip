from pathlib import Path
from zip_rar_tool import extract, compress


def test_extract_progress_callback(tmp_path):
    """progress_callback is called with (current, total) for each file."""
    src = tmp_path / "src"
    src.mkdir()
    (src / "a.txt").write_text("a")
    (src / "b.txt").write_text("b")
    archive = tmp_path / "test.zip"

    compress(str(src), str(archive))

    calls = []
    def cb(current, total):
        calls.append((current, total))

    out = tmp_path / "out"
    extract(str(archive), str(out), progress_callback=cb)

    assert len(calls) == 2, f"expected 2 calls, got {len(calls)}"
    assert calls[0] == (1, 2)
    assert calls[1] == (2, 2)


def test_extract_without_callback_still_works(tmp_path):
    """Backward compat: extract without progress_callback must not break."""
    src = tmp_path / "src"
    src.mkdir()
    (src / "x.txt").write_text("hello")
    archive = tmp_path / "test.zip"

    compress(str(src), str(archive))

    out = tmp_path / "out"
    extract(str(archive), str(out))

    assert (out / "x.txt").read_text() == "hello"


def test_compress_progress_callback(tmp_path):
    """Compress also supports progress_callback."""
    src = tmp_path / "src"
    src.mkdir()
    (src / "a.txt").write_text("a")
    (src / "b.txt").write_text("b")

    calls = []
    def cb(current, total):
        calls.append((current, total))

    archive = tmp_path / "test.zip"
    compress(str(src), str(archive), progress_callback=cb)

    assert len(calls) == 2
