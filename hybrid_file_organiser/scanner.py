from __future__ import annotations
from pathlib import Path
from dataclasses import dataclass
from collections import Counter

@dataclass
class ScanResult:
    root: Path
    files: list
    folders: int
    total_bytes: int
    errors: list

def scan_directory(root, recursive=False, excluded_dirs=None):
    root = Path(root).expanduser().resolve()
    excluded = set(excluded_dirs or [])
    found, errors, folders, total = [], [], 0, 0
    if not root.is_dir():
        raise NotADirectoryError(str(root))
    if recursive:
        for current, dirs, names in __import__("os").walk(root):
            dirs[:] = [d for d in dirs if d not in excluded]
            folders += len(dirs)
            for name in names:
                p = Path(current) / name
                try:
                    if p.is_symlink() or not p.is_file():
                        continue
                    size = p.stat().st_size
                    found.append(p)
                    total += size
                except OSError as exc:
                    errors.append(f"{p}: {exc}")
    else:
        for p in root.iterdir():
            try:
                if p.is_dir():
                    folders += 1
                elif p.is_file() and not p.is_symlink():
                    found.append(p)
                    total += p.stat().st_size
            except OSError as exc:
                errors.append(f"{p}: {exc}")
    return ScanResult(root, found, folders, total, errors)

def human_size(value):
    size = float(value)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if size < 1024 or unit == "TB":
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} TB"

def extension_summary(paths):
    counts = Counter((p.suffix.lower() or "[no extension]") for p in paths)
    return counts
