from __future__ import annotations
import hashlib
import shutil
from pathlib import Path
from dataclasses import dataclass
from . import database

@dataclass
class PlanItem:
    source: Path
    destination: Path
    category: str
    reason: str

def sha256_file(path):
    digest = hashlib.sha256()
    with open(path, "rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()

def category_for(path, categories):
    ext = path.suffix.lower()
    for category, extensions in categories.items():
        if ext in [x.lower() for x in extensions]:
            return category
    return "Others"

def build_plan(paths, root, config):
    root = Path(root)
    categories = config["categories"]
    excluded_ext = {x.lower() for x in config.get("exclude_extensions", [])}
    excluded_names = set(config.get("exclude_names", []))
    plan, skipped = [], []
    for source in paths:
        if source.name in excluded_names or source.suffix.lower() in excluded_ext:
            skipped.append((source, "Excluded by settings"))
            continue
        category = category_for(source, categories)
        if category == "Others" and not config.get("move_unknown_to_others", True):
            skipped.append((source, "Unrecognised extension"))
            continue
        destination_dir = root / category
        if source.parent == destination_dir:
            skipped.append((source, "Already in destination category"))
            continue
        plan.append(PlanItem(source, destination_dir / source.name, category, "Extension match" if category != "Others" else "Unrecognised extension"))
    return plan, skipped

def unique_destination(path):
    if not path.exists():
        return path
    stem, suffix = path.stem, path.suffix
    for number in range(1, 10000):
        candidate = path.with_name(f"{stem} ({number}){suffix}")
        if not candidate.exists():
            return candidate
    raise FileExistsError(f"Could not find a free destination name for {path}")

def execute_plan(plan, root, progress=None, progress_callback=None):
    op_id = database.create_operation(root)
    moved = skipped = errors = 0
    for item in plan:
        try:
            item.destination.parent.mkdir(parents=True, exist_ok=True)
            destination = unique_destination(item.destination)
            digest = sha256_file(item.source)
            shutil.move(str(item.source), str(destination))
            database.add_move(op_id, item.source, destination, digest)
            moved += 1
        except (OSError, shutil.Error) as exc:
            errors += 1
            if progress:
                progress(f"Could not move {item.source.name}: {exc}")
        finally:
            if progress_callback:
                progress_callback(item)
    database.finish_operation(op_id, moved, skipped, errors, "complete" if errors == 0 else "completed_with_errors")
    return op_id, moved, skipped, errors

def undo_operation(op_id):
    rows = database.moves_for(op_id, only_not_undone=True)
    restored, conflicts, errors = 0, 0, 0
    for row in rows:
        current = Path(row["destination"])
        original = Path(row["source"])
        try:
            if not current.exists():
                errors += 1
                continue
            if original.exists():
                conflicts += 1
                continue
            original.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(current), str(original))
            database.mark_undone(row["id"])
            restored += 1
        except OSError:
            errors += 1
    return restored, conflicts, errors

def find_duplicates(paths):
    by_size = {}
    for path in paths:
        try:
            size = path.stat().st_size
            by_size.setdefault(size, []).append(path)
        except OSError:
            continue
    groups = []
    for same_size in by_size.values():
        if len(same_size) < 2:
            continue
        hashes = {}
        for path in same_size:
            try:
                hashes.setdefault(sha256_file(path), []).append(path)
            except OSError:
                pass
        groups.extend(group for group in hashes.values() if len(group) > 1)
    return groups
