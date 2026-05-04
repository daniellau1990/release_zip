"""Multi-file compression helper for interactive .bat"""
import sys
from pathlib import Path

if len(sys.argv) < 3:
    sys.exit("Usage: batch_compress.py source... output_path")

*inputs, output = sys.argv[1:]
out = Path(output)
ext = out.suffix.lower()

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