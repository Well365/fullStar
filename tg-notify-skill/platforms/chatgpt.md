# ChatGPT / Custom GPT

Plan A 为 **轻量 Skill**：依赖 Agent 能执行本地 shell。ChatGPT 网页版通常 **无法** 直接跑 `tg-notify` CLI。

## 适用场景

- **ChatGPT macOS 桌面版** + Advanced Data Analysis / 本地工具（若可用）
- **Custom GPT** 仅作 **Instructions 参考**（复制 SKILL.md 正文，去掉 YAML frontmatter）
- 需要真正执行时 → 使用 **Phase B：MCP HTTP 服务**（后续扩展）

## Custom GPT Instructions（粘贴 SKILL.md 正文）

1. 打开 Custom GPT 编辑器
2. 将 `SKILL.md` 中 `# tgkit` 以下章节粘贴到 Instructions
3. 说明：用户需在本机自行运行命令，或由配套 Automation 执行

## 无终端时的替代

| 方案 | 说明 |
|------|------|
| MCP Server | 暴露 `tg_send_text` 等 HTTP tools |
| n8n / Zapier | Webhook → 你的 Bot API 代理 |
| telegram_services Bot | 双向 Bot 收命令（非 Skill） |

Plan A 推荐优先在 **Cursor / Claude Code** 使用本 Skill。
