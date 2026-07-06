# Worker Result: 008 API Key Fallback Review

- Completed: 2026-07-06T16:05:00+08:00
- Review owner: Codex
- Mode: review-only relay follow-up

## Objective

Review why the GitHub/production generation still falls back to the rule-based report and archive the result in relay.

## Findings

- The application code already supports `OPENAI_API_KEY`, `OPENAI_BASE_URL`, and `OPENAI_MODEL`.
- The GitHub Actions workflow already passes `OPENAI_API_KEY`, `OPENAI_BASE_URL`, and `OPENAI_MODEL` from repository secrets into `python src/main.py`.
- Local `.env` is missing, so local generation falls back with `OPENAI_API_KEY is not set`.
- Current generated `backup/2026-07-06.md` and `rss.xml` still contain the fallback notice `OPENAI_API_KEY is not set`.
- GitHub repository `mizid0402-ops/finance-daily` exists, is public, and uses default branch `main`.

## Checks Run

- `git status --short --branch`
- `git remote -v`
- `Get-RelaySnapshot.ps1`
- `py -m pytest -q`: passed, 14 tests.
- GitHub repository metadata lookup for `mizid0402-ops/finance-daily`.
- Sensitive file checks for `.env`, `.venv`, SQLite, caches, and committed key-like strings.

## Safety Review

- `.env` is not present locally.
- `.venv/` and `data/finance_daily.sqlite` are ignored.
- No `.env`, `.venv/`, SQLite database, pycache, or pytest cache is present in `HEAD`.
- `config/sources.yml` contains public RSS URLs only.
- Secret-pattern scan only found placeholder/example references, not a real API key.

## Resolution Status

Blocked on secret configuration. The fallback is expected until a real `OPENAI_API_KEY` is configured in GitHub Secrets or a local `.env`.

## Next Required Human Action

Configure at least:

- GitHub Secret `OPENAI_API_KEY`

Optional but recommended:

- GitHub Secret `OPENAI_BASE_URL`
- GitHub Secret `OPENAI_MODEL`

Then trigger the `Finance Daily` workflow manually or rerun locally with `.env`.
