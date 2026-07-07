# 财经 AI 日报系统

自动抓取最近 24 小时财经新闻，进行去重、分类、事件聚类，并通过 OpenAI-compatible 接口生成中文财经日报，同时输出 Markdown 备份、RSS 和 SQLite 数据。

## MVP 功能

- RSS 财经新闻抓取，默认覆盖 Yahoo Finance、CNBC、MarketWatch、NASDAQ、WSJ、Seeking Alpha，并支持配置中文源。
- URL / 标题去重，SQLite 持久化保存文章与日报。
- 财经分类与事件聚类。
- DeepSeek / OpenAI 兼容接口生成日报。
- API 不可用时生成规则模板草稿，不中断 Markdown、RSS 和 SQLite 输出。
- 输出 `backup/YYYY-MM-DD.md`、`rss.xml` 和 `data/finance_daily.sqlite`。

## 本地运行

```powershell
cd "F:\workspace\小玩意\财报每日推送"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

$env:OPENAI_API_KEY="你的 key"
$env:OPENAI_BASE_URL="https://api.deepseek.com"
$env:OPENAI_MODEL="deepseek-chat"

python src/main.py
```

> **可选环境变量 `SITE_URL`**：控制 RSS 频道和文章链接的基 URL。不设置时默认为 `https://example.com/finance-daily`。  
> 示例：`$env:SITE_URL="https://daily.example.com"`。末尾携带斜杠会被自动处理，不会产生 `//` 双斜杠。

如果 Windows 中 `python` 指向 Microsoft Store shim，可改用：

```powershell
py src/main.py
```

## 配置新闻源

编辑 `config/sources.yml`：

```yaml
sources:
  - name: Yahoo Finance
    url: https://finance.yahoo.com/news/rssindex
```

单个 RSS 源失败或超时不会中断整次日报生成。

## 日报结构

```markdown
# 财经日报-YYYY-MM-DD

## 一、市场总览
## 二、今日核心事件
## 三、产业链受益方向
## 四、资金更该关注什么类型的公司
## 五、相关公司映射
## 六、风险提示
## 七、明日关注
```

分析链路固定为：事件催化 -> 产业需求与供给验证 -> 产业链受益环节 -> 资金更该关注什么类型的公司 -> 相关公司映射 -> 风险提示。

## GitHub Actions

Workflow 每天 UTC 23:00（北京时间次日 07:00）自动运行，也支持手动触发（workflow_dispatch）。Job 环境变量 `TZ=Asia/Shanghai`，确保 `date` 和 Python 日期 API 均以北京时间为准。

### 配置

需要在 GitHub 仓库中设置以下 **Secrets**（可选 — 缺失时应用会降级为规则模板草稿）：

| Secret | 说明 |
|---|---|
| `OPENAI_API_KEY` | OpenAI / DeepSeek 等兼容 API 密钥 |
| `OPENAI_BASE_URL` | API 地址，如 `https://api.deepseek.com` |
| `OPENAI_MODEL` | 模型名，如 `deepseek-chat` |

以及可选的 **Variables**（或同样以 Secrets 方式设置）：

| Variable / Secret | 说明 |
|---|---|
| `SITE_URL` | RSS 频道链接的基 URL。不设置时应用内部 fallback `https://example.com/finance-daily`。优先读取 `vars.SITE_URL`，未设置时回退到 `secrets.SITE_URL`。 |

> SITE_URL 也可通过本地 `.env` 文件或环境变量设置，见"本地运行"一节。

### 流程说明

1. **安装依赖** — `pip install -r requirements.txt`（启用 pip 缓存加速）
2. **运行测试** — `python -m pytest -q`，测试失败时终止 workflow
3. **生成日报** — 执行主程序，输出 `backup/*.md`、`rss.xml`，并在运行环境内更新本地 SQLite 数据库
4. **提交产出** — 仅提交 `backup/*.md` 和 `rss.xml`；本地 SQLite 数据库不会提交；Commit 消息包含执行日期（北京时间）

### 并发控制

同一分支的调度与手动运行不会重叠，避免生成输出提交冲突。调度事件（schedule）下 checkout 会显式检出分支而非 detached HEAD，确保后续 push 正常工作。

### 推送可靠性

Push 失败后会自动 rebase 重试，最多 3 次，避免因并发运行导致提交冲突而中断。使用显式目标 `origin HEAD:<branch>` 推送，确保 detached HEAD 下依然正确提交。如果 3 次均失败，workflow 以非零退出码终止。

远端仓库、分支、RSS 发布 URL、Secrets/Variables 和首次 push 的决策清单见 `docs/github-remote-setup.md`。

## 免责声明

本系统仅用于公开信息聚合与研究辅助，不构成投资建议，不提供买入、卖出、目标价或收益承诺。公司映射需要结合公告、财报、监管文件和市场数据进一步核验。
