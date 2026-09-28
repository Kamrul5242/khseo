# Host adapters

The KHSEO core (`SKILL.md` + `rules/` + `workflows/` + `templates/`) is provider-neutral. An
adapter only explains how to load it into a particular host. Installing KHSEO grants **no**
access by itself — the host decides which tools (files, web, terminal, git, deploy) exist.

| Host | How to install |
|---|---|
| **Claude Code** | Copy/clone the repo folder to `~/.claude/skills/khseo/` (personal) or `.claude/skills/khseo/` (project). Claude loads it when you say "KHSEO …". |
| **Claude.ai / Claude Desktop** | Settings → Capabilities → Skills → upload a ZIP of this folder. |
| **Claude Agent SDK / API** | Upload as a custom skill, or place in the agent's skills directory. |
| **ChatGPT (Custom GPT / Project)** | Paste [system-prompt.md](system-prompt.md) into Instructions; upload `rules/`, `workflows/`, `templates/` files as Knowledge. |
| **Gemini (Gem) / Gemini CLI** | Gem: paste [system-prompt.md](system-prompt.md). CLI: add it to `GEMINI.md` and reference the folder. |
| **Cursor** | Add `.cursor/rules/khseo.mdc` containing [system-prompt.md](system-prompt.md) and keep the folder in the repo. |
| **GitHub Copilot** | Put [system-prompt.md](system-prompt.md) in `.github/copilot-instructions.md`. |
| **Codex / OpenCode / generic agents** | Reference the folder from `AGENTS.md` (see [AGENTS.md](AGENTS.md)). |
| **Any API agent (DeepSeek, Qwen, Mistral, Grok, local LLMs)** | Use [system-prompt.md](system-prompt.md) as the system message; give the agent file-read access to this folder, or inline the files it needs. |

After loading, a host with tools should run a capability check the first time KHSEO is used
(see `templates/approval-request.md` → "Capability check").
