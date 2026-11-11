# Desktop Sticky Card — macOS Edition

菜单栏待办卡片。可固定在屏幕右上角，也可在鼠标移到菜单栏图标时展开。

## 与 Windows 版的区别

| 项目 | Windows | macOS |
|------|---------|-------|
| 单实例锁 | msvcrt | fcntl |
| DPI | ctypes.windll Per-Monitor | Retina 原生支持，无需处理 |
| 无标题栏字体 | Segoe UI | Helvetica Neue |
| 字号基准 | 偏小（适配 Windows 渲染） | 偏大 1pt（适配 macOS 渲染） |
| 编辑快捷键 | Ctrl+S | Cmd+S |
| 默认编辑器 | notepad | nano |
| 启动脚本 | .bat | .sh |
| resize 热区 | 6px | 8px（适配 trackpad） |
| resize 光标 | size_nw_se / size_ne_sw | bottom_right_corner / bottom_left_corner |

## 特性

- **菜单栏卡片** — 鼠标悬停展开，或固定在屏幕右上角持续显示
- **点击勾选** — 直接在卡片上点击任务切换完成状态，自动记录完成时间
- **All / Todo 视图** — 一键切换，展开全部或只看未完成
- **8 套主题** — Light / Dark / Macaron (Rose/Mint/Lavender) / Morandi (Green/Blue/Rose)
- **5 档字号** — XS / S / M / L / XL
- **可调大小** — 拖拽边缘调整宽高
- **卡片上直接编辑** — 点 Edit 进入编辑模式，Cmd+S 保存，Esc 取消
- **时间戳** — 创建时间自动记录，可一键显示/隐藏
- **对话终端** — 直接打字添加任务，支持 `1.xxx；2.xxx` 批量录入
- **文件驱动** — 内容就是 `card-content.md`，任何编辑器都能改
- **轻依赖** — 使用 Python、tkinter 和 macOS Swift 命令行工具

## 环境要求

- Python 3.8+
- macOS 11 或更新版本
- Tk 8.6+。近期 macOS 上不要使用系统 Python 自带的 Tk 8.5；它可能只显示空白窗口。推荐安装 `brew install python-tk@3.14`
- macOS Swift 命令行工具（`/usr/bin/swift`），用于菜单栏图标

## 快速启动

新用户可在终端执行以下命令，下载项目并安装 CLI 与可移植 Skill：

```bash
bash -o pipefail -c 'curl -fsSL https://raw.githubusercontent.com/ChenJinCloud/desktop-sticky-card/master/install-macos.sh | bash'
```

安装前需要 Git、Apple 命令行工具，以及带 Tk 8.6+ 的 Python。安装器不会自动安装这些依赖，也不会覆盖已有同名命令或 Skill；如有冲突，它会停止并显示路径。安装完成后运行 `~/.local/bin/sticky-card-start` 启动卡片。若 `~/.local/bin` 不在 PATH 中，用完整路径调用 CLI。

安装器将 Skill 链接到 Codex、Claude Code、WorkBuddy 及共享 `.agents/skills` 目录。DeepSeek Harness 和豆包工作已在本机验证可发现或使用对应入口；其他机器的技能发现与本机文件权限需在各 Agent 中验证。Grok Bot 需要在其本机执行功能可用时，通过命令路径调用；不保证自动发现 Skill。云端 Agent 无法仅靠安装文件直接操作用户 Mac。

已经克隆项目的用户也可以从项目根目录执行 `bash install-macos.sh`。现有安装目录不会自动更新，以免覆盖本地改动和卡片数据。

从源码手动启动：

```bash
# 在完整项目目录中运行；macOS 版会复用上一级 shared/ 存储模块
cd mac

# 首次使用：仅在内容文件不存在时复制示例
test -e card-content.md || test -L card-content.md || cp card-content.example.md card-content.md

# 赋予执行权限（仅首次）
chmod +x start.sh chat.sh card.sh python-with-tk.sh

# 启动菜单栏卡片
./start.sh

# 如需同时启动对话终端
./start.sh --chat
```

单独启动：

```bash
# 只启动卡片
./python-with-tk.sh sticky-card.py

# 只启动对话终端
./chat.sh

# CLI 单命令
./card.sh 写周报
./card.sh 整理 周报 数据
./card.sh add "写周报"
./card.sh done 1
```

直接输入的文字会自动作为新任务；因此任务包含空格时也不需要加引号。`add` 写法仍然兼容。

## Agent 调用 CLI

Agent 可以通过 CLI 读取或更新同一张卡片。默认数据位于安装目录的 `mac/card-content.md`；如果 GUI 使用了 `DESKTOP_STICKY_CARD_HOME`，调用 CLI 时也要设置为相同目录。

```bash
# 读取完整 Markdown；show 只列出任务
~/.local/bin/sticky-card content

# 新增任务，或追加多行普通内容
~/.local/bin/sticky-card add "整理本周进展"
printf '## 进展\n已完成资料整理\n' | ~/.local/bin/sticky-card append --stdin

# 处理任务与查看帮助
~/.local/bin/sticky-card show
~/.local/bin/sticky-card done 1
~/.local/bin/sticky-card --help
```

`append` 保留已有内容，`--stdin` 接收多行文本。写入与 GUI 共用锁和本地每日快照。任务编号会随内容变化，执行完成或删除前应先用 `show` 查看当前编号。`write` 会替换全部卡片内容，只在明确需要覆盖时使用。

GUI、CLI 和对话终端使用同一套跨进程锁、原子写入和每日快照逻辑。如需将个人数据与源码分开，可在启动前设置：

```bash
export DESKTOP_STICKY_CARD_HOME="$HOME/.desktop-sticky-card"
```

## 卡片顶栏

| 按钮 | 功能 |
|------|------|
| ● Pinned | 切换置顶/非置顶 |
| XS/S/M/L/XL | 字号 |
| Light/Dark/... | 主题 |
| All / Todo | 全部 / 只看未完成 |
| T | 显示/隐藏时间戳 |
| Edit | 编辑模式（Cmd+S 保存，Esc 取消） |
| ✕ | 关闭 |

## 文件结构

```
mac/
├── card-content.md    # 卡片内容（Markdown，编辑即生效）
├── sticky-card.py     # 卡片 GUI
├── cardlib.py         # 共享库
├── chat.py            # 对话终端
├── card.py            # CLI 工具
├── start.sh           # 启动菜单栏卡片；--chat 同时启动终端
├── chat.sh            # 单独启动对话终端
├── card.sh            # CLI 入口
├── .card-state.json   # 显示偏好（自动生成）
└── README.md
```

项目根目录的 `shared/cardstore.py` 是 Windows 与 macOS 共用的数据层，因此分发时需要同时保留 `shared/` 目录。

点击卡片上的 `Pinned` 可将卡片固定在屏幕右上角并持续显示；再次点击切换为 `Unpinned` 后，鼠标移到菜单栏图标上可展开卡片，移出图标和卡片后会自动收起。固定状态会保存，重启后恢复。右键点击菜单栏图标并选择 `Quit Sticky Card` 可退出。卡片窗口设置了 macOS 的窗口共享限制，以减少其出现在截图中的机会；不同截图和录屏工具的行为可能不同，请在使用的工具中确认。

`python-with-tk.sh` 会依次寻找带 Tk 8.6+ 的 Python，并拒绝已知可能产生空白窗口的系统 Tk 8.5。也可以通过 `PYTHON_WITH_TK` 明确指定兼容的解释器。

## License

MIT
