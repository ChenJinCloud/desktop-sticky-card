# Desktop Sticky Card — macOS Edition

始终悬浮在桌面上的待办卡片，不需要切换窗口，余光就能扫到接下来要做的事。

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

- **桌面置顶** — 悬浮在所有窗口之上，始终可见（可切换）
- **点击勾选** — 直接在卡片上点击任务切换完成状态，自动记录完成时间
- **All / Todo 视图** — 一键切换，展开全部或只看未完成
- **8 套主题** — Light / Dark / Macaron (Rose/Mint/Lavender) / Morandi (Green/Blue/Rose)
- **5 档字号** — XS / S / M / L / XL
- **可调大小** — 拖拽边缘调整宽高
- **卡片上直接编辑** — 点 Edit 进入编辑模式，Cmd+S 保存，Esc 取消
- **时间戳** — 创建时间自动记录，可一键显示/隐藏
- **对话终端** — 直接打字添加任务，支持 `1.xxx；2.xxx` 批量录入
- **文件驱动** — 内容就是 `card-content.md`，任何编辑器都能改
- **零依赖** — 仅 Python 标准库 tkinter

## 环境要求

- Python 3.8+
- macOS 自带 tkinter（如果使用 Homebrew Python，需要 `brew install python-tk`）

## 快速启动

```bash
# 首次使用：复制示例内容文件
cp card-content.example.md card-content.md

# 赋予执行权限（仅首次）
chmod +x start.sh chat.sh card.sh

# 启动（卡片 + 对话终端）
./start.sh
```

单独启动：

```bash
# 只启动卡片
python3 sticky-card.py

# 只启动对话终端
./chat.sh

# CLI 单命令
./card.sh add "写周报"
./card.sh done 1
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
├── start.sh           # 一键启动：卡片 + 对话终端
├── chat.sh            # 单独启动对话终端
├── card.sh            # CLI 入口
├── .card-state.json   # 显示偏好（自动生成）
└── README.md
```

## License

MIT
