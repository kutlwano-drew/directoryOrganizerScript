from __future__ import annotations
import logging
import sys
from datetime import datetime
from pathlib import Path
from collections import Counter
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeElapsedColumn
from . import __version__, database
from .config import load_config, save_config, LOG_PATH, DEFAULT_CATEGORIES
from .scanner import scan_directory, human_size, extension_summary
from .engine import build_plan, execute_plan, undo_operation, find_duplicates
from .ui import console, banner, title, menu, pause, ask_yes_no, flash
from .intelligence import directory_insights, parse_search_query, search_matches

def setup_logging():
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(filename=LOG_PATH, level=logging.INFO,
                        format="%(asctime)s %(levelname)s %(message)s")

def choose_directory(default=None):
    value = Prompt.ask("Directory path", default=str(default or Path.cwd())).strip().strip('"')
    path = Path(value).expanduser()
    if not path.exists() or not path.is_dir():
        flash("That path is not an existing directory.", "red")
        return None
    return path.resolve()

def remember_directory(cfg, path):
    value = str(Path(path).resolve())
    recent = [x for x in cfg.get("recent_directories", []) if x != value]
    cfg["recent_directories"] = [value] + recent[:9]
    save_config(cfg)

def scan_with_feedback(path, cfg):
    try:
        with console.status("[bold cyan]Scanning directory…[/]", spinner="dots"):
            excluded = list(cfg.get("exclude_directories", [])) + list(cfg.get("categories", {}).keys()) + ["Others"]
        result = scan_directory(path, cfg.get("recursive", False), excluded)
        return result
    except Exception as exc:
        logging.exception("Scan failed")
        flash(f"Scan failed: {exc}", "red")
        return None

def show_scan(result):
    table = Table(title="Directory overview", border_style="cyan")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", justify="right")
    table.add_row("Directory", str(result.root))
    table.add_row("Files", str(len(result.files)))
    table.add_row("Subdirectories", str(result.folders))
    table.add_row("Total size", human_size(result.total_bytes))
    console.print(table)
    counts = extension_summary(result.files)
    ext_table = Table(title="Most common file extensions", border_style="blue")
    ext_table.add_column("Extension")
    ext_table.add_column("Count", justify="right")
    for ext, count in counts.most_common(15):
        ext_table.add_row(ext, str(count))
    console.print(ext_table)

def organise_flow(cfg):
    title("Organise files")
    path = choose_directory(cfg.get("recent_directories", [None])[0] if cfg.get("recent_directories") else None)
    if path is None:
        return
    remember_directory(cfg, path)
    result = scan_with_feedback(path, cfg)
    if result is None:
        return
    plan, skipped = build_plan(result.files, path, cfg)
    counts = Counter(item.category for item in plan)
    table = Table(title="Proposed organisation", border_style="cyan")
    table.add_column("Destination category")
    table.add_column("Files", justify="right")
    for category, count in sorted(counts.items()):
        table.add_row(category, str(count))
    console.print(table)
    console.print(f"\n[bold]Planned moves:[/] {len(plan)}    [yellow]Skipped:[/] {len(skipped)}")
    if skipped:
        console.print("[dim]Skipped examples: " + ", ".join(f"{p.name} ({reason})" for p, reason in skipped[:5]) + "[/]")
    if plan and ask_yes_no("Inspect proposed files by category before continuing?", default=False):
        categories = sorted(counts)
        for idx, category in enumerate(categories, 1):
            console.print(f"{idx}. {category} ({counts[category]} files)")
        try:
            selected_category = categories[int(Prompt.ask("Category number"))-1]
            detail = Table(title=f"Preview: {selected_category}", border_style="yellow")
            detail.add_column("Source file"); detail.add_column("Destination")
            for item in [x for x in plan if x.category == selected_category][:200]:
                detail.add_row(str(item.source), str(item.destination))
            console.print(detail)
            if ask_yes_no("Organise only this category?", default=False):
                plan = [x for x in plan if x.category == selected_category]
                counts = Counter(item.category for item in plan)
        except (ValueError, IndexError):
            flash("Invalid category selection. Keeping the complete plan.", "yellow")
    if not plan:
        flash("Nothing needs to be moved.", "yellow")
        pause()
        return
    if not ask_yes_no("Proceed with these file movements?", default=False):
        flash("Operation cancelled. No files were moved.", "yellow")
        pause()
        return
    errors_seen = []
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"),
                  BarColumn(), TextColumn("{task.completed}/{task.total}"), TimeElapsedColumn(),
                  console=console) as progress:
        task = progress.add_task("Moving files", total=len(plan))
        op_id, moved, skipped_count, errors = execute_plan(
            plan, path, errors_seen.append, lambda _item: progress.advance(task)
        )
    logging.info("Operation %s: moved=%s errors=%s root=%s", op_id, moved, errors, path)
    console.print(Panel(
        f"[green]Moved:[/] {moved}\n[yellow]Skipped:[/] {len(skipped) + skipped_count}\n[red]Errors:[/] {errors}\n[dim]Operation ID: {op_id}[/]",
        title="Organisation complete", border_style="green" if not errors else "yellow"))
    if errors_seen:
        for message in errors_seen[:8]:
            console.print(f"[red]• {message}[/]")
    if ask_yes_no("Would you like to undo this operation now?", default=False):
        restored, conflicts, undo_errors = undo_operation(op_id)
        flash(f"Restored: {restored}   Conflicts: {conflicts}   Errors: {undo_errors}")
    pause()

def analyse_flow(cfg):
    title("Directory analysis")
    path = choose_directory(cfg.get("recent_directories", [None])[0] if cfg.get("recent_directories") else None)
    if path is None:
        return
    remember_directory(cfg, path)
    result = scan_with_feedback(path, cfg)
    if result:
        show_scan(result)
        insights = directory_insights(result)
        console.print(Panel(f"[bold]Largest file:[/] {insights['largest_file'].name if insights['largest_file'] else 'None'} ({human_size(insights['largest_bytes'])} )\n[bold]Files older than 1 year:[/] {len(insights['old_files'])}\n[bold]Empty directories:[/] {len(insights['empty_dirs'])}", title="Directory intelligence", border_style="magenta"))
        if insights["largest"]:
            large_table = Table(title="Largest files (top 10)", border_style="yellow")
            large_table.add_column("Size", justify="right")
            large_table.add_column("File")
            for size, file_path in insights["largest"]:
                large_table.add_row(human_size(size), str(file_path))
            console.print(large_table)
        pause()

def category_manager(cfg):
    while True:
        options = [("1", "List categories"), ("2", "Create category"), ("3", "Edit category extensions"),
                   ("4", "Delete category"), ("5", "Restore default categories"), ("0", "Back")]
        choice = menu("Category manager", options)
        cats = cfg["categories"]
        if choice == "0":
            return
        if choice == "1":
            table = Table(title="Configured categories", border_style="cyan")
            table.add_column("Category")
            table.add_column("Extensions")
            for name, exts in cats.items():
                table.add_row(name, ", ".join(exts))
            console.print(table)
            pause()
        elif choice == "2":
            name = Prompt.ask("New category name").strip()
            if not name or name in cats or name in (".", "..") or "/" in name or "\\" in name:
                flash("Invalid or duplicate category name.", "red")
                continue
            exts = [x.strip().lower() for x in Prompt.ask("Extensions, comma-separated (e.g. .log,.ini)").split(",") if x.strip()]
            exts = [x if x.startswith(".") else "." + x for x in exts]
            if not exts:
                flash("At least one extension is required.", "red")
                continue
            cats[name] = sorted(set(exts))
            save_config(cfg)
            flash(f"Category '{name}' created.")
        elif choice == "3":
            names = list(cats)
            for i, name in enumerate(names, 1):
                console.print(f"{i}. {name}")
            try:
                idx = int(Prompt.ask("Category number")) - 1
                name = names[idx]
            except (ValueError, IndexError):
                flash("Invalid selection.", "red")
                continue
            exts = [x.strip().lower() for x in Prompt.ask("Replace extensions with comma-separated values").split(",") if x.strip()]
            cats[name] = sorted(set(x if x.startswith(".") else "." + x for x in exts))
            save_config(cfg)
            flash(f"Updated {name}.")
        elif choice == "4":
            names = list(cats)
            for i, name in enumerate(names, 1):
                console.print(f"{i}. {name}")
            try:
                idx = int(Prompt.ask("Category number")) - 1
                name = names[idx]
            except (ValueError, IndexError):
                flash("Invalid selection.", "red")
                continue
            if ask_yes_no(f"Delete category '{name}'? Files already inside it will not be deleted.", default=False):
                del cats[name]
                save_config(cfg)
                flash("Category deleted.")
        elif choice == "5":
            if ask_yes_no("Replace all category mappings with factory defaults?", default=False):
                cfg["categories"] = {k: list(v) for k, v in DEFAULT_CATEGORIES.items()}
                save_config(cfg)
                flash("Default categories restored.")

def settings_flow(cfg):
    while True:
        choice = menu("Settings", [
            ("1", f"Recursive scanning: {'ON' if cfg.get('recursive') else 'OFF'}"),
            ("2", f"Move unknown files to Others: {'ON' if cfg.get('move_unknown_to_others', True) else 'OFF'}"),
            ("3", "Manage excluded extensions"),
            ("4", "Manage excluded filenames"),
            ("5", "Manage excluded directory names"),
            ("6", "Export configuration"),
            ("7", "Restore all settings"),
            ("0", "Back")
        ])
        if choice == "0":
            return
        if choice == "1":
            cfg["recursive"] = not cfg.get("recursive", False)
        elif choice == "2":
            cfg["move_unknown_to_others"] = not cfg.get("move_unknown_to_others", True)
        elif choice in ("3", "4", "5"):
            key = {"3": "exclude_extensions", "4": "exclude_names", "5": "exclude_directories"}[choice]
            console.print(f"Current values: {', '.join(cfg.get(key, [])) or '(none)'}")
            raw = Prompt.ask("Enter comma-separated values (leave blank to clear)", default="")
            cfg[key] = [x.strip() for x in raw.split(",") if x.strip()]
            if key == "exclude_extensions":
                cfg[key] = [x.lower() if x.startswith(".") else "." + x.lower() for x in cfg[key]]
        elif choice == "6":
            destination = Path(Prompt.ask("Export file path", default=str(Path.cwd() / "hybrid_file_organiser-config.json"))).expanduser()
            import json
            destination.write_text(json.dumps(cfg, indent=2), encoding="utf-8")
            flash(f"Configuration exported to {destination}")
        elif choice == "7":
            from .config import default_config
            if ask_yes_no("Restore every setting and category to defaults?", default=False):
                cfg.clear()
                cfg.update(default_config())
                flash("Settings restored.")
        save_config(cfg)

def search_flow(cfg):
    title("File search")
    path = choose_directory(cfg.get("recent_directories", [None])[0] if cfg.get("recent_directories") else None)
    if path is None:
        return
    remember_directory(cfg, path)
    query = Prompt.ask("Search query (supports ext:pdf size:>10mb modified:30d name:invoice)").strip()
    result = scan_with_feedback(path, {**cfg, "recursive": True})
    if not result:
        return
    filters = parse_search_query(query)
    matches = [p for p in result.files if search_matches(p, filters)]
    table = Table(title=f"Search results ({len(matches)})", border_style="cyan")
    table.add_column("Filename")
    table.add_column("Location")
    table.add_column("Size", justify="right")
    for p in matches[:200]:
        try: size = human_size(p.stat().st_size)
        except OSError: size = "Unavailable"
        table.add_row(p.name, str(p.parent), size)
    console.print(table)
    if len(matches) > 200:
        console.print("[dim]Showing first 200 results.[/]")
    if matches and ask_yes_no("Inspect a file's actions?", default=False):
        try:
            index = int(Prompt.ask(f"Result number (1-{min(len(matches),200)})")) - 1
            selected = matches[index]
            action = menu(f"Selected: {selected.name}", [("1", "Show metadata"), ("2", "Open containing folder"), ("3", "Copy path to clipboard (print path)"),("0", "Back")])
            if action == "1":
                stat = selected.stat()
                console.print(Panel(f"Path: {selected}\nSize: {human_size(stat.st_size)}\nModified: {datetime.fromtimestamp(stat.st_mtime)}\nExtension: {selected.suffix or '(none)' }", title="File metadata"))
            elif action == "2":
                import os, subprocess
                if sys.platform.startswith("win"): os.startfile(str(selected.parent))
                elif sys.platform == "darwin": subprocess.Popen(["open", str(selected.parent)])
                else: subprocess.Popen(["xdg-open", str(selected.parent)])
            elif action == "3": console.print(str(selected))
        except (ValueError, IndexError, OSError) as exc: flash(f"Could not inspect selection: {exc}", "yellow")
    pause()

def duplicates_flow(cfg):
    title("Duplicate finder")
    path = choose_directory()
    if path is None:
        return
    result = scan_with_feedback(path, {**cfg, "recursive": True})
    if not result:
        return
    with console.status("[bold cyan]Comparing file sizes and SHA-256 hashes…[/]", spinner="dots"):
        groups = find_duplicates(result.files)
    if not groups:
        flash("No identical files were found.")
    else:
        for number, group in enumerate(groups, 1):
            size = 0
            try: size = group[0].stat().st_size
            except OSError: pass
            console.print(Panel(f"Group size: {human_size(size)}\nPotentially reclaimable: {human_size(size * (len(group)-1))}\n" + "\n".join(str(p) for p in group), title=f"Duplicate group {number}", border_style="yellow"))
        console.print("[yellow]HYBRID FILE ORGANISER does not automatically delete duplicates. Review them manually.[/]")
    pause()

def history_flow():
    title("Operation history")
    rows = database.history()
    table = Table(border_style="cyan")
    table.add_column("ID")
    table.add_column("Date")
    table.add_column("Directory")
    table.add_column("Moved", justify="right")
    table.add_column("Errors", justify="right")
    table.add_column("Status")
    for row in rows:
        table.add_row(str(row["id"]), row["created_at"], row["source_root"], str(row["moved"]), str(row["errors"]), row["status"])
    console.print(table if rows else "[dim]No operations recorded yet.[/]")
    if len(rows) >= 2 and ask_yes_no("Compare two recent operations?", default=False):
        try:
            first = int(Prompt.ask("First operation ID", default=str(rows[0]["id"])))
            second = int(Prompt.ask("Second operation ID", default=str(rows[1]["id"])))
            selected = [next(r for r in rows if int(r["id"]) == first), next(r for r in rows if int(r["id"]) == second)]
            comparison = Table(title="Operation comparison", border_style="magenta")
            comparison.add_column("Metric"); comparison.add_column(f"#{first}",justify="right"); comparison.add_column(f"#{second}",justify="right")
            for key,label in [("moved","Moved"),("skipped","Skipped"),("errors","Errors"),("status","Status"),("created_at","Date")]:
                comparison.add_row(label,str(selected[0][key]),str(selected[1][key]))
            console.print(comparison)
        except (ValueError, StopIteration): flash("Could not compare those operation IDs.", "yellow")
    if rows and ask_yes_no("Undo an operation?", default=False):
        op_id = Prompt.ask("Enter operation ID", default=str(rows[0]["id"]))
        try:
            restored, conflicts, errors = undo_operation(int(op_id))
            flash(f"Restored {restored}; conflicts {conflicts}; errors {errors}.")
        except ValueError:
            flash("Invalid operation ID.", "red")
    pause()

def rename_flow():
    title("Batch rename")
    path = choose_directory()
    if path is None:
        return
    files = [p for p in path.iterdir() if p.is_file()]
    if not files:
        flash("No files found in this directory.", "yellow")
        pause()
        return
    prefix = Prompt.ask("Prefix to add (blank for none)", default="")
    suffix = Prompt.ask("Suffix to add before extension (blank for none)", default="")
    preview = []
    for p in files:
        new = p.with_name(prefix + p.stem + suffix + p.suffix)
        if new != p:
            preview.append((p, new))
    table = Table(title=f"Rename preview ({len(preview)} files)", border_style="cyan")
    table.add_column("Current name")
    table.add_column("New name")
    for old, new in preview[:50]:
        table.add_row(old.name, new.name)
    console.print(table)
    if len(preview) > 50:
        console.print("[dim]Showing first 50 changes.[/]")
    if preview and ask_yes_no("Apply these renames?", default=False):
        changed = 0
        for old, new in preview:
            if not new.exists():
                old.rename(new)
                changed += 1
        flash(f"Renamed {changed} files. Conflicting names were skipped.")
    pause()

def large_files_flow(cfg):
    title("Large file explorer")
    path = choose_directory(cfg.get("recent_directories", [None])[0] if cfg.get("recent_directories") else None)
    if not path: return
    remember_directory(cfg, path)
    result = scan_with_feedback(path, {**cfg, "recursive": True})
    if not result: return
    raw = Prompt.ask("Minimum file size", default="100mb").lower().strip()
    units = {"tb":1024**4,"gb":1024**3,"mb":1024**2,"kb":1024,"b":1}
    number, unit = raw, "b"
    for u in units:
        if raw.endswith(u): number, unit = raw[:-len(u)], u; break
    try: minimum = float(number) * units[unit]
    except ValueError: flash("Invalid size. Example: 100mb", "red"); pause(); return
    rows=[]
    for file in result.files:
        try:
            size=file.stat().st_size
            if size >= minimum: rows.append((size,file))
        except OSError: pass
    rows.sort(reverse=True,key=lambda x:x[0])
    table=Table(title=f"Large files ({len(rows)})",border_style="yellow")
    table.add_column("Size",justify="right"); table.add_column("Path")
    for size,file in rows[:250]: table.add_row(human_size(size),str(file))
    console.print(table); pause()


def empty_directories_flow(cfg):
    title("Empty directory finder")
    path=choose_directory(cfg.get("recent_directories", [None])[0] if cfg.get("recent_directories") else None)
    if not path: return
    remember_directory(cfg,path)
    empty=[]
    for current, dirs, files in __import__('os').walk(path):
        dirs[:] = [d for d in dirs if d not in cfg.get("exclude_directories", [])]
        try:
            if not dirs and not files: empty.append(Path(current))
        except OSError: pass
    table=Table(title=f"Empty directories ({len(empty)})",border_style="cyan")
    table.add_column("Directory path")
    for folder in empty[:250]: table.add_row(str(folder))
    console.print(table)
    console.print("[yellow]Read-only finder: no directories are removed.[/]")
    pause()


def favourites_flow(cfg):
    while True:
        favs=cfg.setdefault("favorites",[])
        opts=[("1","Add favourite directory"),("2","Open favourite directory"),("3","Remove favourite") ,("0","Back")]
        choice=menu("Favourite directories",opts)
        if choice=="0": return
        if choice=="1":
            path=choose_directory()
            if path and str(path) not in favs: favs.append(str(path)); save_config(cfg); flash("Favourite added.")
        elif choice=="2":
            if not favs: flash("No favourites yet.","yellow"); continue
            for i,p in enumerate(favs,1): console.print(f"{i}. {p}")
            try:
                selected=Path(favs[int(Prompt.ask("Favourite number"))-1])
                if selected.exists():
                    import os, subprocess
                    if sys.platform.startswith("win"): os.startfile(str(selected))
                    elif sys.platform=="darwin": subprocess.Popen(["open",str(selected)])
                    else: subprocess.Popen(["xdg-open",str(selected)])
                else: flash("That favourite path no longer exists.","yellow")
            except (ValueError,IndexError): flash("Invalid choice.","red")
        elif choice=="3":
            if not favs: flash("No favourites to remove.","yellow"); continue
            for i,p in enumerate(favs,1): console.print(f"{i}. {p}")
            try: del favs[int(Prompt.ask("Favourite number"))-1]; save_config(cfg); flash("Favourite removed.")
            except (ValueError,IndexError): flash("Invalid choice.","red")


def profiles_flow(cfg):
    while True:
        profiles=cfg.setdefault("profiles",{"Default":{}})
        choice=menu("Organisation profiles",[("1","List profiles"),("2","Save current settings as profile"),("3","Activate profile"),("4","Delete profile"),("0","Back")])
        if choice=="0": return
        if choice=="1":
            for name,profile in profiles.items(): console.print(f"{'*' if name==cfg.get('active_profile') else ' '} {name} — {len(profile.get('categories',cfg.get('categories',{})))} categories")
            pause()
        elif choice=="2":
            name=Prompt.ask("Profile name").strip()
            if not name or name in profiles: flash("Name is empty or already exists.","red"); continue
            profiles[name]={"categories":cfg.get("categories",{}),"exclude_extensions":cfg.get("exclude_extensions",[]),"exclude_names":cfg.get("exclude_names",[]),"exclude_directories":cfg.get("exclude_directories",[]),"recursive":cfg.get("recursive",False),"move_unknown_to_others":cfg.get("move_unknown_to_others",True)}
            cfg["active_profile"]=name; save_config(cfg); flash(f"Profile '{name}' saved.")
        elif choice=="3":
            names=list(profiles)
            for i,n in enumerate(names,1): console.print(f"{i}. {n}")
            try:
                selected_name=names[int(Prompt.ask("Profile number"))-1]
                profile=profiles[selected_name]
                for key in ["categories","exclude_extensions","exclude_names","exclude_directories","recursive","move_unknown_to_others"]:
                    if key in profile: cfg[key]=profile[key]
                cfg["active_profile"]=selected_name; save_config(cfg); flash(f"Activated {cfg['active_profile']}.")
            except (ValueError,IndexError): flash("Invalid profile.","red")
        elif choice=="4":
            names=[n for n in profiles if n!="Default"]
            if not names: flash("No custom profiles.","yellow"); continue
            for i,n in enumerate(names,1): console.print(f"{i}. {n}")
            try:
                removed=names[int(Prompt.ask("Profile number"))-1]
                del profiles[removed]
                if cfg.get("active_profile")==removed:
                    cfg["active_profile"]="Default"
                    for key in ["categories","exclude_extensions","exclude_names","exclude_directories","recursive","move_unknown_to_others"]:
                        if key in profiles.get("Default",{}): cfg[key]=profiles["Default"][key]
                save_config(cfg); flash("Profile deleted.")
            except (ValueError,IndexError): flash("Invalid profile.","red")


def command_palette(cfg):
    query=Prompt.ask("Command palette — search actions (e.g. analyse, large, favourites, profiles)").strip().lower()
    actions={"organise":organise_flow,"analyse":analyse_flow,"category":category_manager,"search":search_flow,"duplicate":duplicates_flow,"rename":rename_flow,"history":history_flow,"settings":settings_flow,"large":large_files_flow,"empty":empty_directories_flow,"favourite":faves_wrapper,"profile":profiles_flow}
    for keyword,func in actions.items():
        if keyword in query:
            func(cfg) if func not in (rename_flow,history_flow) else func()
            return
    flash("No matching action. Try: organise, analyse, category, search, duplicate, rename, history, settings, large, empty, favourites, profiles.","yellow")
    pause()


def faves_wrapper(cfg):
    favourites_flow(cfg)



def dashboard(cfg):
    while True:
        banner()
        console.print(Panel(
            f"[bold white]Version[/] {__version__}     [bold white]Profile[/] {cfg.get('active_profile','Default')}\n"
            f"[bold white]Categories[/] {len(cfg['categories'])}     [bold white]Recursive scan[/] {'ON' if cfg.get('recursive') else 'OFF'}\n"
            f"[dim]Configuration: ~/.hybrid_file_organiser/config.json[/]",
            title="SYSTEM STATUS", border_style="cyan"))
        choice = menu("Main menu", [
            ("1", "Organise files"),
            ("2", "Analyse a directory"),
            ("3", "Manage categories"),
            ("4", "Search files"),
            ("5", "Find duplicate files"),
            ("6", "Batch rename files"),
            ("7", "Operation history & undo"),
            ("8", "Settings & exclusions"),
            ("9", "Help & safety guide"),
            ("10", "Large file explorer"),
            ("11", "Empty directory finder"),
            ("12", "Favourite directories"),
            ("13", "Organisation profiles"),
            ("14", "Command palette"),
            ("0", "Exit HYBRID FILE ORGANISER")
        ])
        if choice == "1": organise_flow(cfg)
        elif choice == "2": analyse_flow(cfg)
        elif choice == "3": category_manager(cfg)
        elif choice == "4": search_flow(cfg)
        elif choice == "5": duplicates_flow(cfg)
        elif choice == "6": rename_flow()
        elif choice == "7": history_flow()
        elif choice == "8": settings_flow(cfg)
        elif choice == "10": large_files_flow(cfg)
        elif choice == "11": empty_directories_flow(cfg)
        elif choice == "12": favourites_flow(cfg)
        elif choice == "13": profiles_flow(cfg)
        elif choice == "14": command_palette(cfg)
        elif choice == "9":
            title("Help & safety")
            console.print(Panel(
                "• Always review the organisation preview before confirming.\n"
                "• HYBRID FILE ORGANISER never silently overwrites an existing destination file; it adds a numbered suffix.\n"
                "• Each completed organisation operation is recorded in a local SQLite journal.\n"
                "• Undo restores files where their original paths are available; conflicts are left untouched.\n"
                "• Duplicate detection is read-only. It never deletes files.\n"
                "• Recursive scanning is OFF by default. Enable it in Settings when needed.\n"
                "• Configuration, history and logs are stored under ~/.hybrid_file_organiser/.",
                title="Important information", border_style="yellow"))
            pause()
        elif choice == "0":
            if ask_yes_no("Exit HYBRID FILE ORGANISER?", default=True):
                console.print("[bold cyan]Thanks for using HYBRID FILE ORGANISER. Stay organised![/]")
                return

def main():
    setup_logging()
    cfg = load_config()
    try:
        running = [row for row in database.history(100) if row["status"] == "running"]
        if running:
            console.print(Panel(f"[yellow]Potential interrupted operations detected: {len(running)}. Review Operation history before new moves.[/yellow]", title="Recovery notice", border_style="yellow"))
        dashboard(cfg)
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted. HYBRID FILE ORGANISER is closing safely.[/]")
    except Exception as exc:
        logging.exception("Unexpected application error")
        console.print(f"[bold red]Unexpected error:[/] {exc}")
        console.print(f"[dim]See log: {LOG_PATH}[/]")
        raise
