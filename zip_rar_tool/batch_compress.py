"""Multi-file compression. Args: output_path [input_file]"""
import sys
import re
from pathlib import Path

if len(sys.argv) < 2:
    sys.exit("Usage: batch_compress.py output_path [input_file]")

output = sys.argv[1]
out = Path(output)

# Read file list from temp file (argv[2]) or stdin
if len(sys.argv) >= 3:
    with open(sys.argv[2], encoding="utf-8") as f:
        content = f.read()
else:
    content = sys.stdin.read()

content = content.strip()
if not content:
    sys.exit("No input files provided")

# Split by regex: handles both space-separated and "quoted"adjacent paths
raw_tokens = re.findall(r'"[^"]*"|\S+', content)
inputs = [t.strip('"') for t in raw_tokens if t.strip('"')]

if not inputs:
    sys.exit("No valid input files")

# Auto-append .zip when no suffix
ext = out.suffix.lower()
if not ext:
    output += ".zip"
    out = Path(output)
    ext = ".zip"

if ext == ".zip":
    import zipfile
    with zipfile.ZipFile(str(out), "w", zipfile.ZIP_DEFLATED) as zf:
        for src in inputs:
            p = Path(src)
            if not p.exists():
                print(f"Skipping (not found): {src}")
                continue
            if p.is_dir():
                for f in p.rglob("*"):
                    if f.is_file():
                        zf.write(str(f), str(f.relative_to(p.parent)))
            else:
                zf.write(str(p), p.name)

elif ext == ".7z":
    import py7zr
    with py7zr.SevenZipFile(str(out), "w") as sz:
        for src in inputs:
            p = Path(src)
            if not p.exists():
                print(f"Skipping (not found): {src}")
                continue
            if p.is_dir():
                sz.writeall(str(p), arcname=p.name)
            else:
                sz.write(str(p), p.name)

else:
    sys.exit(f"Unsupported format: {ext}. Use .zip or .7z")

print(f"Created {output} with {len(inputs)} source(s)")
