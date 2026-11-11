# Desktop Sticky Card

**一张随时可以看到，也可以交给 AI Agent 管理的桌面卡片。**

把待办、笔记和临时想法放在 Mac 桌面右上角。平时将鼠标移到菜单栏图标上即可查看；需要一直看到时，点击卡片上的 `Pinned`。你可以自己编辑内容，也可以直接对 Agent 说：“把明天下午三点的会议记到桌面卡片。”

[快速开始](#快速开始) · [功能介绍](#功能介绍) · [让-agent-使用卡片](#让-agent-使用卡片) · [macOS 详细说明](mac/README.md) · [Windows 版](README.windows.md)

## 快速开始

### 让 Agent 帮你安装

把下面这段话发给能在你的 Mac 上运行命令的 Agent：

> 请帮我在这台 Mac 上安装并启动 Desktop Sticky Card：https://github.com/ChenJinCloud/desktop-sticky-card。请先阅读安装说明，配置 CLI 和可用的 Agent Skill，再添加一条测试待办并检查是否写入卡片。如果缺少依赖或遇到文件冲突，请告诉我，不要覆盖现有内容。

安装后，你可以继续对 Agent 说：

- “把明天下午三点的线下交流记到桌面卡片。”
- “看看卡片上还有哪些待办。”
- “把已经完成的会议标记为完成。”
- “把今天的工作进展追加到卡片里。”

### 自己在终端安装

**安装要求：**macOS 11 或更新版本、Git、Apple 命令行工具，以及 Python 3.8+ 和 Tk 8.6+。安装器会检查这些依赖；如果缺少依赖，需要先安装。

```bash
bash -o pipefail -c 'curl -fsSL https://raw.githubusercontent.com/ChenJinCloud/desktop-sticky-card/master/install-macos.sh | bash'
```

安装完成后，启动卡片：

```bash
~/.local/bin/sticky-card-start
```

在屏幕右上角找到菜单栏图标，将鼠标移上去即可展开卡片。点击 `Pinned` 可以让它一直显示；再次点击切回悬停模式。右键菜单栏图标，选择 `Quit Sticky Card` 可以退出。

安装器遇到已有同名命令、Skill 或不属于本项目的安装目录时会停止，避免覆盖已有文件。重复运行会保留现有数据，已有安装目录不会自动更新。手动安装和依赖排查请看 [macOS 详细说明](mac/README.md)。

## 功能介绍

### 随时查看待办和笔记

卡片支持 Markdown 标题、列表和普通文字。点击待办可以切换完成状态；使用 `All / Todo` 切换全部内容和未完成任务。点击 `Edit` 直接编辑，按 `Cmd + S` 保存，按 `Esc` 取消。

### 固定显示或悬停查看

需要持续关注时，点击 `Pinned` 将卡片固定在右上角。切换为 `Unpinned` 后，鼠标移到菜单栏图标上展开，移出图标和卡片后自动收起。固定状态会在重启后恢复。

### 调整卡片外观

卡片提供 8 套主题和 5 档字号，可拖动边缘调整大小。点击 `T` 可以显示或隐藏时间戳。

### 减少截图中的内容暴露

卡片窗口使用 macOS 的窗口共享限制，减少内容出现在截图中的机会。不同截图和录屏工具的行为可能不同，请使用自己的工具确认。

### 内容保存在本地

卡片内容是本地 Markdown 文件，桌面卡片和 CLI 使用同一份数据。应用会保存每日快照；你也可以用其他编辑器打开内容文件。

## 让 Agent 使用卡片

安装器会设置 `sticky-card` 命令，并将可移植 Skill 链接到 Codex、Claude Code、WorkBuddy 和共享 `.agents/skills` 目录。DeepSeek Harness 和豆包工作可以使用共享入口；Grok Bot 可以在本机执行功能可用时调用 CLI。

Agent 需要能在你的 Mac 上运行命令并访问卡片文件，才能操作同一张卡片。不同 Agent 的 Skill 发现方式、沙箱和文件权限可能不同；如果 Agent 没有自动发现 Skill，可以让它使用 `~/.local/bin/sticky-card`。云端 Agent 需要具备访问这台 Mac 的能力。

你也可以直接使用 CLI：

```bash
# 添加任务并查看当前任务
~/.local/bin/sticky-card add '准备本周复盘'
~/.local/bin/sticky-card show

# 标记第 1 条任务完成
~/.local/bin/sticky-card done 1

# 追加笔记并查看整张卡片
printf '## 进展\n已完成资料整理\n' | ~/.local/bin/sticky-card append --stdin
~/.local/bin/sticky-card content

# 查看全部命令
~/.local/bin/sticky-card --help
```

任务编号会随内容变化，操作前请先用 `show` 确认。`append` 保留已有内容；`write` 会替换整张卡片，`clear` 会删除所有已完成任务。

## 数据和设置

默认安装在 `~/.local/share/desktop-sticky-card`，卡片内容位于 `mac/card-content.md`，窗口设置位于 `mac/.card-state.json`。每日快照保存在 `mac/card-history/YYYY-MM-DD/`，记录当天首次触发时已有的文件。

如果想将数据放在其他目录，启动卡片和调用 CLI 前都要设置相同的环境变量：

```bash
export DESKTOP_STICKY_CARD_HOME="$HOME/.desktop-sticky-card"
```

## Windows 版

Windows 版的功能和启动方式见 [Windows 版说明](README.windows.md)。

## 反馈与许可

遇到问题或有功能建议，欢迎通过 [GitHub Issues](https://github.com/ChenJinCloud/desktop-sticky-card/issues) 反馈。

本项目采用 [MIT License](LICENSE)。
