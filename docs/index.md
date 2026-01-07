# Git Scanner

Welcome to the **Git Scanner** documentation. This tool is designed to be a lightweight, dependency-free scanner for managing your git repositories.

<img src="assets/logo_v2.png" width="150" align="right" alt="Git Scanner Logo" />

## Features

- **Recursively Scan**: Finds all git repositories in a directory tree.
- **Status Check**: Instantly see which repos are `DIRTY` (uncommitted changes) or have `UNPUSHED` commits.
- **Find Uninitialized Code**: Identifies folders that contain code but have not been initialized as git repositories.
- **Zero Dependencies**: The core tool is a single Python script using only the standard library.

## Installation

### Prerequisites

- **Python 3.6+**: Pre-installed on most Linux/Mac systems and easily available on Windows.

### Download

Since this is a single-script tool, you can simply clone the repository or download `scanner.py`.

```bash
git clone https://github.com/your-username/git-scanner.git
cd git-scanner
```

### Optional: Alias

For easier access, you can add an alias to your shell profile (`.bashrc` or `.zshrc`):

```bash
alias gitscan="python3 /path/to/git-scanner/scanner.py"
```
