# Video Downloader - Development Guide

## Project Overview

影片批量下載工具 - 支援 YouTube 與 Bilibili 平台的 PySide6 桌面應用程式。

## Quick Start

```bash
# Install dependencies
uv sync

# Run the application
uv run python video_downloader.py

# Run linting
uv run ruff check . --fix
uv run ruff format .

# Run tests
uv run pytest -v
```

## Project Structure

```
├── video_downloader.py  # Main application (PySide6 GUI)
├── pyproject.toml       # Project configuration
├── README.md            # User documentation
├── docs/                # User guides
│   ├── quick_start.md
│   ├── user_guide.md
│   ├── faq.md
│   └── troubleshooting.md
└── .agent/workflows/    # Automation workflows
    └── release.md
```

## Code Style

- Use `ruff` for linting and formatting
- Target Python 3.10+
- Line length: 120 characters
- Run before committing: `uv run ruff check . --fix && uv run ruff format .`

## Common Lint Issues

| Issue | Fix |
|-------|-----|
| W293: whitespace on blank line | `ruff format` auto-fixes |
| E722: bare `except:` | Change to `except Exception:` |
| I001: unsorted imports | `ruff check --fix` auto-fixes |
| F401: unused import | Remove or add `# noqa: F401` |
| NameError: forward reference | Add `from __future__ import annotations` |

## Release Workflow

Use the `/release` workflow for automated releases:

```bash
# The workflow will:
# 1. Run lint check and auto-fix
# 2. Run tests
# 3. Commit changes
# 4. Create git tag
# 5. Push to GitHub
```

See `.agent/workflows/release.md` for detailed steps.

### Version Update Locations

When releasing a new version, update:
1. `pyproject.toml` - `version = "X.Y.Z"`
2. `video_downloader.py` - `APP_VERSION = "vX.Y.Z"`
3. `README.md` - Add changelog entry

## Key Features

- **Keyboard Shortcuts**: Ctrl+Enter (download), Ctrl+Shift+V (paste), F1 (help), Ctrl+O (path), Ctrl+Q (quit)
- **Drag & Drop**: URLs and .txt files
- **Cookie Status**: 🟢 valid, 🟡 unverified, 🔴 invalid
- **Export**: CSV/HTML download reports

## Testing Tips

- Use `send_command_input` for interactive terminal testing
- Syntax check: `python -m py_compile video_downloader.py`
- Full lint: `uv run ruff check .`

## Dependencies

- PySide6 - Qt GUI framework
- yt-dlp - Video downloading engine
- ruff - Linting and formatting
