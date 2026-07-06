# Finance Daily Next Blocks Design

## Goal

Advance the finance daily MVP through four ordered improvements: report analysis quality, configurable RSS publishing URL, GitHub Actions hardening, and GitHub remote setup preparation.

## Work Order

1. Improve report analysis while preserving the current Markdown, RSS, and SQLite outputs.
2. Make the RSS publishing base URL configurable without requiring a remote site yet.
3. Harden GitHub Actions so scheduled generation is easier to validate and less noisy.
4. Prepare GitHub remote setup material, then pause before any external repository, push, or secret change.

## Architecture

The existing pipeline remains intact: `src/main.py` collects articles, deduplicates them, clusters events, generates a Markdown report, stores data, and writes `rss.xml`. Report analysis changes stay inside `analyzer/` and tests. Publishing URL behavior is added as a small configuration boundary near the RSS write step. Actions hardening is limited to `.github/workflows/daily.yml` and documentation. Remote setup is documentation and relay state only unless the user explicitly approves external actions later.

## Error Handling

The system must continue to generate a fallback report without `OPENAI_API_KEY`. Missing `SITE_URL` must not break local generation. GitHub Actions must fail on test or generation errors, but skip commits when outputs do not change.

## Testing

Use TDD for behavior changes. Run focused pytest targets for each changed area, then run the full test suite. Validate XML parsing for RSS. For workflow YAML, inspect the file and keep commands shell-safe.

## Human Checkpoints

Stop before creating a GitHub remote, pushing a branch, configuring secrets, or choosing a real public publishing URL if it is not already supplied.
