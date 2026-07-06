# Work Block 001: MVP Python Pipeline

## Objective

Create the first runnable Python MVP for the finance daily system.

## Scope

- `collector/`
- `analyzer/`
- `storage/`
- `rss/`
- `src/main.py`
- project docs and workflow files

## Acceptance Criteria

- Tests pass with `py -m pytest -q`.
- Local command `py src/main.py` generates Markdown, RSS, and SQLite outputs.
- LLM failures produce a fallback Markdown draft.

## Risks

- Some RSS feeds may reject requests or have stale data.
- Local `python` command may point to Windows Store shim; use `py` on this machine.
