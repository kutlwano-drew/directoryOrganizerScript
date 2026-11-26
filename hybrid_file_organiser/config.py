from __future__ import annotations
import json
from pathlib import Path
from copy import deepcopy

DEFAULT_CATEGORIES = {
    "Documents": [".pdf", ".doc", ".docx", ".txt", ".odt", ".rtf"],
    "Videos": [".mp4", ".mov", ".avi", ".mkv", ".flv", ".webm"],
    "Audio": [".mp3", ".wav", ".aac", ".flac", ".ogg", ".m4a"],
    "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".tiff"],
    "Archives": [".zip", ".tar", ".gz", ".rar", ".7z", ".bz2", ".xz"],
    "Scripts": [".py", ".js", ".sh", ".bat", ".ps1", ".rb"],
    "Spreadsheets": [".xls", ".xlsx", ".ods", ".csv"],
    "Presentations": [".ppt", ".pptx", ".odp"],
    "Fonts": [".ttf", ".otf", ".woff", ".woff2"],
    "Databases": [".db", ".sqlite", ".sqlite3"],
}

APP_DIR = Path.home() / ".hybrid_file_organiser"
CONFIG_PATH = APP_DIR / "config.json"
DB_PATH = APP_DIR / "history.sqlite3"
LOG_PATH = APP_DIR / "hybrid_file_organiser.log"

def default_config():
    return {
        "categories": deepcopy(DEFAULT_CATEGORIES),
        "exclude_extensions": [],
        "exclude_names": [],
        "exclude_directories": [".git", "__pycache__", ".hybrid_file_organiser"],
        "theme": "cyan",
        "animations": True,
        "recursive": False,
        "move_unknown_to_others": True,
        "confirm_before_move": True,
        "profiles": {"Default": {}},
        "active_profile": "Default",
        "favorites": [],
        "recent_directories": [],
        "version": 2,
    }

def load_config():
    APP_DIR.mkdir(parents=True, exist_ok=True)
    if not CONFIG_PATH.exists():
        cfg = default_config()
        save_config(cfg)
        return cfg
    try:
        data = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        base = default_config()
        base.update(data)
        base["favorites"] = list(dict.fromkeys(str(x) for x in base.get("favorites", []) if x))
        base["recent_directories"] = list(dict.fromkeys(str(x) for x in base.get("recent_directories", []) if x))[:10]
        profiles = base.setdefault("profiles", {"Default": {}})
        profiles.setdefault("Default", {})
        if not profiles["Default"]:
            profiles["Default"] = {key: deepcopy(base.get(key)) for key in ["categories", "exclude_extensions", "exclude_names", "exclude_directories", "recursive", "move_unknown_to_others"]}
        if not isinstance(base.get("categories"), dict):
            base["categories"] = deepcopy(DEFAULT_CATEGORIES)
        return base
    except (OSError, json.JSONDecodeError):
        broken = CONFIG_PATH.with_suffix(".corrupt.json")
        try:
            CONFIG_PATH.replace(broken)
        except OSError:
            pass
        cfg = default_config()
        save_config(cfg)
        return cfg

def save_config(cfg):
    APP_DIR.mkdir(parents=True, exist_ok=True)
    tmp = CONFIG_PATH.with_suffix(".tmp")
    tmp.write_text(json.dumps(cfg, indent=2), encoding="utf-8")
    tmp.replace(CONFIG_PATH)
