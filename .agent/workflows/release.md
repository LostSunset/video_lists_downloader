---
description: Automated release workflow - inspect scope, update version/docs/logs, test, commit, tag, and push to GitHub
---

# Release Workflow

This workflow automates the release process for the Video Downloader project.

## Prerequisites

- Git configured with push access to the repository
- `uv` installed for Python dependency management
- `gh` authenticated as `LostSunset` for repository and branch protection operations
- A clean understanding of which files belong to the release

## Steps

### 0. Inspect Scope and Remote State

// turbo
```bash
git status --short --branch
git remote -v
gh repo view LostSunset/video_lists_downloader --json nameWithOwner,defaultBranchRef,isPrivate,viewerPermission
```

Confirm the intended files before staging. Do not upload ignored local runtime files such as `bin/`, `.venv/`, `old_version/`, `download_history.json`, `playlist_state.json`, or `playlist_updates_log.json`.

### 1. Decide Version Bump

Use Semantic Versioning:

| Change Type | Version Bump |
|-------------|--------------|
| Bug fix / performance improvement | PATCH |
| User-facing docs or maintenance workflow docs | PATCH |
| Release/process/dependency metadata | PATCH |
| Feature | MINOR |
| Breaking change | MAJOR |

For direct pushes to `main`, bump the version unless the push is clearly metadata-only and does not affect users, maintainers, release process, docs, or automation.

### 2. Update Version Number

Update the version in these files:

- `pyproject.toml` - `version = "X.Y.Z"`
- `video_downloader.py` - `APP_VERSION = "vX.Y.Z"`
- `uv.lock` - run `uv sync`

### 3. Decide Documentation Updates

Check whether the version requires updates to:

- `README.md`
- `CHANGELOG.md`
- `docs/*.md`
- `docs/sessions/*.md`
- `AGENTS.md`
- `CLAUDE.md`
- `docs/developer_log.md`
- `docs/research_log.md`

### 4. Update README.md Changelog

Add the new version entry under `## 版本歷史 | Changelog`:

```markdown
### vX.Y.Z (YYYY-MM-DD)
- New feature 1
- New feature 2
- Bug fix 1
```

### 5. Update Developer Logs and SESSION

- Add a version entry to `docs/developer_log.md`.
- Add a dated SESSION file under `docs/sessions/` when the work has meaningful context.
- Update `docs/research_log.md` when goals, architecture, platform behavior, or release policy changes.

### 6. Run Lint Check and Auto-Fix

// turbo
```bash
uv run ruff check . --fix
uv run ruff format .
```

### 7. Verify No Remaining Lint Errors

// turbo
```bash
uv run ruff check .
```
If errors remain, fix them manually before proceeding.

### 8. Run Tests

// turbo
```bash
uv run pytest -v
```

If tests cannot run because dependencies are missing, run `uv sync --extra dev` and retry once.

### 9. Commit Changes

// turbo
```bash
git add pyproject.toml video_downloader.py uv.lock README.md CHANGELOG.md AGENTS.md CLAUDE.md .agent docs
git commit -m "chore: release vX.Y.Z"
```

### 10. Create Git Tag

// turbo
```bash
git tag -a vX.Y.Z -m "Release vX.Y.Z"
```

### 11. Push to GitHub

```bash
git push origin main
git push origin vX.Y.Z
```

### 12. Verify or Apply Branch Protection

Non-admin developers must use pull requests. `LostSunset` as owner/admin may directly push for intentional maintenance/release work.

```bash
cat <<'JSON' | gh api --method PUT repos/LostSunset/video_lists_downloader/branches/main/protection \
  -H "Accept: application/vnd.github+json" \
  --input -
{
  "required_status_checks": null,
  "enforce_admins": false,
  "required_pull_request_reviews": {
    "required_approving_review_count": 1,
    "dismiss_stale_reviews": true,
    "require_code_owner_reviews": false
  },
  "restrictions": null,
  "required_linear_history": false,
  "allow_force_pushes": false,
  "allow_deletions": false,
  "block_creations": false,
  "required_conversation_resolution": false,
  "lock_branch": false,
  "allow_fork_syncing": false
}
JSON
```

Verify:

```bash
gh api repos/LostSunset/video_lists_downloader/branches/main/protection
```

## Quick Release Command

For a quick release after all changes are ready:

```bash
# Replace X.Y.Z with actual version
uv sync && uv run ruff check . --fix && uv run ruff format . && uv run pytest -v && git add pyproject.toml video_downloader.py uv.lock README.md CHANGELOG.md AGENTS.md CLAUDE.md .agent docs && git commit -m "chore: release vX.Y.Z" && git tag -a vX.Y.Z -m "Release vX.Y.Z" && git push origin main && git push origin vX.Y.Z
```

## Verification Checklist

- [ ] All lint errors fixed
- [ ] Version updated in pyproject.toml
- [ ] Version updated in video_downloader.py (APP_VERSION)
- [ ] uv.lock synced
- [ ] README changelog updated
- [ ] CHANGELOG updated
- [ ] AGENTS.md and CLAUDE.md synchronized
- [ ] Developer log updated
- [ ] SESSION added when needed
- [ ] Research log updated when needed
- [ ] Git tag created
- [ ] Pushed to GitHub
- [ ] Branch protection verified
