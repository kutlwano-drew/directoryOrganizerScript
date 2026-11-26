# HYBRID FILE ORGANISER
## Changelog — Version 1.0 → Version 2.0

### Version 1.0 — Original File Organizer
The initial version was a basic Python file-organizing script designed to automatically sort files into folders based on their extensions.

**Original capabilities**
- Automatic file organization based on predefined file extensions.
- Eight default categories: Documents, Videos, Audio, Images, Archives, Scripts, Spreadsheets and Presentations.
- Automatic creation of destination folders.
- Uncategorized files placed into an `Others` folder.
- File-format exclusion support.
- Creation of custom categories.
- Editing existing category configurations.
- Adding, replacing and removing supported file extensions.
- Renaming category folders.
- Restoring default category configurations.
- Basic interactive menu-driven interface.

**Limitations**
- No persistent configuration storage.
- No organization preview before files were moved.
- No duplicate detection.
- No operation history.
- No undo functionality.
- No file search or filtering.
- No detailed directory analysis.
- No batch renaming.
- No advanced file management capabilities.
- Limited error handling and operation visibility.
- Configuration changes existed only for the current runtime session.

---

### Version 2.0 — HYBRID FILE ORGANISER

A comprehensive overhaul of the original script, transforming it from a basic extension-based sorter into a modular, interactive and more safety-conscious command-line file management utility.

#### Added Features

**1. Modular Architecture**
- Reorganized the application into dedicated modules.
- Separated scanning, file operations, configuration, database management and user interface logic.
- Improved maintainability and extensibility.

**2. Interactive CLI Dashboard**
- Replaced the original basic numbered menu with a richer terminal interface.
- Added improved navigation, structured information presentation and more detailed operation feedback.
- Introduced a more cohesive application identity under HYBRID FILE ORGANISER.

**3. Directory Scanning & Analysis**
- Added directory scanning and file inventory capabilities.
- Improved visibility into directory contents, file counts and storage information.
- Added analytical capabilities beyond simple extension-based sorting.

**4. Organisation Preview**
- Added the ability to review proposed file movements before executing them.
- Improved control over organisation operations.
- Reduced the risk of unintended file movements.

**5. Duplicate Detection**
- Introduced duplicate file identification.
- Implemented SHA-256 hashing for content-based duplicate verification.
- Added duplicate analysis to help identify redundant files.

**6. Batch Renaming**
- Added batch file-renaming capabilities.
- Expanded file management beyond directory organisation.

**7. Operation History**
- Introduced persistent tracking of file operations.
- Added operation records for reviewing previous activities.

**8. Undo Functionality**
- Added the ability to reverse supported file operations.
- Improved operational safety and recoverability.

**9. Persistent Configuration**
- Added configuration persistence.
- Settings and category configurations can be retained between application sessions rather than being reset whenever the script closes.

**10. Exclusion Management**
- Expanded file exclusion functionality.
- Improved control over which files are included in organisation operations.

**11. Improved Error Handling**
- Enhanced error reporting and operation feedback.
- Improved handling of invalid directories, failed operations and filesystem exceptions.

**12. Improved File Organisation**
- Expanded the original categorisation and organisation workflow.
- Improved handling of file movements and destination directories.
- Built on the original extension-mapping system while introducing more flexible organisation functionality.

**13. Database Integration**
- Added SQLite-backed storage for persistent application data.
- Enabled operation tracking and supporting data persistence without requiring an external database server.

**14. Improved Terminal Presentation**
- Added Rich-powered terminal output.
- Introduced formatted tables, panels, status indicators and improved readability.

**15. Application Branding**
- Introduced the HYBRID FILE ORGANISER application identity.
- Replaced the original generic File Organizer Script presentation with a more structured application experience.

---

### Summary of Evolution

| Area | Version 1.0 | Version 2.0 |
|---|---|---|
| File organisation | Basic extension sorting | Expanded organisation workflow |
| Categories | 8 predefined categories | More flexible category configuration |
| Interface | Basic text menus | Rich interactive CLI |
| Configuration | Runtime only | Persistent settings |
| Preview | None | Organisation preview |
| Duplicate detection | None | SHA-256 based |
| File renaming | None | Batch renaming |
| File scanning | Basic directory iteration | Dedicated scanning capabilities |
| History | None | Persistent operation history |
| Undo | None | Reversal of supported operations |
| Database | None | SQLite |
| Exclusions | Basic extension exclusions | Expanded exclusion management |
| Analytics | None | Directory analysis |
| Error handling | Basic exception handling | Improved reporting and operation handling |
| Architecture | Single script | Modular application architecture |

### Version 2.0 Objective

HYBRID FILE ORGANISER 2.0 was developed to evolve the original script into a more complete file-management utility while retaining its core philosophy: local filesystem management, user-controlled operations, straightforward usability and a command-line-first experience.

The overhaul prioritizes functionality, modularity, persistence, visibility and safer file operations without requiring a graphical interface.
