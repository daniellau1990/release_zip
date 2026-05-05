"""Tests for batch_compress.py (temp-file based multi-file compression)"""
from pathlib import Path
import subprocess
import sys
import os
import tempfile

_SCRIPT = Path(__file__).resolve().parents[1] / "zip_rar_tool" / "batch_compress.py"


def _run_with_temp(input_text, output_path, cwd):
    """Write input_text to temp file, pass to batch_compress.py"""
    tmp = tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", suffix=".txt", delete=False, dir=cwd)
    tmp.write(input_text)
    tmp.close()
    try:
        proc = subprocess.run(
            [sys.executable, str(_SCRIPT), str(output_path), tmp.name],
            capture_output=True, text=True, cwd=cwd,
        )
    finally:
        os.unlink(tmp.name)
    return proc


def test_single_file(tmp_path):
    src = tmp_path / "a.txt"
    src.write_text("hello", encoding="utf-8")
    out = tmp_path / "out.zip"

    proc = _run_with_temp(str(src), out, tmp_path)
    assert proc.returncode == 0, proc.stderr
    assert out.exists()

    import zipfile
    with zipfile.ZipFile(str(out)) as zf:
        assert zf.read("a.txt").decode() == "hello"


def test_multi_file(tmp_path):
    a = tmp_path / "a.txt"; a.write_text("a")
    b = tmp_path / "b.txt"; b.write_text("b")
    out = tmp_path / "out.zip"

    proc = _run_with_temp(f"{a}\n{b}", out, tmp_path)
    assert proc.returncode == 0

    import zipfile
    with zipfile.ZipFile(str(out)) as zf:
        names = zf.namelist()
        assert "a.txt" in names
        assert "b.txt" in names


def test_folder(tmp_path):
    src = tmp_path / "myfolder"
    src.mkdir()
    (src / "nested.txt").write_text("nested")
    out = tmp_path / "out.zip"

    proc = _run_with_temp(str(src), out, tmp_path)
    assert proc.returncode == 0

    import zipfile
    with zipfile.ZipFile(str(out)) as zf:
        assert "myfolder/nested.txt" in zf.namelist()


def test_mixed(tmp_path):
    a = tmp_path / "a.txt"; a.write_text("a")
    folder = tmp_path / "folder"
    folder.mkdir(); (folder / "f.txt").write_text("f")
    out = tmp_path / "out.zip"

    proc = _run_with_temp(f"{a}\n{folder}", out, tmp_path)
    assert proc.returncode == 0

    import zipfile
    with zipfile.ZipFile(str(out)) as zf:
        assert "a.txt" in zf.namelist()
        assert "folder/f.txt" in zf.namelist()


def test_auto_suffix(tmp_path):
    """Input 'a' without suffix should create a.zip"""
    src = tmp_path / "f.txt"; src.write_text("x")
    out = tmp_path / "a"
    proc = _run_with_temp(str(src), out, tmp_path)
    assert proc.returncode == 0
    # Should have created a.zip
    out_zip = tmp_path / "a.zip"
    assert out_zip.exists()
    assert not out.exists()


def test_concat_quoted_unquoted(tmp_path):
    """Handle Windows drag-drop: "quoted"unquoted (no space between)"""
    quoted = tmp_path / "my file.txt"; quoted.write_text("quoted")
    unquoted = tmp_path / "plain.txt"; unquoted.write_text("plain")

    # Simulate: "my file.txt"plain.txt with NO space between
    input_line = f'"{quoted}"{unquoted}'
    out = tmp_path / "out.zip"

    proc = _run_with_temp(input_line, out, tmp_path)
    assert proc.returncode == 0, proc.stderr

    import zipfile
    with zipfile.ZipFile(str(out)) as zf:
        names = zf.namelist()
        assert "my file.txt" in names, names
        assert "plain.txt" in names, names


def test_quoted_paths(tmp_path):
    """Paths with spaces or special chars in quotes"""
    folder = tmp_path / "my folder"
    folder.mkdir(); (folder / "f.txt").write_text("f")
    src = tmp_path / "a&b.txt"; src.write_text("special")
    out = tmp_path / "out.zip"

    input_line = f'"{src}" "{folder}"'
    proc = _run_with_temp(input_line, out, tmp_path)
    assert proc.returncode == 0, proc.stderr

    import zipfile
    with zipfile.ZipFile(str(out)) as zf:
        names = zf.namelist()
        assert "a&b.txt" in names
        assert "my folder/f.txt" in names
