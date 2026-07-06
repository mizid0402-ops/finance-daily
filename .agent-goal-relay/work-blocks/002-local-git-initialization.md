# Work Block 002: Local Git Initialization

## Objective

Initialize local Git version control for the finance daily MVP and prepare the project for a future GitHub Actions remote workflow.

## Scope

- `.gitignore`
- `.agent-goal-relay/`
- local Git metadata
- current project files and generated outputs

## Expected Output

- A local Git repository exists.
- The first commit captures source, tests, docs, relay state, workflow, and current generated outputs.
- Local-only files such as `.venv/`, `.env`, caches, and temporary files are ignored.

## Constraints

- Do not create a remote repository.
- Do not push.
- Do not configure secrets or deployment.
- Keep generated diary outputs tracked: `backup/*.md`, `rss.xml`, and `data/finance_daily.sqlite`.

## Acceptance Criteria

- `py -m pytest -q` passes before and after Git initialization.
- `py src/main.py` succeeds before and after Git initialization.
- `git log --oneline -1` shows the initial local commit.
- `.venv/`, `.pytest_cache/`, `__pycache__/`, and `.env` are not tracked.
- `backup/2026-07-06.md`, `rss.xml`, and `data/finance_daily.sqlite` are tracked.

## Risk Level

Low. This work only adds local version control and ignore rules.

## Validation Method

- `py -m pytest -q`
- `py src/main.py`
- `git status --short --branch`
- `git log --oneline -1`
- `git ls-files`

## Exact Next Step After Completion

Wait for the user to choose the next objective: GitHub remote setup, Actions hardening, RSS publishing URL, or report-analysis improvements.
