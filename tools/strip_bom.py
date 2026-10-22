"""Strip UTF-8 BOMs that editors on Windows like to add."""
import pathlib

SKIP = {".git", "__pycache__", ".pytest_cache"}
fixed = []
for path in pathlib.Path(".").rglob("*"):
    if not path.is_file() or any(part in SKIP for part in path.parts):
        continue
    if path.suffix.lower() in {".png", ".jpg", ".jpeg", ".gif", ".ico", ".zip", ".pyc"}:
        continue
    data = path.read_bytes()
    if data.startswith(b"\xef\xbb\xbf"):
        path.write_bytes(data[3:])
        fixed.append(str(path))
print("stripped BOM from:", fixed)
