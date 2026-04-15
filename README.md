# Desktop Sticky Card

![Banner](banner.jpg)

## 解决什么问题

待办工具都需要主动打开才能看到。一旦需要"想起来才去看"，它就失去了锚点的意义。

Desktop Sticky Card 是一个始终悬浮在桌面上的待办卡片——不需要切换窗口，余光就能扫到接下来要做的事，随时确认自己的节奏和位置。

## 特性

- **桌面置顶** — 悬浮在所有窗口之上，始终可见（可切换）
- **点击勾选** — 直接在卡片上点击任务切换完成状态，自动记录完成时间
- **All / Todo 视图** — 一键切换，展开全部或只看未完成
- **8 套主题** — Light / Dark / 马卡龙（Rose / Mint / Lavender）/ 莫兰蒂（Green / Blue / Rose）
- **5 档字号** — XS / S / M / L / XL
- **可调大小** — 拖拽边缘调整宽高
- **卡片上直接编辑** — 点 Edit 进入编辑模式，Ctrl+S 保存，Esc 取消
- **全局快捷键** — Ctrl+Alt+Space 显示/隐藏卡片，Ctrl+Alt+N 快速添加任务
- **每日习惯打卡** — 独立视图，每天自动重置，顶栏 Habits 按钮切换
- **可折叠分区** — `##` 标题点击可展开/收起，适合放 OKR、目标、备忘等长内容
- **标签系统** — 任务加 `#标签名` 分类，筛选栏一键过滤，标签 badge 可显示/隐藏
- **时间戳** — 创建时间自动记录，可一键显示/隐藏
- **本地历史快照** — 每天自动保留一份完整文件快照，保存在应用目录下的 `card-history/`
- **对话终端** — 直接打字添加任务，支持 `1.xxx；2.xxx` 批量录入
- **文件驱动** — 内容就是 `card-content.md`，任何编辑器都能改
- **高 DPI 支持** — Per-Monitor DPI 感知，文字清晰锐利
- **状态自动保存** — 窗口位置、大小、主题、字号、显示偏好全部持久化
- **零依赖** — 仅 Python 标准库 tkinter

## 快速启动

```bash
# 首次使用：复制示例文件
cp card-content.example.md card-content.md
cp card-habits.example.md card-habits.md
cp card-tags.example.json card-tags.json

# 启动
双击 start.bat
```

同时启动桌面卡片 + 对话终端。

![Demo](demo.gif)

在终端里直接打字就能操作：

```
> 写周报
  ✓ 已添加: 写周报

> 1.买菜；2.做饭；3.洗碗
  ✓ 已添加: 买菜
  ✓ 已添加: 做饭
  ✓ 已添加: 洗碗

> 完成 1
  ✓ 完成: 写周报

> 帮助
  （查看所有命令）
```

也可以双击 `sticky-card.pyw` 单独启动卡片，用 Edit 模式或任何编辑器修改 `card-content.md`。

## 对话终端命令

| 命令 | 功能 | 中文别名 |
|------|------|----------|
| 任意文字 | 添加为新任务 | — |
| `1.买菜；2.做饭` | 批量添加多条任务 | — |
| `done 1` | 勾选第 N 条任务 | 完成、勾选、✓、v |
| `undo 1` | 取消勾选第 N 条 | 恢复、取消、撤销 |
| `rm 1` | 删除第 N 条任务 | 删除、删 |
| `clear` | 清除所有已完成任务 | 清空、清除 |
| `list` | 编号列出所有任务 | 列表、任务 |
| `show` | 显示完整卡片内容 | 看看、看、卡片 |
| `title xxx` | 设置卡片标题 | 标题 |
| `replace xxx` | 替换全部内容 | 替换、覆写、write |
| `edit` | 用编辑器打开 md 文件 | — |
| `help` | 帮助 | 帮助、? |
| `exit` | 退出 | 退出、quit、q、bye |

## 卡片操作

| 操作 | 功能 |
|------|------|
| 点击任务 | 勾选 / 取消勾选 |
| 拖拽任务 | 拖放排序 |
| 拖拽顶栏 | 移动窗口 |
| 拖拽边缘 | 调整窗口大小 |
| Edit → Ctrl+S | 保存编辑 |
| Edit → Esc | 取消编辑 |

## 快捷键

窗口底部会显示当前快捷键提示。默认快捷键如下：

| 快捷键 | 功能 |
|------|------|
| `Ctrl+Alt+Space` | 全局显示 / 隐藏卡片 |
| `Ctrl+Alt+N` | 全局快速添加任务 |
| `Ctrl+N` | 在卡片聚焦时快速添加任务 |
| `Enter` | 快速添加模式下保存并返回卡片 |
| 点击编辑框外 | 快速添加模式下保存并返回卡片 |
| `Ctrl+E` | 进入编辑；编辑中再次按下则保存 |
| `Ctrl+S` / `Ctrl+Enter` | 保存编辑 |
| `Esc` | 取消编辑 |
| `Ctrl+D` | All / Todo 视图切换 |
| `Ctrl+H` | Habits 视图切换 |
| `Ctrl+T` | 显示 / 隐藏时间戳 |
| `Ctrl+Shift+T` | 显示 / 隐藏标签 badge |
| `Ctrl+P` | Pinned / Unpinned 切换 |
| `Ctrl+Shift+C` | 切换主题 |
| `Ctrl+Shift+S` | 切换字号 |
| `Ctrl+Q` | 关闭卡片 |

## 开机自启（Windows）

将 `sticky-card.pyw` 的快捷方式放入启动目录即可：

1. 按 `Win + R`，输入 `shell:startup` 回车，打开启动文件夹
2. 右键 `sticky-card.pyw` → 发送到 → 桌面快捷方式
3. 将生成的快捷方式剪切到启动文件夹

取消自启：删除启动文件夹中的快捷方式即可。

## 本地历史快照

应用会在本地自动保存每日快照，目录为：

```text
card-history/YYYY-MM-DD/
```

窗口底部会显示完整路径，点击路径可打开文件夹。快照保存在当前应用文件夹内，不会上传到任何远程服务。

每个日期文件夹会保存当天首次触发快照时的完整文件副本：

- `card-content.md`
- `card-habits.md`
- `card-tags.json`
- `.card-state.json`
- `manifest.json`

这个策略是“每天一个完整版本”，用于恢复和追溯；不会自动切割或移动你的当前卡片内容。

## 卡片顶栏

| 按钮 | 功能 |
|------|------|
| ● Pinned | 切换置顶/非置顶 |
| XS/S/M/L/XL | 字号 |
| Light/Dark/... | 主题 |
| All / Todo | 全部 / 只看未完成 |
| Habits | 切换到每日习惯打卡视图 |
| Tag | 显示/隐藏任务行内标签 |
| T | 显示/隐藏时间戳 |
| Edit | 编辑模式（Ctrl+S 保存，Esc 取消） |
| ✕ | 关闭 |

## 文件结构

```
├── card-content.md         # 卡片内容（Markdown，编辑即生效）
├── card-habits.md          # 每日习惯（自定义，首次从 example 复制）
├── card-habits.example.md  # 每日习惯模板
├── card-tags.json          # 标签配置（自定义，首次从 example 复制）
├── card-tags.example.json  # 标签配置模板
├── card-history/            # 本地每日历史快照（自动生成）
├── sticky-card.pyw         # 卡片 GUI
├── cardlib.py              # 共享库
├── chat.py                 # 对话终端
├── card.py                 # CLI 工具
├── start.bat               # 一键启动：卡片 + 对话终端
├── chat.bat                # 单独启动对话终端
├── card.bat                # CLI 入口
├── .card-state.json        # 显示偏好（自动生成）
├── README.md
└── CHANGELOG.md
```

## Markdown 语法

| 语法 | 效果 |
|------|------|
| `# Title` | 大标题 |
| `## Title` | 可折叠分区（点击展开/收起） |
| `### Title` | 小标题 |
| `- [ ] Task` | 未完成任务 ☐ |
| `- [x] Task` | 已完成任务 ☑ |
| `- Item` | 列表项 |
| `---` | 分隔线 |
| `- [ ] Task #Tag` | 带标签的任务 |
| `*text*` | 斜体 |

## 标签

在 `card-tags.json` 中定义标签名，任务中用 `#标签名` 标记：

```json
{
  "tags": ["Work", "Personal", "Study", "Health"]
}
```

```markdown
- [ ] Review pull requests #Work
- [ ] Read chapter 5 #Study
```

卡片顶部会出现标签筛选栏，点击可按类别过滤任务。顶栏 Tag 按钮控制行内标签 badge 的显示/隐藏。标签颜色跟随当前主题自动切换。

## 可折叠分区

`##` 标题可以点击展开/收起，适合放目标、OKR、备忘等不需要时刻展示的内容：

```markdown
## Goals
- Revenue: $10,000 MRR
- Users: 5,000 WAU

## Sprint
- [ ] Design homepage #Work
- [ ] Fix login bug #Work
```

点击 `▼ Goals` 可收起该区域，变为 `▶ Goals`。折叠状态自动保存。分区范围从 `##` 标题开始，到下一个 `#`、`##` 或 `---` 结束。

## 环境要求

- Python 3.8+（需含 tkinter，Windows 默认包含）
- Windows 10/11

## License

MIT
