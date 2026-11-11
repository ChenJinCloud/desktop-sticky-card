---
name: desktop-sticky-card
description: Use when the user wants to read or update their Mac desktop sticky card, including adding notes and tasks through its CLI.
---

# Desktop Sticky Card

The local card displays the user's notes and tasks. Use `sticky-card` or, if it is not on PATH, `"$HOME/.local/bin/sticky-card"`. If neither is executable, or the agent runs remotely or in a sandbox without access to the Mac, explain the limitation; do not create a separate card and claim it is the desktop card.

```bash
sticky-card content
sticky-card show
sticky-card add '准备项目周报'
printf '## 进展\n已完成资料整理\n' | sticky-card append --stdin
sticky-card done 1
sticky-card --help
```

`content` reads the full Markdown; `show` lists tasks. Read current tasks before changing an item by number: concurrent edits can change the numbering. Unknown command words are treated as new tasks. Append rather than overwrite unless the user explicitly requests replacement: `write` replaces the whole card, and `clear` removes completed tasks. Check the exit status and read back the requested result.

The CLI and GUI must use the same `DESKTOP_STICKY_CARD_HOME` if a custom data directory is set. By default both use the installed project's `mac` directory. CLI success does not establish that the window is visible. WorkBuddy may ask for confirmation when an atomic write replaces its temporary file; follow its normal approval flow.
