"""Tests for batch_compress.py (stdin-based multi-file compression)"""
from pathlib import Path
import subprocess
import sys

_SCRIPT = Path(__file__).resolve().parents[1] / "zip_rar_tool" / "batch_compress.py"


def _run_batch_compress(input_text, output_path, cwd):
    """Helper: pipe text to batch_compress.py and return output"""
    proc = subprocess.run(
        [sys.executable, str(_SCRIPT), str(output_path)],
        input=input_text,
        capture_output=True,
        text=True,
        cwd=cwd,
    )
    return proc


def test_batch_single_file(tmp_path):
    src = tmp_path / "a.txt"
    src.write_text("hello", encoding="utf-8")
    out = tmp_path / "out.zip"

    proc = _run_batch_compress(str(src), out, tmp_path)
    assert proc.returncode == 0
    assert out.exists()

    import zipfile
    with zipfile.ZipFile(str(out)) as zf:
        assert zf.read("a.txt").decode() == "hello"


def test_batch_multi_file(tmp_path):
    a = tmp_path / "a.txt"; a.write_text("a")
    b = tmp_path / "b.txt"; b.write_text("b")
    out = tmp_path / "out.zip"

    proc = _run_batch_compress(f"{a} {b}", out, tmp_path)
    assert proc.returncode == 0

    import zipfile
    with zipfile.ZipFile(str(out)) as zf:
        names = zf.namelist()
        assert "a.txt" in names
        assert "b.txt" in names


def test_batch_folder(tmp_path):
    src = tmp_path / "myfolder"
    src.mkdir()
    (src / "nested.txt").write_text("nested")
    out = tmp_path / "out.zip"

    proc = _run_batch_compress(str(src), out, tmp_path)
    assert proc.returncode == 0

    import zipfile
    with zipfile.ZipFile(str(out)) as zf:
        assert "myfolder/nested.txt" in zf.namelist()


def test_batch_mixed(tmp_path):
    a = tmp_path / "a.txt"; a.write_text("a")
    folder = tmp_path / "folder"
    folder.mkdir()
    (folder / "f.txt").write_text("f")
    out = tmp_path / "out.zip"

    proc = _run_batch_compress(f"{a} {folder}", out, tmp_path)
    assert proc.returncode == 0

    import zipfile
    with zipfile.ZipFile(str(out)) as zf:
        assert "a.txt" in zf.namelist()
        assert "folder/f.txt" in zf.namelist()


def test_batch_quoted_paths(tmp_path):
    """Simulate paths with special characters (shlex handling)"""
    folder = tmp_path / "my folder"
    folder.mkdir()
    (folder / "f.txt").write_text("f")

    src = tmp_path / "a&b.txt"
    src.write_text("special")
    out = tmp_path / "out.zip"

    input_line = f'"{src}" "{folder}"'
    proc = _run_batch_compress(input_line, out, tmp_path)
    assert proc.returncode == 0, proc.stderr

    import zipfile
    with zipfile.ZipFile(str(out)) as zf:
        assert "a&b.txt" in zf.namelist()
