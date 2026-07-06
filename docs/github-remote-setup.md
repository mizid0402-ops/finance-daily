# GitHub Remote Setup

This project is now connected to the existing GitHub repository:

```text
https://github.com/mizid0402-ops/finance-daily.git
```

## Current Local State

- Current branch: `main`
- Remote name: `origin`
- Fetch URL: `https://github.com/mizid0402-ops/finance-daily.git`
- Push URL: `https://github.com/mizid0402-ops/finance-daily.git`
- Upstream: `origin/main`

The local repository is already aligned with the requested remote address.

## GitHub Actions

The daily workflow is defined in `.github/workflows/daily.yml`.

Current repository configuration:

| Type | Name | Required | Notes |
|---|---|---:|---|
| Secret | `OPENAI_API_KEY` | Yes for LLM output | Configured in GitHub Actions secrets. |
| Variable | `OPENAI_BASE_URL` | Yes for DeepSeek | `https://api.deepseek.com` |
| Variable | `OPENAI_MODEL` | Yes for DeepSeek | `deepseek-v4-flash` |
| Variable | `SITE_URL` | Yes for published RSS links | `https://mizid0402-ops.github.io/finance-daily` |

If `SITE_URL` is not set, the application uses the fallback value:

```text
https://example.com/finance-daily
```

## GitHub Pages

GitHub Pages is enabled from the `main` branch root directory:

```text
https://mizid0402-ops.github.io/finance-daily/
```

## Useful Commands

Verify the remote:

```powershell
git remote -v
git branch -vv
```

Push the current branch if needed:

```powershell
git push -u origin main
```
