# HL42 Profile — Minimal macOS Terminal 定稿

## 最终选择

2026-11-24，用户从三个实际实现中选择了第一个 Minimal macOS Terminal。本目录为该方案的独立最终文件；不是新一轮视觉修改。README 和全部 SVG 与用户审阅的第一版逐字节一致。其余两个方案、上一轮 Creative Hybrid、原始 README 快照和全部预览仍保留。

本地定稿后，用户进一步明确授权 push。发布沿用选定的设计，不修改仓库可见性；原始 README 保留在 Git 历史与 docs/archive/README.original.md。

## 设计与实现

使用 macOS Terminal 风格窗口、静态红黄绿控制按钮、原创 HUNTER 线条字标、绿色 zsh 提示符和等宽正文。HUNTER 字形由 SVG path 构成，不依赖下载字体或第三方打字服务。

六个内容区域：whoami、cat profile.yaml、ls ~/projects、cat tech-stack.txt、systemctl status hunter、git log --activity。项目描述与入口、个人资料、技术分类和活动链接均保留为原生文本/链接，而不是整页截图。

SVG 自包含深色背景，桌面和手机分别排版，520px 以下选择移动版。GitHub 控制外部页面、原生文字、链接与代码块主题，README 无法强制整页深色或执行 JavaScript。本地预览控件不属于部署文件。

打字以 CSS 裁切动画在 1.6 秒内播放一次；光标每 1.1 秒闪烁，共六次后停止。减少动态效果时直接显示完整命令。动画被禁用时内容仍完整可读。没有外部图片、字体、脚本、foreignObject、统计卡或 Badge 服务。

## 内容依据

身份、教育、实习和技术背景来自本人公开个人网站源码；项目内容重新核对公开 README 和依赖文件。RepoWiki 是 Go/Vue 本地工具，生成调用外部模型；RAG Agent 是 TypeScript/Next.js/pgvector；SaveWise 当前使用 React/TypeScript/Supabase/PostgreSQL，未沿用旧 MongoDB 描述。Ciravo 为预发布产品，没有公开应用源码，因此没有编造仓库入口或独立核实的技术栈。

个人状态是明确标识的比喻，没有虚构 uptime、生产健康或项目在线情况。教育仍标为 May 2027 expected。公开网站中的实习经历是本人发布的事实，不是第三方背景调查。

## 真实活动记录

activity.json 和 README 活动区使用 GitHub 官方公开 Events API 的真实快照，并保留采集时间、UTC 事件时间和实际提交/分支链接。当前包含四次推送、一次分支创建。没有生成提交消息、贡献日历、活跃天数或完整贡献统计。

公开 API 的返回范围有限，空列表不代表没有工作。更新器只选取 HL42 自己的公开 push/branch-create 事件，排除 HL42/HL42 维护事件，按时间排序去重，并转义外部标签。缺少 SHA 时标明不可用；网络/API 错误或缺少更新标记时拒绝覆盖旧内容。git log --activity 是展示标题，不是真实 Git 参数。

## 验证

所选方案已通过 1060px、390px、320px × Light/Dark 共六组浏览器布局检查，无坏图、页面横向溢出或代码块滚动。三个候选方案共 18 组检查通过。12 个 SVG 均经 XML 解析、可访问名称与外部资源检查。

浏览器确认打字遮罩从 27.5px 展开至完整 330px，减少动态效果时立即为 330px。原生链接、标题结构、事件排序/去重/转义/缺 SHA/错误响应/缺标记保护均经检查。11 个公开项目及事件目标返回 HTTP 200；LinkedIn 页面内容和邮箱投递未验证。

Actions YAML 已解析，固定的 checkout/upload-artifact 提交已核实，Python 验证命令已执行。尚未在远端运行 Actions。GitHub/Camo 最终的 SVG 动画、缓存、手机和主题行为仍需发布后的实页验收；本地截图不等于在线截图。

## 维护

部署文件为本目录的 README.md、assets/、scripts/、activity.json 和 .github/workflows/profile.yml。retrospective.md 可按需一同保留。不需要 npm 或服务端来展示 Profile。

离线检查：

```sh
python3 scripts/validate.py
```

获取最新真实公开活动，只更新本地文件：

```sh
python3 scripts/activity.py
python3 scripts/validate.py
```

更新器只替换 README 中 ACTIVITY:START/END 之间的内容，并更新 activity.json。首次访问无需个人令牌；CI 使用只读 GITHUB_TOKEN。API 失败时保留旧快照。离线重放可用 --from-file，配合 --fetched-at 记录原采集时间。

随附工作流对 push/PR 做离线检查；手动或每天 12:23 UTC 刷新公开事件后输出审阅 artifact。权限仅 contents: read，不 commit、不 push，不自动写回公开 Profile。工作流随已授权发布的文件一同提交。需要全自动写回 Profile 时再单独确定发布策略。

内容调整直接修改最终 README 和 SVG。若要重新生成三方案评审，使用上层 terminal-lab/tools/build.py；该生成器读取冻结的原始活动快照，不应覆盖最终目录的新活动。更多源码和预览工具保存在 terminal-lab，不必复制到公开仓库。

已获发布授权。合入前对照远端最新文件，保留新内容并运行离线检查；使用预期分支头保护发布，避免覆盖并发修改。发布后在实际 GitHub 页面检查 Light/Dark、手机、链接和动画。
