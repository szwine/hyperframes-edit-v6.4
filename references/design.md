# hyperframes-edit v5 — 视觉设计说明（动效 / 图标 / 科技感）

> 配套 `scripts/build_html.py` 自动实现。本文说明「为什么这样做」，便于调风格时改 CSS/SVG。
> v5 = 柱子哥 @柱子哥TzFilm 真实成片逐帧实测后的精修版。

## 设计目标
在 v4「真实语音对齐 + 顶部安全区」基础上，把"高级感"做细：字幕要**会跳动**、图标要**自动贴合语义**、角落要**有持续旋转的徽章**、HUD 要**有呼吸感**。同时保证：不挡原视频已有字幕、不溢出、声画保真、**绝不改动原画面**。

## 1. 顶部安全区
- 字幕容器 `top:9%`（v4 是 7%，柱子哥实测更靠上更醒目），`max-width:calc(100% - 80px)` 居中。
- 先用 `ffmpeg` 抽 `frame0.png` 目测；若顶部有内容，抬高到 `top:5%` 或改两侧浮条。

## 2. 字幕"跳动"（v5 核心）
- 每句拆成 `<span class="ch">`，GSAP 用 `stagger` 让字**逐个弹出**（scale 0.7→1 + 发光），节奏 = `句时长 / 字数`（上限 0.16s/字），即"跟着说话速率走"。
- 容器进场 `back.out` 上滑；进场后再做一次轻微 `scale 1.035` 呼吸（yoyo），让当前句"活"起来。
- 句尾前 0.35s 淡出 + 结束点硬杀防残留。

## 3. 每段小图标（v5 自动语义分配）
- `keyword_icon()` 按文案关键词挑图标（见 SKILL.md 映射表），任意稿子通用，不再写死段号。
- 图标库（霓虹三色 + drop-shadow 发光）：spark/bolt/question/arrow/heart/robot/health/exo/number1-3/lightbulb/share/chat/user/flag。
- 图标内联在 `.cap-text` 开头，不参与逐字动画（静态），文字逐字弹出。

## 4. 常驻角落旋转徽章（v5 新增）
- 一个固定在角落（默认右上 `tr`）的圆形徽章：虚线旋转环（`cbspin` CSS 无限转）+ 内圈 + 中心发光字形（取 `corner_badge.glyph`）+ 底部标签。
- 用 **CSS 动画**而非 GSAP，确保被 headless 录屏稳定捕获（整片持续旋转）。
- 配置：`corner_badge.enabled / corner / glyph / label / spin_sec`。

## 5. HUD 科技底纹（v5 更细致）
- 常驻：`hud-vignette` 暗角、`dotgrid` 点阵（带 `dotpulse` 呼吸）、`scanlines` 扫描线、`hud-corners` 四角框。
- v5 新增：`sweep` 扫描线**扫掠**（自上而下循环）、`progress` 底部**进度条**（整片 scaleX 0→1）。
- 这些层挂在 `class="clip"` + `data-start=0 data-duration=总时长` 的 `.hud` 容器内，整片保留；`pointer-events:none`、`z-index:5`，不抢字幕。
- 角落徽章与进度条 `z-index:8/9`，在 HUD 之上、字幕（10）之下。

## 6. Hero 图片徽章（视觉爆点）
- `hero_map`：`{段号: ["图标png","标签"]}`。图片用 ImageGen 生成（透明、霓虹、约 1024²）放 `assets/`。
- 展示：圆形 `border-radius:50%` 裁切（裁掉 AI 水印）+ 外圈虚线旋转环（GSAP 有限旋转 360°，确保捕获）+ 标签。
- 默认素材：`icon_ai.png` / `icon_robot.png` / `icon_health.png` / `icon_exo.png`，每次按产品替换。

## 7. 配色与字体
- 主色青 `#00f0ff`；辅品红 `#ff4dff`、黄绿 `#39ff14`、暖黄 `#ffcc00`；文字白。
- 全部走 CSS 变量（`--primary` 等），改 `config.json` 的 `colors` 即全局换色。
- 字体优先 `Microsoft YaHei`（系统自带，`@font-face` 用 `local()` 免外网）。

## 8. 离线注意
- GSAP 从 `cdn.jsdelivr.net` 加载；无网时下载 `gsap.min.js` 到工程本地并改 `<script src>`。
- CSS 动画（角落徽章/扫掠/进度/点阵）不依赖外网，离线照常。

## 9. 交付前验证清单
- [ ] `out.mp4` 同时有 `h264`(video) 与 `aac`(audio) 流。
- [ ] 抽 2~3 帧确认字幕在顶部、未遮挡原字幕、角落徽章在转。
- [ ] hero 段徽章圆形裁切正常、水印已切除、环在转。
- [ ] 逐字跳动在播放时可见（非整句齐出）。
- [ ] 时长与源一致（±0.5s）。

## 10. 一句话给用户的承诺
"你录、我叠皮；原片不动，出来就是柱子哥那种——字会跳、段段有图标、角落徽章转、满屏科技感。"
