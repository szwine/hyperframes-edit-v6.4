# 🎬 hyperframes.edit v6.4 — 富图层·动效剪辑版

> 老李出品 · 竖屏口播视频「一键加料」神器
> 给普通口播视频加上：顶部字幕 + 旋转徽章 + 数据卡片 + 对比表格 + 动效，成片像专业剪辑师做的。

---

## 这是啥（30 秒看懂）

你拍了一段竖屏口播视频（手机对着自己说话那种），
这个工具给它**叠一层"皮"**：

- ✅ 顶部赛博字幕（卡拉OK式逐句高亮）
- ✅ 角落旋转徽章（品牌感）
- ✅ 关键语句加料（大数字、对比表格、图标、金句卡）
- ✅ 全程不挡脸、不改原画面、只加视觉

**原视频一点不动，效果全是"贴"上去的。**

---

## 电脑要求

- **Windows 10/11**（不支持 Mac，抱歉）
- 有 Python 3.9+（没有的话安装脚本会帮你装）
- 硬盘剩 2GB 以上（装依赖约 1.2GB）
- 网络能访问 GitHub / 微软 CDN（下载依赖用）

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
- 自动下载 hyperframes 渲染引擎

> ⏳ 全程约 5-15 分钟，取决于网速。**中途别关窗口。**
> 如果哪一步失败，重跑一次 install.bat 即可（已装好的不会重复下载）。

### 第 3 步：验证

安装完看到「✅ 安装完成」就是成功。

---

## 怎么用（每个视频 4 步）

在桌面新建一个文件夹（如 `myvideo/`），把要加工的视频放进去：

### ① 准备输入
| 文件 | 怎么来 |
|------|--------|
| `src.mp4` | 你的口播原视频（改名为 src.mp4，**不要用中文名**） |
| `script_segments.txt` | 口播稿，一句一行（UTF-8 编码） |

### ② 写动效配置
复制 `scripts/beats.example.json` 为 `beats.json`，
打开它，把里面的文字换成你自己的内容（每段 = 一个动效时刻）。

### ③ 跑三行命令（在 myvideo 文件夹里打开终端）

```bash
# 转码 + 抽音频
ffmpeg -i src.mp4 -c:v libx264 -crf 18 -preset fast -pix_fmt yuv420p -r 30 src_fixed.mp4
ffmpeg -i src.mp4 -vn -ac 1 -ar 16000 _audio.wav

# 生成时间轴
python scripts/make_timeline.py _silence.txt script_segments.txt
```

### ④ 生成 + 渲染

```bash
python scripts/gen_rich.py
bash scripts/render.sh    # 输出 out.mp4
```

> ⏳ 3 分钟的视频大约渲染 12-16 分钟，可以后台跑。

---

## 文件说明

```
hyperframes-edit-v6.4/
├── install.bat              ← 一键安装（先双击这个）
├── SKILL.md                 ← 给 AI 看的完整说明书（技术细节）
├── scripts/
│   ├── gen_rich.py          ← 富图层导演版生成器（默认，效果最全）
│   ├── build_html.py        ← 轻量字幕皮（只要干净字幕用这个）
│   ├── make_timeline.py     ← 静音检测→字幕时间轴
│   ├── render.sh            ← 渲染 + 音频兜底
│   ├── beats.example.json   ← 动效配置范例（复制去改）
│   ├── config.example.json  ← 全局配置范例
│   └── gsap.min.js          ← 动效库（离线自带）
├── assets/                  ← 徽章/图标素材
└── references/              ← 设计文档
```

---

## 常见问题

**Q: 装到一半失败了？**
A: 网络问题。重跑 install.bat，已下载的不会重复下。

**Q: 渲染出来没声音？**
A: render.sh 会自动兜底混回原声。如果还不行，检查 src.mp4 是否有音轨。

**Q: 视频黑屏？**
A: 源视频是 HEVC 格式，先转码 H.264（第③步已包含）。

**Q: 动效比字幕快？**
A: 说明原片字幕显示比说话晚。把所有 beats.json 里的 win 时间整体往后挪 1-2 秒。

**Q: 我想用剪映怎么办？**
A: 这个工具和剪映不冲突。剪映剪辑，本工具加料，最后导出就行。

---

## 免责声明

本工具只做视觉叠加，不改原画面。请遵守平台规则，健康内容不诊断、不荐药、不承诺疗效。

## License

Apache 2.0
