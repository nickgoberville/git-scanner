# Usage Guide

## Basic Usage

Run the scanner by pointing it to a directory. If no directory is provided, it scans the current working directory.

```bash
python3 scanner.py [directory_path]
```

**Example:**

```bash
python3 scanner.py ~/projects
```

## CLI Arguments

| Argument       | Description                                                      |
| :------------- | :--------------------------------------------------------------- |
| `path`         | The root directory to scan. Defaults to `.` (Current Directory). |
| `--verbose`    | Print more details during the scan.                              |
| `-h`, `--help` | Show the help message and exit.                                  |

## Understanding the Output

The tool provides a clean summary of your repositories.

### Git Repositories

It lists found repositories with status icons:

- `[OK]` **CLEAN**: No changes, everything up to date.
- `[*] ` **DIRTY**: You have uncommitted changes.
- `[*] ` **UNPUSHED COMMITS**: You have committed changes that haven't been pushed to the upstream branch.
- `[!]` **ERROR**: Something went wrong checking status.

### Uninitialized Directories

Shows folders that contain source code (e.g., `.py`, `.js`, `.c`) but are **not** inside a git repository. This is useful for finding forgotten projects.

```text
[?] code_no_git
```
