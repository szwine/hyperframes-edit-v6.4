# 🎬 hyperframes.edit v6.4 — 富图层·动效剪辑版（v2 修正说明）

> 老李出品 · 竖屏口播视频「一键加料」神器
> 给普通口播视频加上：顶部字幕 + 旋转徽章 + 数据卡片 + 对比表格 + 动效，成片像专业剪辑师做的。
>
> ✅ 本版修复了初版「粉丝严格照做就卡死」的三个坑：
> ① 漏了生成 `_silence.txt` 的命令（直接 FileNotFoundError 崩）；
> ② 用裸 `ffmpeg` 但运行时没进系统 PATH；
> ③ 让 Windows 用户跑 `bash render.sh`，而默认终端没有 bash。
> 现在**全程双击 `.bat` 即可，无需 Git Bash、无需配 PATH**。

---

## 这是啥（30 秒看懂）

你拍了一段竖屏口播视频（手机对着自己说话那种），这个工具给它**叠一层"皮"**：

- ✅ 顶部赛博字幕（卡拉OK式逐句高亮）
- ✅ 角落旋转徽章（品牌感）
- ✅ 关键语句加料（大数字、对比表格、图标、金句卡）
- ✅ 全程不挡脸、不改原画面、只加视觉

**原视频一点不动，效果全是"贴"上去的。**

---

## 电脑要求

- **Windows 10/11**（不支持 Mac，抱歉）
- 有 Python 3.9+（没有的话安装脚本会提示你装）
- 硬盘剩 2GB 以上（装依赖约 1.2GB）
- 网络能访问 GitHub / 微软 / 谷歌 CDN（下载依赖用）

---

## 安装（只需 3 步）

### 第 1 步：下载并解压

点右上角绿色 **Code** 按钮 → **Download ZIP**
解压到一个好找的地方（比如桌面），得到 `hyperframes-edit-v6.4` 文件夹。

### 第 2 步：双击安装

进入文件夹，**双击 `install.bat`**，黑窗口会自动跑：

- 自动下载 FFmpeg（视频引擎）
- 自动下载 Node.js（渲染环境）
- 自动下载 Chrome 无头浏览器（渲染用）
- 自动下载 hyperframes 渲染引擎（装不上会在结尾提示，见下方"装完没装全"）

> ⏳ 全程约 5-15 分钟，取决于网速。**中途别关窗口。**
> 如果哪一步失败，重跑一次 install.bat 即可（已装好的不会重复下载）。

### 第 3 步：验证

安装完看到「✅ 安装完成」就是成功。
> ⚠️ 如果第⑥步 hyperframes 没装上，会显示 WARN 而不是致命错误——请回看黑窗口有没有
> `WARN] hyperframes 未自动安装完成` 字样；有的话自行进 `hyperframes-install` 目录跑 `npm install` 再继续。

---

## 怎么用（每个视频 4 步，全程双击 .bat）

**最简单的做法：直接在本仓库 `hyperframes-edit-v6.4` 文件夹里操作**——
把你的口播视频改名 `src.mp4` 丢进这个文件夹，下面的文件也放这里，然后双击两个 bat 即可。
（进阶：也可以把 `scripts/` 文件夹、`prep.bat`、`render.bat` 一起复制到你的视频文件夹里再双击。）

### ① 准备输入

| 文件 | 怎么来 |
|------|--------|
| `src.mp4` | 你的口播原视频（改名为 src.mp4，**不要用中文名**） |
| `script_segments.txt` | 口播稿，一句一行（UTF-8 编码，记事本"另存为"选 UTF-8） |

### ② 写动效配置

复制 `scripts/beats.example.json` 为 `beats.json`，
打开它，把里面的**文字**换成你自己的内容（每段 = 一个动效时刻）。

> ⚠️ **关键：必须同时改 `win:[t1,t2]` 的真实说话秒数！**
> 范例里的时间是示例视频的（2.1s、8.3s…），**不是你的**。
> 两个办法拿到你自己的时间：
> - **偷懒法**：用剪映/手机看着视频，记下每句重点说话的"开始秒数~结束秒数"，填进 win。
> - **准法**：装 faster-whisper（`pip install faster-whisper`）从 `_audio.wav` 提取真实说话时间轴，
>   把每句 start/end 填进对应 beat 的 win。动效 = win[0]+0.1s 出现、win[1]+0.35s 消失，绝不与字幕抢跑。
> 若不改 win，动效会固定落在示例时间，和你的口播对不上。

### ③ 双击 `prep.bat`（预处理）

自动完成：转码 H.264 → 抽音频 → 静音检测生成 `_silence.txt` → 生成字幕时间轴 `timeline.json` → 生成叠层 `index.html`。
看到「✅ 预处理完成」即可。若没自动生成 `beats.json` 会先用范例（记得回去改 win 时间）。

### ④ 双击 `render.bat`（渲染成片）

读取 `index.html`，调用 Chrome 无头浏览器渲染，自动音频兜底，输出 `out.mp4`。
> ⏳ 3 分钟的视频大约渲染 12-16 分钟，期间别关窗口。完成后看 `out.mp4` 即可。

> 💡 高级用户仍可用 Git Bash 跑 `bash scripts/render.sh`（功能相同），但普通 Windows 用户直接双击 `render.bat` 即可。

---

## 文件说明

```
hyperframes-edit-v6.4/
├── install.bat              ← 一键安装（先双击这个）
├── prep.bat                 ← ✅ 预处理（转码+时间轴+生成叠层），双击即用
├── render.bat               ← ✅ 渲染成片（cmd 版，双击即用，无需 Git Bash）
├── SKILL.md                 ← 给 AI 看的完整说明书（技术细节）
├── scripts/
│   ├── gen_rich.py          ← 富图层导演版生成器（默认，效果最全）
│   ├── build_html.py        ← 轻量字幕皮（只要干净字幕用这个）
│   ├── make_timeline.py     ← 静音检测→字幕时间轴
│   ├── render.sh            ← 渲染（Git Bash 版，可选）
│   ├── beats.example.json   ← 动效配置范例（复制去改，记得改 win 时间）
│   ├── config.example.json   ← 全局配置范例（见下方"配置怎么改"）
│   └── gsap.min.js          ← 动效库（离线自带）
├── assets/                  ← 徽章/图标素材
└── references/              ← 设计文档
```

---

## 配置怎么改（config.json）

在工程目录建 `config.json`（JSON 格式），**gen_rich.py 实际只认这些顶层键**：

```json
{
  "show_caption": true,        // 是否叠加本工具生成的字幕层。⚠️ 原片已自带字幕时必须设 false，否则两排字幕
  "badge_core": "⚡",          // 角落徽章中心的图标/字
  "badge_label": "AI口播",     // 徽章下方文字
  "color_primary": "#00f0ff",  // 主色（青）
  "color_magenta": "#ff4dff",
  "color_green": "#39ff14",
  "color_amber": "#ffcc00",
  "color_ink": "#ff2a6d"
}
```

> ⚠️ 仓库里的 `config.example.json` 已修正为上面的格式。早期版本用了 `colors.primary`、
> `corner_badge.label` 等嵌套键，但 `gen_rich.py` 读的是顶层键，照着旧写法改颜色/徽章不会生效。

---

## 常见问题

**Q: 装到一半失败了？**
A: 网络问题。重跑 install.bat，已下载的不会重复下。

**Q: prep.bat 报"找不到 ffmpeg / 找不到 python"？**
A: 没先装依赖。请先双击 install.bat 装好（python 去微软商店装 3.9+）。

**Q: 渲染出来没声音？**
A: render.bat 会自动兜底混回原声。如果还不行，检查 src.mp4 是否有音轨。

**Q: 视频黑屏？**
A: 源视频是 HEVC 格式，prep.bat 第①步已自动转码 H.264，重跑一次 prep.bat 即可。

**Q: 动效比字幕快 / 对不上？**
A: beats.json 里的 win 时间没改成你自己的。用剪映或 whisper 拿到真实说话秒数重填 win；若仍偏早，把全部 win 整体后移 1-2 秒。

**Q: 我想用剪映怎么办？**
A: 这个工具和剪映不冲突。剪映剪辑，本工具加料，最后导出就行。

---

## 免责声明

本工具只做视觉叠加，不改原画面。请遵守平台规则，健康内容不诊断、不荐药、不承诺疗效。

## License

Apache 2.0
