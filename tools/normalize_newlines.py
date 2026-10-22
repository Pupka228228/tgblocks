"""Normalize line endings of the working tree to LF (the repository already is)."""
import pathlib
import subprocess

SKIP = {".git", "__pycache__", ".pytest_cache", "_edgeprofile"}
changed = 0
for path in pathlib.Path(".").rglob("*"):
    if not path.is_file():
        continue
    if any(part in SKIP or part.startswith("_edgeprofile") for part in path.parts):
        continue
    if path.suffix.lower() in {".png", ".jpg", ".jpeg", ".gif", ".ico", ".zip", ".pyc"}:
        continue
    data = path.read_bytes()
    if b"\r\n" in data:
        path.write_bytes(data.replace(b"\r\n", b"\n"))
        changed += 1
print("normalized", changed, "files")
