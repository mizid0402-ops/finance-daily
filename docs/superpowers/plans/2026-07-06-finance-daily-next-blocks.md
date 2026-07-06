# Finance Daily Next Blocks Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Improve the finance daily MVP in four ordered low-risk blocks, stopping before external GitHub or publishing decisions.

**Architecture:** Keep the current Python pipeline shape. Add analysis quality helpers under `analyzer/`, configuration at `src/main.py`/RSS boundary, workflow hardening in `.github/workflows/daily.yml`, and remote setup docs without performing external writes.

**Tech Stack:** Python 3.12, pytest, feedparser, requests, OpenAI-compatible SDK, GitHub Actions.

---

### Task 1: Report Analysis

**Files:**
- Modify: `analyzer/report.py`
- Modify: `analyzer/llm.py`
- Test: `tests/test_report_and_rss.py`

- [ ] **Step 1: Write failing tests**

Add tests showing that fallback reports include a structured market breadth summary, event confidence based on source count, and company-mapping guidance without buy/sell/target-price language.

- [ ] **Step 2: Run focused tests**

Run: `py -m pytest tests/test_report_and_rss.py -q`

Expected: fail because the new structured analysis fields do not exist yet.

- [ ] **Step 3: Implement minimal report analysis helpers**

Add small helpers in `analyzer/report.py` for market breadth, confidence labels, and company-mapping guidance. Keep the public `build_fallback_report()` signature unchanged.

- [ ] **Step 4: Run focused tests and full tests**

Run: `py -m pytest tests/test_report_and_rss.py -q`

Run: `py -m pytest -q`

Expected: all tests pass.

### Task 2: RSS Publishing URL

**Files:**
- Modify: `src/main.py`
- Modify: `rss/generator.py` if needed
- Modify: `README.md`
- Test: `tests/test_report_and_rss.py`

- [ ] **Step 1: Write failing tests**

Add a test proving that RSS item links use a supplied `SITE_URL`-style base URL and that trailing slashes are normalized.

- [ ] **Step 2: Run focused tests**

Run: `py -m pytest tests/test_report_and_rss.py -q`

Expected: fail until configuration is wired through.

- [ ] **Step 3: Implement configuration**

Read `SITE_URL` from the environment in `src/main.py`, default to `https://example.com/finance-daily`, and pass it to `write_rss()`.

- [ ] **Step 4: Run validation**

Run: `py -m pytest -q`

Run: `py src/main.py`

Expected: tests pass and local generation succeeds.

### Task 3: Actions Hardening

**Files:**
- Modify: `.github/workflows/daily.yml`
- Modify: `README.md`

- [ ] **Step 1: Harden workflow**

Add dependency caching, run tests before generation, pass `SITE_URL` from variables or secrets, use concurrency, and keep commit behavior idempotent.

- [ ] **Step 2: Validate locally**

Run: `py -m pytest -q`

Inspect `.github/workflows/daily.yml` for syntax and shell command consistency.

### Task 4: GitHub Remote Setup Preparation

**Files:**
- Modify: `README.md`
- Add: `docs/github-remote-setup.md`

- [ ] **Step 1: Add setup guide**

Document decisions needed for repository visibility, remote URL, branch push, Pages or raw RSS publishing, and GitHub secrets/variables.

- [ ] **Step 2: Stop for human decision**

Do not create a remote, push, or configure secrets. Mark relay as waiting for user choice.

---

## Self-Review

- The plan covers all four requested areas in order.
- External writes are explicitly deferred to a human checkpoint.
- New Python behavior uses test-first steps.
- Configuration and workflow changes stay scoped to existing files.
