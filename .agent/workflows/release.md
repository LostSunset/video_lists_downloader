---
description: Automated release workflow - lint, test, update README, commit, tag, and push to GitHub
---

# Release Workflow

This workflow automates the release process for the Video Downloader project.

## Prerequisites

- Git configured with push access to the repository
- `uv` installed for Python dependency management
- All changes committed before running

## Steps

### 1. Run Lint Check and Auto-Fix
// turbo
```bash
uv run ruff check . --fix
uv run ruff format .
```

### 2. Verify No Remaining Lint Errors
// turbo
```bash
uv run ruff check .
```
If errors remain, fix them manually before proceeding.

### 3. Run Tests (if available)
// turbo
```bash
uv run pytest -v || echo "No tests configured"
```

### 4. Update Version Number
Update the version in these files:
- `pyproject.toml` - `version = "X.Y.Z"`
- `video_downloader.py` - `APP_VERSION = "vX.Y.Z"`

### 5. Update README.md Changelog
Add the new version entry under `## 版本歷史 | Changelog`:
```markdown
### vX.Y.Z (YYYY-MM-DD)
- New feature 1
- New feature 2
- Bug fix 1
```

### 6. Commit Changes
// turbo
```bash
git add -A
git commit -m "chore: release vX.Y.Z"
```

### 7. Create Git Tag
// turbo
```bash
git tag -a vX.Y.Z -m "Release vX.Y.Z"
```

### 8. Push to GitHub
```bash
git push origin main
git push origin vX.Y.Z
```

## Quick Release Command

For a quick release after all changes are ready:

```bash
# Replace X.Y.Z with actual version
uv run ruff check . --fix && uv run ruff format . && git add -A && git commit -m "chore: release vX.Y.Z" && git tag -a vX.Y.Z -m "Release vX.Y.Z" && git push origin main && git push origin vX.Y.Z
```

## Verification Checklist

- [ ] All lint errors fixed
- [ ] Version updated in pyproject.toml
- [ ] Version updated in video_downloader.py (APP_VERSION)
- [ ] README changelog updated
- [ ] Git tag created
- [ ] Pushed to GitHub
