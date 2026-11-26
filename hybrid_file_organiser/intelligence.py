"""Local, read-only filesystem intelligence helpers for HYBRID."""
from __future__ import annotations
from pathlib import Path
from datetime import datetime, timedelta
from collections import Counter
from .scanner import human_size


def directory_insights(result):
    files = result.files
    extensions = Counter((p.suffix.lower() or "[no extension]") for p in files)
    sizes = []
    old_files = []
    now = datetime.now().timestamp()
    empty_dirs = []
    try:
        for current, dirs, names in __import__('os').walk(result.root):
            dirs[:] = [d for d in dirs if d not in {'.git', '__pycache__'}]
            if not dirs and not names:
                empty_dirs.append(Path(current))
    except OSError:
        pass
    for p in files:
        try:
            stat = p.stat()
            sizes.append((stat.st_size, p))
            if now - stat.st_mtime > 365 * 86400:
                old_files.append(p)
        except OSError:
            continue
    sizes.sort(reverse=True, key=lambda x: x[0])
    duplicate_bytes = 0
    return {
        "extensions": extensions, "largest": sizes[:10], "old_files": old_files,
        "empty_dirs": empty_dirs, "largest_bytes": sizes[0][0] if sizes else 0,
        "largest_file": sizes[0][1] if sizes else None,
        "uncategorized": extensions.get('[no extension]', 0),
    }


def parse_search_query(query: str):
    """Parse simple search tokens: ext:pdf size:>10mb modified:30d name:invoice."""
    filters = {"terms": [], "ext": None, "size": None, "modified_days": None, "name": None}
    for token in query.split():
        low = token.lower()
        if low.startswith("ext:"):
            filters["ext"] = low[4:].lstrip('.')
        elif low.startswith("size:"):
            filters["size"] = low[5:]
        elif low.startswith("modified:"):
            raw = low[9:].rstrip('d')
            try: filters["modified_days"] = int(raw)
            except ValueError: pass
        elif low.startswith("name:"):
            filters["name"] = token[5:].casefold()
        else:
            filters["terms"].append(low)
    return filters


def search_matches(path: Path, filters: dict):
    try:
        stat = path.stat()
    except OSError:
        return False
    if filters["ext"] and path.suffix.lower().lstrip('.') != filters["ext"]:
        return False
    if filters["name"] and filters["name"] not in path.name.casefold():
        return False
    if filters["terms"] and not all(term in path.name.casefold() for term in filters["terms"]):
        return False
    if filters["modified_days"] is not None and stat.st_mtime < (datetime.now().timestamp() - filters["modified_days"] * 86400):
        return False
    if filters["size"]:
        raw = filters["size"]
        op = raw[0] if raw and raw[0] in '<>=' else '='
        amount = raw[1:] if op != '=' else raw
        multiplier = 1
        for suffix, factor in [('tb',1024**4),('gb',1024**3),('mb',1024**2),('kb',1024),('b',1)]:
            if amount.endswith(suffix):
                amount = amount[:-len(suffix)]; multiplier = factor; break
        try: limit = float(amount) * multiplier
        except ValueError: return False
        if op == '>' and not stat.st_size > limit: return False
        if op == '<' and not stat.st_size < limit: return False
        if op == '=' and not stat.st_size == limit: return False
    return True
