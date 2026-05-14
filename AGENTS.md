# Video Downloader - Development Guide

## Repository Identity

- GitHub repository: `https://github.com/LostSunset/video_lists_downloader.git`
- Owner/admin username: `LostSunset`
- Owner/admin email: `lollipopg4ao3@gmail.com`
- Default branch: `main`

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

```text
├── video_downloader.py  # Main application (PySide6 GUI)
├── bin_manager.py       # yt-dlp/ffmpeg binary manager
├── pyproject.toml       # Project configuration
├── README.md            # User documentation
├── CHANGELOG.md         # Release changelog
├── AGENTS.md            # Codex development rules
├── CLAUDE.md            # Claude Code development rules
├── docs/                # User and maintenance guides
│   ├── quick_start.md
│   ├── user_guide.md
│   ├── faq.md
│   ├── troubleshooting.md
│   ├── developer_log.md
│   ├── research_log.md
│   └── sessions/
└── .agent/workflows/    # Automation workflows
    └── release.md
```

## Code Style

- Use `ruff` for linting and formatting.
- Target Python 3.10+.
- Line length: 120 characters.
- Run before committing: `uv run ruff check . --fix && uv run ruff format .`.

## Common Lint Issues

| Issue | Fix |
|-------|-----|
| W293: whitespace on blank line | `ruff format` auto-fixes |
| E722: bare `except:` | Change to `except Exception:` |
| I001: unsorted imports | `ruff check --fix` auto-fixes |
| F401: unused import | Remove or add `# noqa: F401` |
| NameError: forward reference | Add `from __future__ import annotations` |

## Branch Protection Policy

- `main` is protected through GitHub branch protection.
- Non-admin developers must open a pull request before merging into `main`.
- `LostSunset` as owner/admin may directly push to `main` when intentionally performing maintenance or release work.
- Do not bypass the PR flow for other developers.
- Before changing branch protection, inspect current settings with:

```bash
gh api repos/LostSunset/video_lists_downloader/branches/main/protection
```

## Automatic Push Rules

When asked to auto-push or release, follow this sequence:

1. Inspect current git state and remote state.
2. Commit and push only the intended scope.
3. Decide whether the version must change according to Semantic Versioning.
4. If the version changes, decide whether a new GitHub Release/tag is required.
5. Decide whether docs in `docs/*.md` or `docs/sessions/*.md` need updates.
6. Decide whether `README.md` needs a changelog or usage update.
7. Decide whether `AGENTS.md` and `CLAUDE.md` need synchronized updates.
8. Update `docs/developer_log.md` and add a SESSION file when the work has meaningful context.
9. Update `docs/research_log.md` when goals, research, architecture, platform behavior, or release policy changes.
10. Run lint/tests or document why a check could not be run.
11. Commit, tag when appropriate, and push.

## Release Workflow

Use the `/release` workflow for automated releases:

```bash
# The workflow will:
# 1. Run lint check and auto-fix
# 2. Run tests
# 3. Update version files and changelogs
# 4. Commit changes
# 5. Create git tag
# 6. Push to GitHub
```

See `.agent/workflows/release.md` for detailed steps.

### Versioning Rules (Semantic Versioning)

Every push MUST evaluate whether the version should change. For direct pushes to `main`, bump the version unless the push is clearly metadata-only and does not affect users, maintainers, release process, docs, or automation.

| Change Type | Version Bump | Example |
|-------------|--------------|---------|
| `fix:` Bug 修復 / 效能提升 | PATCH | v0.3.0 -> v0.3.1 |
| `docs:` User-facing docs or maintenance docs | PATCH | v0.3.0 -> v0.3.1 |
| `chore:` Release/process/dependency metadata | PATCH | v0.3.0 -> v0.3.1 |
| `feat:` 新功能 | MINOR | v0.3.0 -> v0.4.0 |
| `breaking:` 重大變更 | MAJOR | v0.3.0 -> v1.0.0 |

### Version Update Locations

When releasing a new version, update:

1. `pyproject.toml` - `version = "X.Y.Z"`
2. `video_downloader.py` - `APP_VERSION = "vX.Y.Z"`
3. `uv.lock` - sync package metadata with `uv sync`
4. `README.md` - add changelog entry
5. `CHANGELOG.md` - add changelog entry
6. `docs/developer_log.md` - add development log entry
7. `docs/sessions/` - add SESSION file when the work has meaningful context

## Developer Log and SESSION Rules

- `docs/developer_log.md` records project-level decisions, releases, branch protection changes, workflow changes, and important maintenance actions.
- `docs/sessions/SESSION_TEMPLATE.md` is the template for session records.
- Add a dated file under `docs/sessions/` for work that spans multiple steps, changes release policy, changes automation, or affects future agents.
- `docs/research_log.md` records research goals, current conclusions, verification approach, and status.
- Never write secrets, cookies, tokens, private credentials, or personal access tokens into logs.

## Key Features

- Keyboard Shortcuts: Ctrl+Enter (download), Ctrl+Shift+V (paste), F1 (help), Ctrl+O (path), Ctrl+Q (quit)
- Drag & Drop: URLs and .txt files
- Cookie Status: valid, unverified, invalid with auto-fallback to no-cookie when browser cookies unavailable
- Playlist Path Change Detection: prompts user when playlist download path differs from previous location
- Export: CSV/HTML download reports

## Testing Tips

- Use `send_command_input` for interactive terminal testing when available.
- Syntax check: `uv run python -m py_compile video_downloader.py`.
- Full lint: `uv run ruff check .`.
- Full test: `uv run pytest -v`.

## Dependencies

- PySide6 - Qt GUI framework
- yt-dlp - Video downloading engine
- yt-dlp-ejs - YouTube challenge helper
- ruff - Linting and formatting
