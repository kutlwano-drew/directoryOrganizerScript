from __future__ import annotations
import time
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeElapsedColumn
from rich.text import Text

console = Console()

def banner():
    console.clear()
    art = Text()
    art.append("███████╗ ██████╗ ██████╗ ████████╗██╗██╗  ██╗\n", style="bold cyan")
    art.append("██╔════╝██╔═══██╗██╔══██╗╚══██╔══╝██║╚██╗██╔╝\n", style="bold cyan")
    art.append("███████╗██║   ██║██████╔╝   ██║   ██║ ╚███╔╝ \n", style="bold bright_cyan")
    art.append("╚════██║██║   ██║██╔══██╗   ██║   ██║ ██╔██╗ \n", style="bold bright_cyan")
    art.append("███████║╚██████╔╝██║  ██║   ██║   ██║██╔╝ ██╗\n", style="bold cyan")
    art.append("╚══════╝ ╚═════╝ ╚═╝  ╚═╝   ╚═╝   ╚═╝╚═╝  ╚═╝\n", style="bold cyan")
    console.print(Panel(art, subtitle="[bold white]HYBRID FILE ORGANISER  •  v3.0.0[/]", border_style="cyan"))

def title(value):
    console.print()
    console.rule(f"[bold cyan]{value}[/]")
    console.print()

def pause():
    Prompt.ask("\n[dim]Press Enter to return[/]", default="")

def ask_yes_no(message, default=False):
    return Confirm.ask(message, default=default)

def menu(title_text, options):
    title(title_text)
    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column("key", style="bold cyan", width=5)
    table.add_column("action", style="white")
    for key, label in options:
        table.add_row(f"[{key}]", label)
    console.print(Panel(table, border_style="cyan"))
    return Prompt.ask("Choose an option", choices=[x[0] for x in options], show_choices=False)

def progress_items(items, description="Processing"):
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"),
                  BarColumn(), TextColumn("{task.completed}/{task.total}"),
                  TimeElapsedColumn(), console=console) as progress:
        task = progress.add_task(description, total=len(items))
        for item in items:
            yield item
            progress.advance(task)

def flash(message, style="green"):
    console.print(Panel(message, border_style=style))
