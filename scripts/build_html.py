#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
hyperframes-edit v5 — 生成 index.html 叠层（柱子哥实测精修版）
输入：timeline.json  (make_timeline.py 产出，已按真实停顿对齐)
      config.json    (可选；每支视频的样式/徽章/hero 配置，缺省用 DEFAULTS)
      assets/*.png   (hero 图标，按需用 ImageGen 生成)
输出：index.html
依赖：src_fixed.mp4 在 cwd（作为背景视频，绝不修改原画面）

v5 相对 v4 的提升（对照柱子哥真实成片实测）：
  ★ 顶部"跳动"字幕：逐字 karaoke 弹出，节奏 = 该句说话速率（字数/时长），真正"跟着说话走"
  ★ 图标按关键词语义自动分配（不再写死段号列表，任意稿子通用）
  ★ 常驻"角落旋转徽章"：整片在角落持续旋转（CSS 驱动，稳定可被录屏捕获）
  ★ HUD 更细致：底部进度条 + 扫描线扫掠 + 点阵脉冲 + 四角框 + 暗角
  ★ 不碰原画面：纯 HTML 叠加层，背景视频原样保留
"""
import json
import os
import shutil
import subprocess
from html import escape

# ---------- 内联 SVG 图标库（霓虹三色 + 发光） ----------
SVG_HEAD = ('style="width:0.95em;height:0.95em;vertical-align:middle;margin-right:0.28em;'
            'fill:none;stroke-width:2.4;stroke-linecap:round;stroke-linejoin:round;')
icons = {
    "spark":    f'<svg viewBox="0 0 24 24" {SVG_HEAD.replace("fill:none","fill:none")}stroke:#00f0ff;filter:drop-shadow(0 0 4px #00f0ff)"><path d="M12 2L15 9L22 12L15 15L12 22L9 15L2 12L9 9L12 2Z"/></svg>',
    "bolt":     f'<svg viewBox="0 0 24 24" style="width:0.95em;height:0.95em;vertical-align:middle;margin-right:0.28em;fill:#ffe600;stroke:#ffe600;stroke-width:0;filter:drop-shadow(0 0 4px #ffe600)"><path d="M13 2L3 14H12L11 22L21 10H12L13 2Z"/></svg>',
    "question": f'<svg viewBox="0 0 24 24" style="width:0.95em;height:0.95em;vertical-align:middle;margin-right:0.28em;fill:none;stroke:#ff4dff;stroke-width:2.2;stroke-linecap:round;stroke-linejoin:round;filter:drop-shadow(0 0 4px #ff4dff)"><circle cx="12" cy="12" r="10"/><path d="M9.5 9.5C9.5 8.1 10.8 7 12.2 7C13.9 7 15 8.2 15 9.8C15 11.5 13.5 12 12.5 13.5V15M12.5 17.5V18" stroke-linecap="round"/></svg>',
    "arrow":    f'<svg viewBox="0 0 24 24" style="width:0.95em;height:0.95em;vertical-align:middle;margin-right:0.28em;fill:none;stroke:#39ff14;stroke-width:2.5;stroke-linecap:round;stroke-linejoin:round;filter:drop-shadow(0 0 4px #39ff14)"><path d="M5 12H19M19 12L13 6M19 12L13 18"/></svg>',
    "heart":    f'<svg viewBox="0 0 24 24" style="width:0.95em;height:0.95em;vertical-align:middle;margin-right:0.28em;fill:#ff2a6d;stroke:#ff2a6d;stroke-width:0;filter:drop-shadow(0 0 4px #ff2a6d)"><path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/></svg>',
    "robot":    f'<svg viewBox="0 0 24 24" style="width:0.95em;height:0.95em;vertical-align:middle;margin-right:0.28em;fill:none;stroke:#00f0ff;stroke-width:2.2;stroke-linecap:round;stroke-linejoin:round;filter:drop-shadow(0 0 4px #00f0ff)"><rect x="4" y="8" width="16" height="11" rx="3"/><path d="M12 8V4M9 4h6"/><circle cx="9.5" cy="13" r="1.3" fill="#00f0ff" stroke="none"/><circle cx="14.5" cy="13" r="1.3" fill="#00f0ff" stroke="none"/></svg>',
    "health":   f'<svg viewBox="0 0 24 24" style="width:0.95em;height:0.95em;vertical-align:middle;margin-right:0.28em;fill:none;stroke:#ff4dff;stroke-width:2.2;stroke-linecap:round;stroke-linejoin:round;filter:drop-shadow(0 0 4px #ff4dff)"><path d="M2 12h4l2-6 4 12 2-6h8"/></svg>',
    "exo":      f'<svg viewBox="0 0 24 24" style="width:0.95em;height:0.95em;vertical-align:middle;margin-right:0.28em;fill:none;stroke:#39ff14;stroke-width:2.2;stroke-linecap:round;stroke-linejoin:round;filter:drop-shadow(0 0 4px #39ff14)"><circle cx="12" cy="5" r="2.2"/><path d="M12 7v6m0 0l-4 6m4-6l4 6M7 11h10"/></svg>',
    "number1":  f'<svg viewBox="0 0 24 24" style="width:0.95em;height:0.95em;vertical-align:middle;margin-right:0.28em;fill:none;stroke:#00f0ff;stroke-width:2.2;filter:drop-shadow(0 0 4px #00f0ff)"><circle cx="12" cy="12" r="10"/><path d="M11 8.5V17M11 8.5L13 6.5M11 8.5L9 6.5"/></svg>',
    "number2":  f'<svg viewBox="0 0 24 24" style="width:0.95em;height:0.95em;vertical-align:middle;margin-right:0.28em;fill:none;stroke:#00f0ff;stroke-width:2.2;filter:drop-shadow(0 0 4px #00f0ff)"><circle cx="12" cy="12" r="10"/><path d="M9 8.5C9 8.5 11 6.5 13 7.5C15 8.5 15 11 13 12L9 17H15"/></svg>',
    "number3":  f'<svg viewBox="0 0 24 24" style="width:0.95em;height:0.95em;vertical-align:middle;margin-right:0.28em;fill:none;stroke:#00f0ff;stroke-width:2.2;filter:drop-shadow(0 0 4px #00f0ff)"><circle cx="12" cy="12" r="10"/><path d="M9 8H14M14 8C15 8 16 9 16 10C16 11.2 15 12 14 12M14 12H10M14 12C15 12 16 13 16 14C16 15.5 15 16 14 16H9"/></svg>',
    "lightbulb":f'<svg viewBox="0 0 24 24" style="width:0.95em;height:0.95em;vertical-align:middle;margin-right:0.28em;fill:none;stroke:#ffcc00;stroke-width:2.2;stroke-linecap:round;stroke-linejoin:round;filter:drop-shadow(0 0 4px #ffcc00)"><path d="M9 18h6M10 22h4"/><path d="M12 2a6 6 0 0 0-6 6c0 2.22 1.21 4.15 3 5.19V15a1 1 0 0 0 1 1h4a1 1 0 0 0 1-1v-1.81c1.79-1.04 3-2.97 3-5.19a6 6 0 0 0-6-6Z"/></svg>',
    "share":    f'<svg viewBox="0 0 24 24" style="width:0.95em;height:0.95em;vertical-align:middle;margin-right:0.28em;fill:none;stroke:#39ff14;stroke-width:2.2;stroke-linecap:round;stroke-linejoin:round;filter:drop-shadow(0 0 4px #39ff14)"><circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><path d="M8.5 10.7L15.5 6.3M8.5 13.3L15.5 17.7"/></svg>',
    "chat":     f'<svg viewBox="0 0 24 24" style="width:0.95em;height:0.95em;vertical-align:middle;margin-right:0.28em;fill:none;stroke:#ff4dff;stroke-width:2.2;stroke-linecap:round;stroke-linejoin:round;filter:drop-shadow(0 0 4px #ff4dff)"><path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7A8.38 8.38 0 0 1 4 11.5a8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9H13a8.5 8.5 0 0 1 8 8v.5z"/></svg>',
    "user":     f'<svg viewBox="0 0 24 24" style="width:0.95em;height:0.95em;vertical-align:middle;margin-right:0.28em;fill:none;stroke:#00f0ff;stroke-width:2.2;stroke-linecap:round;stroke-linejoin:round;filter:drop-shadow(0 0 4px #00f0ff)"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>',
    "flag":     f'<svg viewBox="0 0 24 24" style="width:0.95em;height:0.95em;vertical-align:middle;margin-right:0.28em;fill:none;stroke:#00f0ff;stroke-width:2.2;stroke-linecap:round;stroke-linejoin:round;filter:drop-shadow(0 0 4px #00f0ff)"><path d="M4 15s1.5-2 5-2 5 2 8 2 4-1 4-1V3s-1.5 1-5 1-5-2-8-2-4 1-4 1z"/><path d="M4 22V2"/></svg>',
}

# ---------- 默认配置（可被 cwd 下的 config.json 覆盖） ----------
DEFAULTS = {
    "resolution": [1080, 1920],
    "caption_top": "9%",          # 柱子哥实测：字幕更靠上更醒目（v4 是 7%）
    "colors": {
        "primary": "#00f0ff", "magenta": "#ff4dff", "green": "#39ff14",
        "amber": "#ffcc00", "text": "#ffffff"
    },
    "corner_badge": {             # 常驻角落旋转徽章
        "enabled": True, "corner": "tr", "glyph": "bolt",
        "label": "AI口播", "spin_sec": 7
    },
    "hud": {"sweep": True, "progress": True, "dots": True, "scanlines": True,
            "corners": True, "vignette": True},
    "karaoke": True,              # 逐字跳动
    "hero_map": {}                # {段号: ["icon.png", "标签"]}；留空则无 hero 徽章
}


def load_config():
    cfg = json.loads(json.dumps(DEFAULTS))  # deep copy
    if os.path.exists("config.json"):
        try:
            user = json.load(open("config.json", encoding="utf-8"))
            cfg.update({k: (user[k] if k in user else cfg[k]) for k in cfg})
            for k in ("colors", "corner_badge", "hud"):
                if k in user and isinstance(user[k], dict):
                    cfg[k].update(user[k])
            if "hero_map" in user:
                cfg["hero_map"] = user["hero_map"]
        except Exception as e:
            print("config.json 解析失败，用默认配置:", e)
    return cfg


# ---------- 关键词 → 图标（任意稿子通用） ----------
def keyword_icon(text: str) -> str:
    t = text.lower()
    if any(w in text for w in ["?","？","为什么","怎么","如何","吗","是不是","能否"]):
        return "question"
    if any(w in t for w in ["ai","人工智能","智能","大模型","模型","gpt","算法"]):
        return "spark"
    if any(w in text for w in ["第一","首先","其一","步骤一","1、","①"]): return "number1"
    if any(w in text for w in ["第二","其次","其二","步骤二","2、","②"]): return "number2"
    if any(w in text for w in ["第三","最后","其三","步骤三","2、","③","总结"]): return "number3"
    if any(w in text for w in ["!","！","重要","必须","一定","千万","切记","警惕","危险"]):
        return "bolt"
    if any(w in text for w in ["机器人","陪伴","数字人","助理"]): return "robot"
    if any(w in text for w in ["健康","身体","医疗","病","养生","医院"]): return "health"
    if any(w in text for w in ["外骨骼","助行","假肢","康复","义肢"]): return "exo"
    if any(w in text for w in ["分享","转发","点赞","关注","收藏","推荐"]): return "share"
    if any(w in text for w in ["例子","比如","例如","像","比如说"]): return "arrow"
    if any(w in text for w in ["心","爱","喜欢","感动","温暖","陪伴","在乎"]): return "heart"
    if any(w in text for w in ["说","讲","聊","对话","沟通","告诉","问"]): return "chat"
    if any(w in text for w in ["人","用户","你","我们","大家","朋友"]): return "user"
    if any(w in text for w in ["目标","计划","方向","flag","蓝图","愿景"]): return "flag"
    if any(w in text for w in ["想法","灵感","点子","思考","认为","觉得","以为"]): return "lightbulb"
    return "spark"


def size_class(text: str) -> str:
    n = len(text)
    if n <= 12: return "big"
    if n <= 22: return "mid"
    return "small"


def char_spans(text: str) -> str:
    out = []
    for ch in text:
        if ch.strip() == "":
            out.append(escape(ch))
        else:
            out.append(f'<span class="ch">{escape(ch)}</span>')
    return "".join(out)


def get_duration(default=186.97):
    # 1) PATH 上的 ffprobe
    ff = shutil.which("ffprobe")
    # 2) render.sh 注入的环境变量
    if not ff:
        p = os.environ.get("HYPERFRAMES_FFMPEG_PATH", "")
        if p: ff = p.replace("ffmpeg.exe", "ffprobe.exe")
    # 3) 已知 runtime 绝对路径（Windows 上 shell 解析失败，但 Python subprocess 直接传字符串可用）
    #    粉丝分发版：优先用 HF_RUNTIME 环境变量（install.bat 设置）
    if not ff or not os.path.exists(ff):
        rt = os.environ.get("HF_RUNTIME", os.path.join(os.path.expanduser("~"), ".workbuddy", "hyperframes-edit-runtime"))
        for cand in (
            os.path.join(rt, "ffmpeg", "bin", "ffprobe.exe"),
            os.path.join(rt, "ffmpeg", "bin", "ffprobe"),
        ):
            if os.path.exists(cand):
                ff = cand
                break
    if ff and os.path.exists(ff) and os.path.exists("src_fixed.mp4"):
        try:
            out = subprocess.check_output(
                [ff, "-v", "error", "-show_entries", "format=duration",
                 "-of", "default=noprint_wrappers=1:nokey=1", "src_fixed.mp4"]
            ).decode().strip()
            return float(out)
        except Exception:
            pass
    # 4) 终极兜底：时间轴尾点（内容真实时长）
    try:
        tl = json.load(open("timeline.json", encoding="utf-8"))
        if tl:
            return float(tl[-1]["end"])
    except Exception:
        pass
    return default


def build():
    cfg = load_config()
    timeline = json.load(open("timeline.json", encoding="utf-8"))
    W, H = cfg["resolution"]
    DUR = round(get_duration(), 2)
    C = cfg["colors"]
    cb = cfg["corner_badge"]
    hud = cfg["hud"]
    hero_map = {int(k): v for k, v in cfg.get("hero_map", {}).items()}

    # ---------- CSS（占位符后替换，避免 f-string 大括号冲突） ----------
    css = """
    * { box-sizing: border-box; }
    html, body { margin:0; padding:0; width:100%; height:100%; background:#000; overflow:hidden; }
    @font-face { font-family:'Microsoft YaHei'; src: local('Microsoft YaHei'); }

    #stage{ position:relative; width:__W__px; height:__H__px; overflow:hidden; background:#000; margin:0 auto;
      --primary:__PRI__; --magenta:__MAG__; --green:__GRN__; --amber:__AMB__; --text:__TXT__; }
    #clip{ position:absolute; top:0; left:0; width:100%; height:100%; object-fit:cover; display:block; }

    /* HUD 科技底纹 */
    .hud{ position:absolute; top:0; left:0; width:100%; height:100%; pointer-events:none; z-index:5;
      background: radial-gradient(circle at 50% 0%, rgba(0,240,255,0.08), transparent 55%); }
    .hud-corners{ position:absolute; inset:24px; border:1px solid rgba(0,240,255,0.22); }
    .corner{ position:absolute; width:80px; height:80px; }
    .corner.tl{ top:0; left:0; border-top:4px solid var(--primary); border-left:4px solid var(--primary); border-top-left-radius:14px; }
    .corner.tr{ top:0; right:0; border-top:4px solid var(--primary); border-right:4px solid var(--primary); border-top-right-radius:14px; }
    .corner.bl{ bottom:0; left:0; border-bottom:4px solid var(--primary); border-left:4px solid var(--primary); border-bottom-left-radius:14px; }
    .corner.br{ bottom:0; right:0; border-bottom:4px solid var(--primary); border-right:4px solid var(--primary); border-bottom-right-radius:14px; }
    .scanlines{ position:absolute; top:0; left:0; width:100%; height:100%;
      background: repeating-linear-gradient(180deg, rgba(0,240,255,0.03) 0, rgba(0,240,255,0.03) 2px, transparent 2px, transparent 8px);
      mix-blend-mode: overlay; }
    .dotgrid{ position:absolute; top:0; left:0; width:100%; height:100%;
      background-image: radial-gradient(rgba(0,240,255,0.12) 1px, transparent 1px);
      background-size: 34px 34px; opacity:0.3; animation: dotpulse 3.2s ease-in-out infinite; }
    @keyframes dotpulse { 0%,100%{opacity:0.22} 50%{opacity:0.4} }
    .hud-vignette{ position:absolute; inset:0; box-shadow: inset 0 0 180px 60px rgba(0,0,0,0.35); }

    /* 扫描线扫掠 */
    .sweep{ position:absolute; left:0; width:100%; height:3px; top:0;
      background:linear-gradient(90deg, transparent, var(--primary), transparent);
      opacity:0.45; box-shadow:0 0 12px var(--primary); animation: sweepmove __SWEEP__s linear infinite; }
    @keyframes sweepmove { 0%{ top:2% } 100%{ top:98% } }

    /* 底部进度条 */
    .progress{ position:absolute; left:0; bottom:0; height:6px; width:100%; background:rgba(255,255,255,0.07); z-index:8; }
    .progress > i{ display:block; height:100%; width:100%; transform-origin:left center; transform:scaleX(0);
      background:linear-gradient(90deg, var(--primary), var(--magenta)); box-shadow:0 0 10px var(--primary);
      animation: prog __DUR__s linear forwards; }
    @keyframes prog { to { transform:scaleX(1); } }

    /* 常驻角落旋转徽章 */
    .corner-badge{ position:absolute; width:150px; height:150px; z-index:9; }
    .corner-badge.tr{ top:46px; right:46px; }
    .corner-badge.tl{ top:46px; left:46px; }
    .corner-badge.bl{ bottom:46px; left:46px; }
    .corner-badge.br{ bottom:46px; right:46px; }
    .cb-ring{ position:absolute; inset:0; border-radius:50%; border:3px dashed var(--primary);
      box-shadow:0 0 22px var(--primary); animation: cbspin __SPIN__s linear infinite; }
    .cb-ring2{ position:absolute; inset:14px; border-radius:50%; border:2px solid rgba(0,240,255,0.35); }
    .cb-core{ position:absolute; inset:30px; border-radius:50%; background:rgba(0,10,30,0.6);
      border:2px solid var(--primary); display:flex; align-items:center; justify-content:center;
      color:var(--primary); font-size:34px; font-weight:800; text-shadow:0 0 12px var(--primary); }
    .cb-label{ position:absolute; bottom:-26px; left:0; right:0; text-align:center;
      color:var(--primary); font-size:22px; letter-spacing:0.2em; text-shadow:0 0 10px var(--primary); }
    @keyframes cbspin { to { transform: rotate(360deg); } }

    /* 字幕层（顶部安全区，跟随配置 caption_top） */
    .cap{ position:absolute; top:__TOP__; left:0; right:0; display:flex; flex-direction:column;
      align-items:center; justify-content:flex-start; max-width:calc(100% - 80px); margin:0 auto;
      padding:0 20px; pointer-events:none; z-index:10; }
    .cap-content{ text-align:center; color:var(--text); text-shadow:0 2px 16px rgba(0,0,0,0.6);
      font-family:'Microsoft YaHei', sans-serif; font-weight:800; line-height:1.25;
      word-break:break-word; white-space:normal; }
    .cap-text{ display:inline-block; position:relative; padding:16px 36px; border-radius:18px;
      background:rgba(0,10,34,0.62); border:2.5px solid rgba(0,240,255,0.8);
      box-shadow:0 0 22px rgba(0,240,255,0.35), inset 0 0 24px rgba(0,240,255,0.08); }
    .cap-content.big .cap-text{ font-size:84px; }
    .cap-content.mid .cap-text{ font-size:60px; }
    .cap-content.small .cap-text{ font-size:44px; }
    /* 逐字跳动 */
    .ch{ display:inline-block; transform-origin:center; will-change:transform,opacity; }
    .cap-text .ch{ margin:0 1px; }

    /* Hero 图片徽章 */
    .cap-hero{ display:flex; flex-direction:column; align-items:center; }
    .icon-box{ position:relative; width:210px; height:210px; margin-bottom:20px;
      display:flex; align-items:center; justify-content:center; }
    .icon-badge{ width:186px; height:186px; border-radius:50%; overflow:hidden;
      border:4px solid var(--primary);
      box-shadow:0 0 40px var(--primary), 0 0 80px rgba(0,240,255,0.2), inset 0 0 30px rgba(0,0,0,0.4);
      background:rgba(0,10,30,0.5); }
    .icon-badge img{ width:100%; height:100%; object-fit:cover; border-radius:50%; }
    .icon-ring{ position:absolute; top:0; left:0; width:100%; height:100%; border-radius:50%;
      border:3px dashed var(--primary); box-shadow:0 0 18px var(--primary); }
    .icon-label{ margin-top:6px; font-size:28px; color:var(--primary); letter-spacing:0.25em;
      text-shadow:0 0 12px var(--primary); }
    """

    css = (css
           .replace("__W__", str(W)).replace("__H__", str(H))
           .replace("__PRI__", C["primary"]).replace("__MAG__", C["magenta"])
           .replace("__GRN__", C["green"]).replace("__AMB__", C["amber"])
           .replace("__TXT__", C["text"])
           .replace("__TOP__", cfg["caption_top"])
           .replace("__DUR__", f"{DUR}")
           .replace("__SWEEP__", f"{max(3.0, DUR/8.0):.1f}")
           .replace("__SPIN__", f"{cb.get('spin_sec',7)}"))

    # ---------- 常驻角落旋转徽章 ----------
    corner_html = ""
    if cb.get("enabled"):
        glyph_svg = icons.get(cb.get("glyph", "bolt"), icons["bolt"])
        corner_html = f'''<div id="cornerBadge" class="corner-badge {cb.get('corner','tr')}">
  <div class="cb-ring"></div>
  <div class="cb-ring2"></div>
  <div class="cb-core">{glyph_svg}</div>
  <div class="cb-label">{escape(cb.get('label',''))}</div>
</div>'''

    # ---------- 字幕 div + GSAP ----------
    cap_divs = []
    used_hero = 0
    gsap_lines = [
        'gsap.set(".cap-content", {autoAlpha:0});',
        'const tl = gsap.timeline({paused:true});',
    ]
    for it in timeline:
        i = it["i"]
        s = it["start"]
        e = it["end"]
        dur = max(round(e - s, 2), 0.6)
        txt = it["text"]
        cls = size_class(txt)
        hero = hero_map.get(i)
        span_html = char_spans(txt)
        inner_id = f"cap{i}_inner"

        if hero:
            img, label = hero[0], hero[1]
            cap_html = f'''<div id="cap{i}" class="clip cap" data-start="{s}" data-duration="{dur}" data-track-index="{i+1}">
  <div id="{inner_id}" class="cap-content cap-hero {cls}">
    <div class="icon-box">
      <div class="icon-badge"><img src="assets/{escape(img)}" alt="" /></div>
      <div class="icon-ring"></div>
    </div>
    <div class="icon-label">{escape(label)}</div>
    <div class="cap-text">{span_html}</div>
  </div>
</div>'''
            cap_divs.append(cap_html)
            used_hero += 1
            # hero 徽章：圆形裁切 + 环旋转（GSAP 有限旋转，确保被录屏捕获）
            gsap_lines.append(f'tl.fromTo("#cap{i} .icon-badge",{{scale:0.5,autoAlpha:0}},{{scale:1,autoAlpha:1,duration:0.55,ease:"back.out(1.6)"}},{s:.2f})')
            gsap_lines.append(f'tl.fromTo("#cap{i} .icon-ring",{{rotation:0}},{{rotation:360,duration:{max(dur-0.3,3.0):.2f},ease:"linear"}},{s:.2f})')
        else:
            ic = icons.get(keyword_icon(txt), icons["spark"])
            cap_html = f'''<div id="cap{i}" class="clip cap" data-start="{s}" data-duration="{dur}" data-track-index="{i+1}">
  <div id="{inner_id}" class="cap-content {cls}">
    <div class="cap-text">{ic}{span_html}</div>
  </div>
</div>'''
            cap_divs.append(cap_html)

        # 通用：容器进入 + 逐字 karaoke 弹出（节奏=说话速率）+ 轻微跳动 + 退出
        gsap_lines.append(f'tl.fromTo("#{inner_id}",{{autoAlpha:0,y:30}},{{autoAlpha:1,y:0,duration:0.35,ease:"back.out(1.3)"}},{s:.2f})')
        if cfg.get("karaoke", True):
            nch = max(len([c for c in txt if c.strip()]), 1)
            per = min(dur / nch, 0.16)
            gsap_lines.append(
                f'tl.fromTo("#cap{i} .ch",{{autoAlpha:0.12,scale:0.7}},'
                f'{{autoAlpha:1,scale:1,duration:{min(per*0.9,0.16):.3f},ease:"back.out(2)",stagger:{per:.3f}}},{s+0.15:.2f})')
        # 跳动呼吸：让当前句"活"起来
        gsap_lines.append(f'tl.to("#{inner_id}",{{scale:1.035,duration:0.4,yoyo:true,repeat:1,transformOrigin:"center center"}},{s+0.25:.2f})')
        out_t = max(e - 0.35, s + 0.6)
        gsap_lines.append(f'tl.to("#{inner_id}",{{autoAlpha:0,y:-18,duration:0.3,ease:"power1.in"}},{out_t:.2f})')
        gsap_lines.append(f'tl.set("#{inner_id}",{{autoAlpha:0}},{e:.2f})')

    gsap_lines.append('window.__timelines = window.__timelines || {};')
    gsap_lines.append('window.__timelines["edit"] = tl;')
    gsap_lines.append('if (!navigator.webdriver) tl.play();')

    # ---------- 组装 HTML ----------
    hud_layers = []
    if hud.get("vignette", True): hud_layers.append('<div class="hud-vignette"></div>')
    if hud.get("dots", True):    hud_layers.append('<div class="dotgrid"></div>')
    if hud.get("scanlines", True): hud_layers.append('<div class="scanlines"></div>')
    if hud.get("sweep", True):    hud_layers.append('<div class="sweep"></div>')
    if hud.get("corners", True):
        hud_layers.append('<div class="hud-corners"><div class="corner tl"></div><div class="corner tr"></div><div class="corner bl"></div><div class="corner br"></div></div>')
    progress_html = '<div class="progress"><i></i></div>' if hud.get("progress", True) else ""

    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width={W}, initial-scale=1" />
<title>口播动销 - Hyperframes v5</title>
<style>{css}</style>
</head>
<body>
<div id="stage" data-composition-id="edit" data-start="0" data-width="{W}" data-height="{H}">
  <video id="clip" class="clip" data-start="0" data-duration="{DUR}" data-has-audio="true" data-track-index="0" src="src_fixed.mp4" playsinline></video>
  <div id="hud" class="clip hud" data-start="0" data-duration="{DUR}" data-track-index="1">
{chr(10).join("    " + L for L in hud_layers)}
  </div>
  {corner_html}
  {progress_html}
{chr(10).join(cap_divs)}
</div>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.12.5/dist/gsap.min.js"></script>
<script>
{chr(10).join(gsap_lines)}
</script>
</body>
</html>'''

    open("index.html", "w", encoding="utf-8").write(html)
    n_hero = used_hero
    print(f"index.html 写入: DUR={DUR}s, {len(timeline)} 段字幕, {n_hero} 个 hero 徽章, 角落徽章={'开' if cb.get('enabled') else '关'}, 逐字跳动={'开' if cfg.get('karaoke') else '关'}")


if __name__ == "__main__":
    build()
