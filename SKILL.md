---
name: hyperframes-edit
description: 'Vertical short-video editing pipeline for Chinese spoken-word "动销" (sales-driving) videos. Takes a portrait talking-head clip plus a script, then renders an MP4. TWO MODES: (A) 富图层导演版【默认/定稿】— top karaoke captions + semantic per-segment icons + rotating corner badge + rich HUD + DIRECTOR-STYLE rich layers (data cards / spec tables / logic-collapse split-screen / quote cards / timeline / picture-in-picture / CTA) that are NOT a second subtitle track — only on key beats, with camera moves and left/right/top layout variety; (B) 轻量字幕皮 — v5 caption skin only. Use when a user asks to edit / cut / produce a 口播 / 口播动销 / 短视频 / 带货口播 video, especially "用 hyperframes 剪" or "hyperframes.edit", or "给我加赛博字幕 / 富图层 / 动效".'
agent_created: true
version: "6.4.0"
---

> 📌 **状态：已锁定为最终版 v6.4.0（富图层·动效剪辑版定稿，2026-07-22）**。
> 🏷️ **版本命名约定**：用户口中的「**富图层6.4版**」= 本「动效剪辑版本」——即这版（动效绑真实说话时间 `win` + 关键词增强 + 关叠字幕层 `show_caption:false` + 不挡脸）。之后用户说"6.4版 / 富图层6.4版"均指此定稿，**不要再回退**到 s/e 手填或 cap 绑"静音检测时间轴"的旧做法（那正是之前反复"动效抢跑"的隐藏根因）。
> 本版把「富图层导演版」(`gen_rich.py`) 定为默认/定稿形态，并**永久修好了"富图层根本不显示"的根因**（见下方⚠️致命坑）。**v6.4 关键升级（来自真实返工）**：
> 1. **动效与字幕彻底同步（根治"快很多"）**：每个 beat 用 `win:[t1,t2]` **直接给真实说话秒数**（优先用 faster-whisper 从音频提取，与剪映字幕同源），动效窗口 = 说话起+0.1s（略晚不抢跑）~ 说话止+0.35s（余韵），**绝不比字幕快**。废弃旧的"静音检测时间轴"（系统性偏早，正是之前反复抢跑的隐藏根因）。
> 2. **字幕层开关显式化**：原片已自带字幕时，config.json 设 `show_caption:false` 关掉本工具的字幕层，避免两排字幕、时间打架（v6.3 前"不同步"的隐藏根因之二）。
> 3. **动效≠第二套字幕**：内容只做**关键词增强**（简图/图标/表格/大数字），绝不重复口播长句——动效是给字幕"加料突出"，不是复读。
> 4. **绝不挡脸/不压字幕**：布局只走 `top/left/right/table`（已验证避开面部中央 25%~45% 与底部字幕区）；表格/大图放上半部并加 `scrim` 压暗。
> 5. 复合动效（数字滚动+图标脉冲+高亮词+入场退场+一次性运镜强调）照旧自动叠加。
> 之前尝试的写法全部淘汰，请勿复用。轻量字幕皮 `build_html.py` 保留为 Mode B。

# Hyperframes Edit (v6 — 富图层导演·定稿版)

## 这个 SKILL 是干嘛的（一句话）
你给我一支**竖屏口播录像 + 一份口播稿 + 一份富图层配置(beats.json)**，我跑这条管线，产出一支**顶部字幕 + 角落旋转徽章 + HUD + 关键节拍富内容层（数据卡/表格/分屏/引言/画中画/CTA）**的 MP4。**原画面不改动**，所有效果都是叠上去的一层"皮"。

## 两种模式
| 模式 | 生成器 | 输出 | 何时用 |
|---|---|---|---|
| **A 富图层导演版【默认/定稿】** | `scripts/gen_rich.py` | 字幕 + 徽章 + HUD + **富图层（非字幕复制品）** + 运镜 | 用户要"加料/富内容/动效/不像第二套字幕" |
| **B 轻量字幕皮** | `scripts/build_html.py` | 字幕 + 语义图标 + 徽章 + HUD（v5 风格） | 用户只要干净的赛博字幕皮 |

> 默认走 **Mode A**。它已经内嵌了字幕、徽章、HUD，并在关键节拍叠加富内容层——不再是"逐字同步第二套字幕"，而是**只在关键位置做动效、关键处有运镜、上半部分左右分屏位置多变**。

## ⚠️ 致命坑（本版才修好，务必记住）

### 坑 1：GSAP 动效不能写在外层 `.clip` 上（否则元素消失）
- 现象：富图层永远停在隐藏态（`autoAlpha:0`），成片里一个都看不到。
- 原因：hyperframes 引擎每帧会强制重置**带 `.clip` 元素**的内联 style（opacity/display），从而**覆盖 GSAP 的 `autoAlpha` 控制**。所以 **GSAP 动效只能写在内层（非 `.clip`）元素上**。
- 铁证：用 `chrome-headless-shell` 直接打开页面截图，富图层完美可见；但引擎渲染出来的成片看不到——证明问题在引擎对 `.clip` 的每帧重置。
- ✅ **v6.1 正确写法**（同官方 `graphics.html` 的 `.moment`）：富图层结构 = **外层 `.clip sc sc-xxx` + `data-start/data-duration`（引擎按窗口显隐）** + **内层 `.sc-inner`（非 `.clip`，纯 GSAP 做入场/退场/scale 动效）**。引擎只管外层窗口，GSAP 只管内层动效，互不打架。

### 坑 2：动效与字幕不同步（v6.1 结构修 + v6.3 内容根治 + v6.4 真实时间轴根治）
- 现象：动效出现/消失的时刻，和口播字幕对不上（"动效比字幕快很多"）。
- 根因三层：
  - **结构层**：旧版 scene 只靠 GSAP `tl` 单独跑，与引擎驱动字幕/视频的**主时钟不是同一套推进**——渲染跳帧/卡顿就错位。
  - **内容层（v6.3）**：即便结构同主时钟，若 beats 手填的 `s/e` 和真实说话区间估偏，动效仍会"快/慢几秒"。
  - **⚠️ 隐藏根因（v6.4 才彻底暴露，最致命）**：动效对齐的"时间轴"和你看的"字幕"根本不是一套！旧版从音频**静音检测**自动切的时间轴，系统性偏早 → 动效相对你的字幕整体抢跑；且默认还**偷偷叠了一层字幕**（`.cap`），屏幕上两排字幕、时间还不一样。
- ✅ v6.1 结构修复：scene 外层加 `.clip` + `data-start/duration`，**由引擎按窗口显隐，与字幕/视频共用同一主时钟**。字幕 `.cap` 同理：外层 `.clip`（引擎窗口）+ 内层 `.pill`（GSAP 淡入 + `tl.set` 硬 kill 防残留）。
- ✅ v6.4 内容根治（关键）：beat 改用 **`win:[t1,t2]` 直接写【真实说话秒数】**——优先用 faster-whisper 从 `_audio.wav` 提取真实说话时间轴（与剪映字幕同源），动效窗口 = 说话起+0.1s（略晚不抢跑）~ 说话止+0.35s（余韵）。彻底抛弃"静音检测时间轴"。（兼容旧 `cap` 绑 timeline.json / `s/e` 手填，但 v6.4 默认【推荐 win】。）
- ✅ v6.4 字幕层开关：`config.json` 的 `show_caption`（默认 true）控制是否叠加生成字幕层。**原片已自带字幕时务必设 `false`**，否则两排字幕时间打架。
- `gen_rich.py` 已内置此约束（`scene` 外层带 `.clip`、动效全在内层 `.sc-inner`、窗口由 `win` 派生），**勿手填 s/e 对齐静音检测轴、勿手改回"纯非 clip + 仅 GSAP"**。

### 坑 3 / v6.3 增强：不挡脸、不压字幕、动效≠字幕、表格对比、复合动效（已内置，按需用）
- **⚠️ 动效不是第二套字幕（v6.3 最重要原则）**：动效只做**关键词增强**——把口播里最该"亮出来"的词、数字、对比、简图、图标、表格，用视觉突出，**绝不把口播长句再打一遍**。例：口播说"大模型"，动效就放一张「主流大模型简图」同步出现；口播说"以前 3 小时现在 20 分"，动效就放一张对比表。动效是给字幕"加料"，不是复读。
- **① 绝不压口播字幕、绝不挡脸**：`.sc` 是带状容器（`top:3%; bottom:35%; overflow:hidden`）→ 富图层只在画面**上半部 ~62%** 活动，**底部 35% 留给字幕**；同时布局只用 `top/left/right/table`（左侧/右侧/顶部/整表），**物理避开面部中央 25%~45% 区**，绝不挡脸。大表格/大图统一放上半部 + `scrim` 压暗。`bottom` 不要小于 35%、不要用 `center`/`split` 布局（会压面部）。
- **② 数字对比用真表格**：`layout:"table"` 用 `.cmp-box > table.cmp`（表头 + 斑马纹 + `now` 绿高亮列 / `old` 红删除线列 + `ico` 图标列）。**凡是"以前 vs 现在 / 模块 vs 作用 / 维度对比"都优先上表格**，比一行大字更有信息量。见 `beats.example.json` 的 b9/b12/b13/b16/b17。
- **③ 复合动效（自动叠加，无需手写）**：`gen_rich.py` 扫 `html` 自动注入——
  - 含 `<... class="num" data-to="48">` → 该数字从 0 滚动到 48（`countTo`，与 autoAlpha 同步）；
  - 含 `<... class="ico">`（图标/序号）→ 所有图标做脉冲（`pulse`）；
  - 在 beat 的 `extra` 里写 `flashHi("#bX .hi", t)` → 高亮词缩放强调。
  配合每节拍的入场/退场/运镜，**一个 beat 同时跑 入场 + 数字滚动 + 图标脉冲 + 高亮强调**，就是"多种动效结合"。`extra` 还能写任意 GSAP（如 `tl.fromTo("#bX .cmp tr",{autoAlpha:0,x:-30},{...stagger},t)` 做逐行展开）。
- ⚠️ `beats.json` 的 `html` 属性**统一用单引号**（避免和 JSON 双引号冲突）；`extra` 里的 GSAP 选择器用双引号（JSON 里写成 `\"`）。

## 实测结论（已写入 Obsidian，作为真实性背书）
- 柱子哥成片 = **单一长镜头，零硬切 / 零转场 / 零 B-roll**（全片 16015 帧逐帧对比，变化量极差仅 29–42，无一处达到硬切阈值）。
- **字幕/叠加区在顶部**（98% 帧的顶部带变化最剧）→ 印证"顶部赛博字幕"。
- 音频近连续，无配乐留白 → 叠加层只加视觉，不动声音。

## Runtime（预装，固定路径）
都在 `C:/Users/ho'li/.workbuddy/hyperframes-edit-runtime/`：
- `ffmpeg/bin/ffmpeg.exe` + `ffprobe.exe`（BtbN 版）
- `hyperframes-install/` — `hyperframes` CLI（`node_modules/hyperframes/dist/cli.js`）
- `chrome-headless-shell/win64-*/chrome-headless-shell.exe`（渲染用 Chromium）

Node：`C:/Users/ho'li/.workbuddy/binaries/node/versions/22.22.2/node.exe`
GSAP：技能自带 `scripts/gsap.min.js`（生成时会自动拷到工程目录，离线安全）。

## 调用流程（Mode A 富图层导演版，默认）

对每支视频建一个工程目录（如 `./hf_project/`），把源片和稿子放进去，依次跑：

### Step 1 — 收齐输入
- 把口播录像复制为 `src.mp4`（**务必用纯 ASCII 文件名**，中文/含 `ho'li` 撇号的路径会让 ffmpeg 静默失败）。
- 把口播稿按"自然停顿"切成一句一行，存成 `script_segments.txt`（UTF-8）。
- 复制 `scripts/beats.example.json` 为 `beats.json`，按你的内容改 `beats[]`（每个 beat = 一个关键动效时刻：`win` 真实说话秒数、`layout` 布局、`html` 面板（关键词增强，不重复字幕）、`cam` 运镜、`scrim/extra` 可选）。**这是唯一需要动的内容文件**。
  - **`win:[t1,t2]` 必填（v6.4 推荐）**：直接写【真实说话秒数】。先用 faster-whisper 从 `_audio.wav` 提取（见 Step 4b）得到每句真实起止，再填；或退用 `cap`（绑 timeline.json 句索引）/ `s/e`（手填秒）。动效窗口 = `win[0]+0.1 ~ win[1]+0.35`，略晚不抢跑。
- （可选）`config.json`：建 `{"show_caption":false}` 关掉本工具字幕层（**原片已自带字幕时必须设**，否则两排字幕）；`badge_core`/`badge_label` 徽章、`color_*` 配色（参考 `config.example.json`）。

### Step 2 — 转码 + 抽音频（HEVC/高帧率必须）
```bash
FF="C:/Users/ho'li/.workbuddy/hyperframes-edit-runtime/ffmpeg/bin/ffmpeg.exe"
"$FF" -y -i src.mp4 -c:v libx264 -crf 18 -preset fast -pix_fmt yuv420p -r 30 -g 30 \
      -keyint_min 30 -movflags +faststart -c:a copy src_fixed.mp4
"$FF" -y -i src.mp4 -vn -ac 1 -ar 16000 _audio.wav
```

### Step 3 — 真实语音区间（silencedetect）
```bash
"$FF" -i _audio.wav -af silencedetect=noise=-26dB:d=0.12 -f null - 2>_silence.txt
```

### Step 4 — 生成字幕时间轴
```bash
python scripts/make_timeline.py _silence.txt script_segments.txt   # -> timeline.json
```
逻辑：按字符比例把每句铺到 [T0,T1]，再把内部边界**吸附到真实停顿中心**（±4s），强制最短可读 1.3s。

### Step 4b —（v6.4 推荐）whisper 提取真实说话时间轴（根治"动效抢跑"）
> ⚠️ v6.4 同步关键：上面 make_timeline 切出的"字幕时间轴"是**静音检测估算**，系统性偏早，不能直接用来对动效。要根治"动效抢跑"，用 faster-whisper 提取**真实说话时间**（与剪映字幕同源）：
```bash
VENV="$HOME/.workbuddy/binaries/python/envs/default"
"$VENV/Scripts/python.exe" - > timeline_whisper.json 2>&1 <<'PY'
from faster_whisper import WhisperModel
m = WhisperModel('small','cpu')
segs, info = m.transcribe('_audio.wav', language='zh', beam_size=5, vad_filter=True)
out=[{"i":i,"start":round(s.start,2),"end":round(s.end,2),"text":s.text.strip()} for i,s in enumerate(segs)]
import json; json.dump(out, open('timeline_whisper.json','w',encoding='utf-8'), ensure_ascii=False, indent=1)
print("SEG_COUNT:",len(out))
PY
```
然后用 `timeline_whisper.json` 里每句的 `start/end` 填 beats.json 的 **`win:[start,end]`**。这就是你剪映字幕的时间来源，动效跟它走、绝不抢跑。

### Step 5 — 生成叠层 HTML（Mode A 核心）
```bash
python scripts/gen_rich.py    # 读 timeline.json + beats.json + config.json + gsap.min.js -> index.html
```
产出包含：背景视频(`#cam` 包裹，支持运镜) + HUD 层 + 常驻角落旋转徽章 + 底部进度条 + 轻量字幕(`.cap`/`.clip` 外层窗口 + `.pill` 内层 GSAP 淡入) + **富图层(`.sc` 外层 `.clip` 引擎窗口显隐 + `.sc-inner` 内层 GSAP 动效，与字幕同主时钟→同步)** + 暗场 scrim。

### Step 6 — 渲染 + 音频兜底
```bash
bash scripts/render.sh    # 跑 hyperframes CLI 渲染，再兜底混回原声（双重兜底，见下）
```
渲染较慢（3 分钟片约 12–16 分钟），建议后台跑。

### Step 7 — 交付前验证
```bash
# 必须同时有 video(h264) + audio(aac)
<runtime>/ffmpeg/bin/ffprobe.exe -v error -show_entries stream=codec_type -of default=noprint_wrappers=1 out.mp4
# 抽几帧确认富图层在关键节拍出现、未遮挡原画面
<runtime>/ffmpeg/bin/ffmpeg.exe -y -ss 7 -i out.mp4 -frames:v 1 _v.png
```

## 渲染失败的双重兜底（render.sh 已内建）
1. **Faststart/assemble 失败但帧已编码** → 自动从 `work-*/video-only.mp4` 混回 `src_fixed.mp4` 原声并做 faststart，无需重渲（v6 定稿这版就靠它救回成片）。
2. **out.mp4 仍缺音轨** → 从 `src_fixed.mp4` 兜底混回原声。
> 交付前**必查 `aac` 流存在**，否则成片无声。

## 富图层内容怎么写（beats.json，不用手碰代码）
`beats.example.json` 是完整范例（通用口播结构，v6.4）。**每个 beat 关键字段**：
- `win`（**v6.4 必填推荐**）：`[t1,t2]` 直接写【真实说话秒数】。如 `[8.3,11.0]` 表示第 8.3~11.0 秒说话。动效窗口 = `t1+0.1`（略晚不抢跑）~ `t2+0.35`（余韵）。优先用 Step 4b 的 whisper 提取秒数填。
- `cap`（兼容旧）：绑 `timeline.json` 句索引（整数 / `[a,b]` 跨句）。仅当没有真实说话秒数时退用。
- `s`/`e`（兼容旧）：手填秒数。最不推荐（易估偏）。
- **内容铁律**：`html` 只写"关键词增强"——kicker 标签 + 简图/图标/表格/大数字，**不要照抄口播长句**。动效是给字幕加料突出，不是第二套字幕。
- 支持的面板 class：
- `kicker`（顶部标签条，如"突发·美股闪崩"）
- `bigstat` + `sub` + `dbar`（巨型数字 + 副标题 + 进度条，如 `-20%`）
- `card-h/card-t/card-d`（左右卡片：标题/主词/副描述）
- `t-title` + `row`（规格表，如参数规模/排名/成本）
- `shout` / `shout.sm` / `.hi` / `.warm`（金句，绿色/琥珀色高亮）
- `quote` + `qm`（引言卡）
- `split-wrap` + `sp.old/sp.new` 或 `sp.node/sp.node.now`（分屏：旧逻辑被击穿 / 时间线锚点）
- `pip` + `side.open/closed` + `vs`（画中画：开源 vs 闭源对决窗）
- `cta-btn` + `id-badge`（结尾引导关注）
- `layout`：`top` / `left` / `right` / `table`（**只用这四个**，避开面部中央与底部字幕区；`table` 用于整张对比表放上半部）。**不要用 `center`/`split`**（会压面部）。
- `cam`：`{scale}` 运镜（v6.3 改为"关键词出现时一次性推近强调再回稳"，如 `scale:1.08`，**不要设过大 scale 持续放大挡脸**）；`scrim:true` 压暗背景突出内容；`extra` 额外 GSAP 语句（时间用绝对秒，可选）

## Hero 图片徽章（视觉爆点，按需）
`config.json` 的 `hero_map`：`{"段号":["icon.png","标签"]}`。图片用 ImageGen 生成（透明背景、霓虹主体、约 1024²），放进工程 `assets/`。展示为圆形裁切（顺手裁掉 AI 生成水印）+ 旋转虚线环 + 发光标签。

## 不碰原画面的保证
所有特效都是 HTML 叠层（`index.html` 里的 `.hud` / `.cap` / `.sc` / 角落徽章），背景 `<video>` 原样播放，渲染时仅合成像素，绝不重编码或裁剪你的录像内容。

## 常见坑（v6 已规避/标注）
- **HEVC 源** → 黑屏，Step 2 必须先转 H.264。
- **中文/撇号路径** → 源片改名 `src.mp4`（ASCII）再进管线。
- **富图层不显示** → 多半是把 GSAP 动效写到了**外层 `.clip`** 上（被引擎每帧重置压制，见上方⚠️坑1）。`gen_rich.py` 已规避（动效全在内层 `.sc-inner`），勿手改外层。
- **动效与字幕不同步（v6.4 已根治）** → 根因是动效对齐的时间轴和你的字幕不是一套（旧静音检测轴偏早 + 偷偷叠字幕层）。v6.4 用 `win:[t1,t2]` 直接写【真实说话秒数】（whisper 提取，与剪映同源），动效 = 说话起+0.1s ~ 说话止+0.35s，绝不抢跑；且 `config.json` 设 `show_caption:false` 关掉叠字幕层。若仍偏早：说明你原片字幕显示得比真实说话晚（手动打字的剪辑习惯），告诉我"还快几秒"，把全 beat 的 `win` 整体后移即可。
- **GSAP CDN 需联网** → 技能已自带 `gsap.min.js` 并自动拷到工程目录；离线也能用。
- **silence_start / silence_end 分行** → `make_timeline.py` 已按序配对，勿手动改。
- **"跟着说话节奏"的精度** → v6 字幕用"句长/句时长"推算（稳健）；若要逐字级精确，可接 ASR 词级时间戳驱动（进阶，未默认启用）。
- **渲染卡在 Faststart** → 预期内，`render.sh` 已双层兜底（video-only 恢复 + 音频混回）。
