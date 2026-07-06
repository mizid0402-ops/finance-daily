# GitHub Remote Setup Decision Guide

本文件用于准备 GitHub 远端仓库、Actions secrets/variables 和 RSS 发布地址。当前 work-block 只做准备，不执行外部写入。

## 当前本地状态

- 本地 Git 仓库已初始化。
- 当前分支：`master`
- 已有本地提交包含源码、测试、GitHub Actions workflow、relay 状态和当前生成产物。
- workflow 会生成并提交：
  - `backup/*.md`
  - `rss.xml`

SQLite 数据库 `data/finance_daily.sqlite` 是本地运行产物，不应上传到 GitHub。

## 需要你决策的事项

### 1. GitHub 仓库

请选择仓库创建方式：

- 新建仓库：例如 `finance-daily`
- 使用已有仓库：需要提供 remote URL

请选择可见性：

- Private：适合包含生成数据库、草稿和未来配置细节
- Public：适合直接公开 RSS 和 Markdown 产物

### 2. 默认分支

当前本地分支是 `master`。可选：

- 保持 `master`
- 改为 `main`

如果要改为 `main`，需要在推送前执行：

```powershell
git branch -M main
```

### 3. RSS 发布 URL

`SITE_URL` 控制 `rss.xml` 中的频道链接和日报条目链接。

可选方案：

- GitHub Pages：例如 `https://<user>.github.io/<repo>`
- raw GitHub 文件地址：不推荐长期使用，但可临时验证
- 自有域名或静态站点：例如 `https://daily.example.com`
- 暂时使用默认值：`https://example.com/finance-daily`

如果选择 GitHub Pages，需要后续决定 Pages 来源，例如：

- 从仓库根目录发布
- 从 `docs/` 发布
- 从 Actions artifact 或独立分支发布

当前 workflow 只提交生成产物，不配置 Pages。

### 4. GitHub Secrets 和 Variables

建议配置：

| 类型 | 名称 | 是否必需 | 说明 |
|---|---|---:|---|
| Secret | `OPENAI_API_KEY` | 否 | 不设置时使用 fallback 规则模板 |
| Secret | `OPENAI_BASE_URL` | 否 | DeepSeek/OpenAI-compatible API 地址 |
| Secret | `OPENAI_MODEL` | 否 | 模型名 |
| Variable 或 Secret | `SITE_URL` | 否 | RSS 发布基 URL；优先 `vars.SITE_URL`，再回退 `secrets.SITE_URL` |

如果没有 `OPENAI_API_KEY`，Actions 仍会运行并生成规则模板日报。

### 5. 首次远端推送

确认仓库和分支后，典型命令是：

```powershell
git remote add origin <REMOTE_URL>
git push -u origin master
```

如果改用 `main`：

```powershell
git branch -M main
git remote add origin <REMOTE_URL>
git push -u origin main
```

## 建议路径

推荐低风险路径：

1. 创建 Private 仓库。
2. 保持当前 `master` 分支，先完成首次 push。
3. 配置 `SITE_URL` 为未来计划发布地址，或者暂时不设置。
4. 先手动触发一次 workflow，确认 tests/generation/commit 行为。
5. 再决定是否启用 GitHub Pages 或公开 RSS。

## 停止条件

在你确认以下信息前，不应自动执行远端操作：

- 仓库是新建还是已有
- 仓库可见性
- remote URL
- 默认分支名
- 是否配置 GitHub Pages
- `SITE_URL` 的真实值
- 是否现在推送本地提交
