# Changelog

## [0.10.0] - 2026-04-07 22:30

### Fixed
- 单实例保护：使用 msvcrt 文件锁，防止重复打开多个卡片窗口
  - 先开卡片再运行 start.bat 不再产生第二个窗口

## [0.9.0] - 2026-04-07 22:00

### Changed
- **代码重构**: 提取 `cardlib.py` 共享模块，消除 chat.py 与 card.py 之间 ~140 行重复代码
  - 统一的文件读写、任务查询、增删改、多任务拆分、时间戳逻辑
- chat.py 重写：命令分发改为 dispatch table 模式，替代 12 个 if-elif 分支
- card.py 重写：精简至 ~80 行，所有业务逻辑委托给 cardlib
- 修复 `_toggle_task` 缺少 `line_idx < 0` 边界检查

## [0.8.0] - 2026-04-07 21:40

### Added
- 5 档字号切换（XS / S / M / L / XL），顶栏按钮点击循环切换
- 所有文字元素（标题、正文、时间戳、编辑器）跟随字号联动

## [0.7.0] - 2026-04-07 21:35

### Added
- 8 套主题配色：Light / Dark / Macaron Rose / Macaron Mint / Macaron Lavender / Morandi Green / Morandi Blue / Morandi Rose
- 顶栏主题切换按钮，点击循环切换
- 主题系统：所有 UI 颜色通过 `self.t()` 统一管理，切换时整体重建 UI

## [0.6.0] - 2026-04-07 21:25

### Fixed
- Windows 高 DPI 屏幕文字模糊：启动时声明 `SetProcessDpiAwareness(2)` Per-Monitor DPI Aware

## [0.5.0] - 2026-04-07 21:15

### Added
- 完成时间记录：勾选任务时自动追加 `done:MM/DD HH:MM` 时间戳，取消勾选时移除
- 已完成任务折叠：顶栏 All/Todo 按钮切换，Todo 模式隐藏所有已完成任务
- 创建时间显示/隐藏：顶栏 T 按钮切换，状态持久化
- 窗口可调大小：拖拽左右边缘和底部调整宽高
- 卡片直接编辑模式：点 Edit 进入 Markdown 编辑，Ctrl+S 保存，Esc 取消
- 窗口状态持久化：位置、大小、主题、字号、显示偏好保存到 `.card-state.json`
- 每 5 秒自动保存状态，防止进程被杀时丢失设置

## [0.4.0] - 2026-04-07 21:05

### Fixed
- **多任务拆分**: 输入 `1.xxx；2.xxx；3.xxx` 自动拆分为多条独立任务
- **任务插入位置**: 新任务插入到现有任务列表末尾（分隔线之前），不再追加到文件最后
- **bat 文件中文乱码**: 移除 .bat 文件中所有中文字符，避免 GBK/UTF-8 编码冲突
- **CHANGELOG 时间精度**: 所有记录精确到小时分钟

### Changed
- `chat.pyw` 重命名为 `chat.py`（需要控制台窗口，.pyw 语义是无窗口）
- 清理 card-content.md，移除示例任务和分隔线

## [0.3.0] - 2026-04-07 20:24

### Added
- `chat.py` 对话终端 — 双击打开，直接打字操作卡片，无需 AI
  - 输入任意文字默认添加为待办
  - 关键词触发：完成/恢复/删除/清空/列表/标题/替换/帮助/退出
- `chat.bat` 对话终端启动脚本
- `card.py` CLI 工具 — 单命令操作（card add/done/rm/clear/...）
- `card.bat` CLI 启动脚本
- 卡片任务项支持点击切换勾选状态（直接修改 card-content.md）

### Changed
- `start.bat` 改为同时启动卡片 + 对话终端

## [0.2.0] - 2026-04-07 20:00

### Changed
- 视觉风格从暗色主题重设计为 Medium 风格
  - 白色背景 + Georgia 衬线字体
  - Medium 品牌绿 #1A8917 作为强调色
  - 淡灰顶栏 + 细边框
  - 任务列表使用方框符号
- 置顶指示改为圆点 + Pinned/Unpinned 文字标签
- 关闭按钮增加 hover 效果

### Added
- README.md 项目文档
- CHANGELOG.md 开发变更日志
- start.bat 快捷启动脚本

## [0.1.1] - 2026-04-07 19:50

### Fixed
- Windows `overrideredirect(True)` 窗口焦点问题：使用 withdraw/deiconify/lift/focus_force 修复
- 移除 toolwindow 方案（会产生双层标题栏）

## [0.1.0] - 2026-04-07 19:40

### Added
- 初版桌面置顶卡片
- 暗色主题（Catppuccin Mocha 配色）
- Markdown 简易渲染（标题、任务列表、列表、水平线、斜体）
- 文件监听自动刷新（500ms 轮询）
- 窗口置顶/取消切换
- 无边框可拖拽窗口
- .pyw 后缀无黑窗启动
