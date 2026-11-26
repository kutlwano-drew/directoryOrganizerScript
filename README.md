<div align="center">

# HYBRID FILE ORGANISER

### A smarter, safer way to bring order to your files — right from the terminal.

**Version 2.0 · Python · CLI-first · Local filesystem utility**

<!-- Replace this block with a logo/banner image if you make one. -->

[Features](#what-hybrid-can-do) · [Preview](#in-action) · [Install](#installation) · [Usage](#getting-started) · [Changelog](CHANGELOG.md)

</div>

---

## Contents

Click any section to jump straight there. Each section also has navigation links at its end so this README can be explored like a small app.


- [01 · About](#about-hybrid)
- [02 · What's new in 2.0](#whats-new-in-20)
- [03 · Features](#what-hybrid-can-do)
- [04 · In action](#in-action)
- [05 · Installation](#installation)
- [06 · Getting started](#getting-started)
- [07 · Safety & control](#safety--control)
- [08 · Configuration](#configuration)
- [09 · Requirements](#requirements)
- [10 · Project structure](#project-structure)
- [11 · Changelog](#changelog)
- [12 · Feedback & contributions](#feedback--contributions)

---


## About HYBRID

HYBRID FILE ORGANISER started as a straightforward Python script: move files into folders based on their extensions. Version 2.0 is a major overhaul of that original idea, evolving it into a more capable, interactive file-management utility while keeping the terminal at the centre of the experience.


HYBRID helps you inspect directories, plan organisation, find duplicates, rename files in batches, and review past operations — without needing a graphical interface or cloud service.

**The philosophy:** keep file management practical, local, understandable, and under your control.

[↑ Back to top](#hybrid-file-organiser) · [Next: What's new →](#whats-new-in-20)

---

## What's new in 2.0

Version 2.0 replaces the original single-script workflow with a modular application and a richer CLI experience.

| Original script | HYBRID 2.0 overhaul |
|---|---|
| Basic extension-based sorting | Expanded organisation workflow and preview |
| Simple text prompts | Rich terminal presentation |
| Session-only category settings | Persistent configuration |
| No operation history | SQLite-backed operation history |
| No undo | Undo for supported operations |
| No duplicate analysis | SHA-256 duplicate detection |
| No batch rename | Batch renaming tools |
| Minimal directory insight | Scanning and directory analysis |
| Single script | Modular codebase |

See the full [changelog](CHANGELOG.md) for the version-by-version record.

[← Previous: About](#about-hybrid) · [↑ Back to top](#hybrid-file-organiser) · [Next: Features →](#what-hybrid-can-do)

---

## What HYBRID can do

HYBRID combines file organisation with tools that help you inspect, manage, and understand the contents of your directories.

### Organise files
Group files into categories using configurable file-type rules. Preview planned changes before committing to an organisation operation.

### Preview before committing
Review the proposed organisation plan and inspect category contents before moving files. Keep control over what the operation will do.

### Find duplicates
Identify duplicate content using SHA-256 hashing rather than relying on filenames alone. Review duplicate groups and understand potential space savings.

### Batch rename
Apply renaming operations to groups of files rather than changing each filename one at a time.

### Scan and inspect
Scan directories, review file information, and use available analysis tools to get a better picture of what is inside.

### Operation history & undo
Review recorded operations and undo supported actions where available. Persistent records help make previous activity easier to understand.

### Persistent settings
Retain supported settings between launches, including organisation preferences and configuration.

### CLI experience
A terminal-first interface with Rich formatting for clearer menus, tables, summaries, and status feedback. No GUI, browser, or cloud account is required.

[← Previous: What's new](#whats-new-in-20) · [↑ Back to top](#hybrid-file-organiser) · [Next: In action →](#in-action)

---
## In action

The demonstrations below are hosted on GitHub and embedded using remote image URLs. Replace `USERNAME` and `REPOSITORY` with your GitHub account and repository name when uploading the GIFs.

<details>
<summary><strong>Organisation preview</strong> — scan, category breakdown, and preview before applying</summary>

![HYBRID organisation preview](https://raw.githubusercontent.com/USERNAME/REPOSITORY/main/assets/gifs/organise-preview.gif)

</details>

<details>
<summary><strong>Duplicate finder</strong> — duplicate groups and hash-based matching</summary>

![HYBRID duplicate finder](https://raw.githubusercontent.com/USERNAME/REPOSITORY/main/assets/gifs/duplicate-finder.gif)

</details>

<details>
<summary><strong>Batch rename</strong> — rename planning and resulting filenames</summary>

![HYBRID batch rename](https://raw.githubusercontent.com/USERNAME/REPOSITORY/main/assets/gifs/batch-rename.gif)

</details>

<details>
<summary><strong>History and undo</strong> — recorded operations and undo workflow</summary>

![HYBRID history and undo](https://raw.githubusercontent.com/USERNAME/REPOSITORY/main/assets/gifs/history-undo.gif)

</details>

Record short demonstrations using a test directory. Keep the terminal text readable and avoid exposing private filenames or paths.


[← Previous: Features](#what-hybrid-can-do) · [↑ Back to top](#hybrid-file-organiser) · [Next: Installation →](#installation)

---
## Installation

### 1. Get the project
Download or clone the repository, then open a terminal in the project directory.

### 2. Create a virtual environment

**Windows (PowerShell):**
```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**Linux / macOS:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies
```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Launch HYBRID
```bash
python run_hybrid_file_organiser.py
```

[← Previous: In action](#in-action) · [↑ Back to top](#hybrid-file-organiser) · [Next: Getting started →](#getting-started)

---
## Getting started

1. Launch HYBRID from your terminal.
2. Choose the tool or workflow from the interactive menu.
3. Select or enter the directory you want to work with.
4. Review the scan, analysis, or proposed operation where a preview is available.
5. Confirm when you're satisfied, then review the result summary.

The exact menu labels and available actions are shown in the app itself. For file-moving operations, review the preview carefully before confirming.

[← Previous: Installation](#installation) · [↑ Back to top](#hybrid-file-organiser) · [Next: Safety & control →](#safety--control)

---
## Safety & control

HYBRID is intended to keep the user in control of file operations.

- Review organisation previews before applying moves.
- Duplicate identification is for review; don't delete files solely because a tool marks them as duplicates.
- Undo is available for supported recorded operations. Not every filesystem action is necessarily reversible.
- Keep backups of important files before large organisation or rename operations.
- Try new rules and workflows on a disposable test directory first.
- Be mindful of permissions, symbolic links, locked files, and destination-name conflicts.

[← Previous: Getting started](#getting-started) · [↑ Back to top](#hybrid-file-organiser) · [Next: Configuration →](#configuration)

---
## Configuration

HYBRID stores supported settings persistently so that configuration can carry across launches. Category and organisation behaviour can be adjusted using the settings and configuration features exposed in the CLI.

Configuration details and defaults may vary by build; use the in-app settings and the project configuration module as the authoritative reference for your local version.

[← Previous: Safety & control](#safety--control) · [↑ Back to top](#hybrid-file-organiser) · [Next: Requirements →](#requirements)

---
## Requirements

- **Python 3.10 or newer**
- **Rich** — terminal formatting and presentation
- **SQLite** — included with Python; used for persistent records

Install Python packages using:
```bash
pip install -r requirements.txt
```

[← Previous: Configuration](#configuration) · [↑ Back to top](#hybrid-file-organiser) · [Next: Project structure →](#project-structure)

---
## Project structure

```text
HYBRID FILE ORGANISER/
├── run_hybrid_file_organiser.py    # Application entry point
├── hybrid_file_organiser/
│   ├── app.py                      # Application orchestration
│   ├── ui.py                       # CLI presentation and interaction
│   ├── scanner.py                   # Directory scanning
│   ├── engine.py                    # File operation engine
│   ├── intelligence.py               # Directory analysis tools
│   ├── config.py                    # Persistent configuration
│   └── database.py                   # SQLite persistence
├── tests/                             # Automated tests
├── requirements.txt
├── pyproject.toml
├── CHANGELOG.md
└── README.md
```

[← Previous: Requirements](#requirements) · [↑ Back to top](#hybrid-file-organiser) · [Next: Changelog →](#changelog)

---
## Changelog

HYBRID 2.0 is a major overhaul of the original single-script file sorter. Read the full [CHANGELOG](CHANGELOG.md) for detailed additions and changes.

[← Previous: Project structure](#project-structure) · [↑ Back to top](#hybrid-file-organiser) · [Next: Feedback →](#feedback--contributions)

---
## Feedback & contributions

Found a bug, have an idea, or want to improve HYBRID? Issues, feature suggestions, and contributions are welcome. When reporting a problem, include your operating system, Python version, steps to reproduce, and any relevant error output — remove personal paths or sensitive details first.


Thanks for checking out **HYBRID FILE ORGANISER**. Keep it local. Keep it clear. Stay in control.


[← Previous: Changelog](#changelog) · [↑ Back to top](#hybrid-file-organiser)


<div align="center">

**HYBRID FILE ORGANISER · Version 2.0**

*Organise with clarity. Operate with confidence.*

</div>
