#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gen_rich.py —— 导演式口播成片生成器（hyperframes-edit 富图层定稿版）
==============================================================
输入（工程目录下）：
  - timeline.json       : make_timeline.py 产出（口播切句 + 时间戳）
  - beats.json          : 富图层内容配置（从 beats.example.json 复制改内容）
  - src_fixed.mp4       : 转码后的口播视频
  - gsap.min.js         : 本地 GSAP（离线必需；无则自动改 CDN）
  - config.json         : 可选，配 徽章/配色/字幕开关
输出：
  - index.html          : 交给 render.sh 渲染

⚠️ v6.4 同步根治（动效绑【真实说话时间】，根治"动效比字幕快很多"）：
  富图层 scene = 外层 .clip（带 data-start/duration，引擎按窗口显隐，与视频/字幕共用【同一主时钟】）
                + 内层 .sc-inner（非 .clip，纯 GSAP 做入场/退场/scale 动效，引擎不重置其 style）。
  ★ 动效时间基准：每个 beat 用 `win:[t1,t2]` 直接指定【真实说话秒数】（优先用 faster-whisper 从音频提取的真实说话时间轴，
    与剪映字幕同源）。动效窗口 = 真实说话起 +0.1s（略晚不抢跑） ~ 真实说话止 +0.35s（余韵）。彻底杜绝"快很多"。
    （兼容旧：`cap` 绑 timeline.json 句索引 / `s/e` 手填秒数，但 v6.4 默认【推荐 win 真实秒数】，因旧时间轴由静音检测
     切出、系统性偏早，正是之前反复"动效抢跑"的隐藏根因。）
  ★ 字幕层开关：config.json 的 `show_caption` 控制是否叠加生成字幕层（.cap）。默认 true；若用户视频【已自带字幕】，
    务必设 `show_caption:false` 关掉，否则成片会出现两排字幕、且时间不一致（v6.3 前反复"不同步"的隐藏根因之一）。
  ★ 内容铁律：动效只做【关键词增强】（简图/图标/表格/大数字），绝不重复口播长句——动效是给字幕加料，不是第二套字幕。
  ⚠️ 旧坑：GSAP 动效只能写在内层 .sc-inner；若写在外层 .clip，引擎每帧重置其 inline style 会压掉 GSAP。
"""
import json, os, sys, re

BASE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.getcwd()

def load_json(name, default=None):
    p = os.path.join(PROJ, name)
    if not os.path.exists(p):
        return default
    with open(p, encoding="utf-8") as f:
        return json.load(f)

tl = load_json("timeline.json")
if not tl:
    sys.exit("FATAL: 找不到 timeline.json（先跑 make_timeline.py）")
DUR = round(tl[-1]["end"], 2)
W, H = 1080, 1920

# beats 配置：优先 beats.json，否则用 --demo 时回退 example
beats_cfg = load_json("beats.json")
if not beats_cfg:
    ex = os.path.join(BASE, "beats.example.json")
    if os.path.exists(ex):
        print("[gen_rich] 未找到 beats.json，使用自带 example（仅演示）")
        beats_cfg = json.load(open(ex, encoding="utf-8"))
    else:
        sys.exit("FATAL: 找不到 beats.json 也没有 example")
beats = beats_cfg.get("beats", [])

# 可选 config：徽章 / 配色 / 字幕开关
cfg = load_json("config.json") or {}
BADGE_CORE = cfg.get("badge_core", "⚡")
BADGE_LABEL = cfg.get("badge_label", "AI口播")
SHOW_CAP = cfg.get("show_caption", True)
PRIMARY = cfg.get("color_primary", "#00f0ff")
MAGENTA = cfg.get("color_magenta", "#ff4dff")
GREEN = cfg.get("color_green", "#39ff14")
AMBER = cfg.get("color_amber", "#ffcc00")
INK = cfg.get("color_ink", "#ff2a6d")

# ---------------- CSS ----------------
CSS = f"""
* {{ box-sizing: border-box; }}
html, body {{ margin:0; padding:0; width:100%; height:100%; background:#000; overflow:hidden; }}
@font-face {{ font-family:'Microsoft YaHei'; src: local('Microsoft YaHei'); }}
#stage{{ position:relative; width:{W}px; height:{H}px; overflow:hidden; background:#000; margin:0 auto;
  --primary:{PRIMARY}; --magenta:{MAGENTA}; --green:{GREEN}; --amber:{AMBER}; --ink:{INK}; --text:#ffffff; }}
#cam{{ position:absolute; inset:0; transform-origin:center center; will-change:transform; }}
#clip{{ position:absolute; top:0; left:0; width:100%; height:100%; object-fit:cover; display:block; }}
.hud{{ position:absolute; inset:0; pointer-events:none; z-index:5;
  background: radial-gradient(circle at 50% 0%, rgba(0,240,255,0.06), transparent 55%); }}
.hud-corners{{ position:absolute; inset:24px; border:1px solid rgba(0,240,255,0.18); }}
.corner{{ position:absolute; width:70px; height:70px; }}
.corner.tl{{ top:0;left:0;border-top:3px solid var(--primary);border-left:3px solid var(--primary);border-top-left-radius:12px;}}
.corner.tr{{ top:0;right:0;border-top:3px solid var(--primary);border-right:3px solid var(--primary);border-top-right-radius:12px;}}
.corner.bl{{ bottom:0;left:0;border-bottom:3px solid var(--primary);border-left:3px solid var(--primary);border-bottom-left-radius:12px;}}
.corner.br{{ bottom:0;right:0;border-bottom:3px solid var(--primary);border-right:3px solid var(--primary);border-bottom-right-radius:12px;}}
.vignette{{ position:absolute; inset:0; box-shadow: inset 0 0 200px 70px rgba(0,0,0,0.4); }}
.sweep{{ position:absolute; left:0; width:100%; height:3px; top:0;
  background:linear-gradient(90deg,transparent,var(--primary),transparent); opacity:0.35;
  box-shadow:0 0 12px var(--primary); animation: sweepmove 14s linear infinite; }}
@keyframes sweepmove {{ 0%{{top:3%}} 100%{{top:97%}} }}
.corner-badge{{ position:absolute; width:140px; height:140px; z-index:9; top:46px; right:46px; }}
.cb-ring{{ position:absolute; inset:0; border-radius:50%; border:3px dashed var(--primary);
  box-shadow:0 0 22px var(--primary); animation: cbspin 7s linear infinite; }}
.cb-ring2{{ position:absolute; inset:13px; border-radius:50%; border:2px solid rgba(0,240,255,0.35); }}
.cb-core{{ position:absolute; inset:28px; border-radius:50%; background:rgba(0,10,30,0.6);
  border:2px solid var(--primary); display:flex; align-items:center; justify-content:center;
  color:var(--primary); font-size:30px; font-weight:800; text-shadow:0 0 12px var(--primary); }}
.cb-label{{ position:absolute; bottom:-26px; left:0; right:0; text-align:center;
  color:var(--primary); font-size:21px; letter-spacing:0.2em; text-shadow:0 0 10px var(--primary); }}
@keyframes cbspin {{ to {{ transform: rotate(360deg); }} }}
.cap{{ position:absolute; left:0; right:0; bottom:6%; display:flex; justify-content:center; padding:0 40px;
  pointer-events:none; z-index:8; }}
.cap .pill{{ max-width:92%; text-align:center; font-family:'Microsoft YaHei',sans-serif; font-weight:700;
  font-size:36px; line-height:1.3; color:#fff; background:rgba(0,8,24,0.5); padding:12px 26px;
  border-radius:16px; border:1px solid rgba(0,240,255,0.35); text-shadow:0 2px 8px #000; }}
.sc{{ position:absolute; z-index:11; pointer-events:none; left:0; right:0; top:3%; bottom:35%;
  display:flex; flex-direction:column; justify-content:flex-start; overflow:hidden; }}
.sc-inner{{ width:100%; }}
.sc-top{{ justify-content:flex-start; align-items:center; text-align:center; }}
.kicker{{ font-family:'Microsoft YaHei',sans-serif; font-weight:900; font-size:40px; color:var(--amber);
  letter-spacing:0.12em; padding:10px 30px; border:2px solid rgba(255,204,0,0.6); border-radius:40px;
  background:rgba(20,14,0,0.5); text-shadow:0 0 14px rgba(255,204,0,0.5); }}
.sc-center{{ left:6%; right:6%; top:6%; justify-content:flex-start; align-items:center; text-align:center; }}
.bigstat{{ font-family:'Microsoft YaHei',sans-serif; font-weight:900; font-size:150px; line-height:1; color:var(--ink);
  text-shadow:0 0 40px rgba(255,42,109,0.6); }}
.bigstat .pct{{ font-size:76px; }}
.sc-center .sub{{ font-size:38px; color:#fff; font-weight:700; margin-top:6px; text-shadow:0 2px 12px #000; }}
.dbar{{ margin:22px auto 0; width:70%; height:26px; background:rgba(255,255,255,0.12);
  border-radius:14px; overflow:hidden; border:1px solid rgba(255,42,109,0.5); }}
.dbar > i{{ display:block; height:100%; width:100%; transform-origin:left center; transform:scaleX(1);
  background:linear-gradient(90deg,var(--ink),#ff8800); }}
.shout{{ font-family:'Microsoft YaHei',sans-serif; font-weight:900; font-size:74px; line-height:1.25; color:#fff;
  text-shadow:0 0 26px rgba(0,0,0,0.7); }}
.shout.sm{{ font-size:60px; }}
.shout .hi{{ color:var(--green); text-shadow:0 0 22px rgba(57,255,20,0.6); }}
.shout.warm .hi{{ color:var(--amber); text-shadow:0 0 22px rgba(255,204,0,0.6); }}
.sc-left{{ left:5%; right:46%; justify-content:center; align-items:flex-start; }}
.sc-right{{ right:5%; left:46%; justify-content:center; align-items:flex-end; }}
.card-h{{ font-size:34px; color:var(--primary); font-weight:800; letter-spacing:0.1em; text-shadow:0 0 12px rgba(0,240,255,0.5);}}
.card-t{{ font-family:'Microsoft YaHei',sans-serif; font-weight:900; font-size:74px; color:#fff; line-height:1.1; margin:6px 0;
  text-shadow:0 0 24px rgba(0,240,255,0.4); }}
.card-d{{ font-size:38px; color:var(--green); font-weight:700; text-shadow:0 0 14px rgba(57,255,20,0.5); }}
.sc-left .t-title{{ font-family:'Microsoft YaHei',sans-serif; font-weight:900; font-size:42px; color:var(--primary);
  margin-bottom:14px; letter-spacing:0.06em; text-shadow:0 0 16px rgba(0,240,255,0.5); }}
.sc-left .row{{ display:flex; justify-content:space-between; align-items:center; padding:12px 0;
  border-bottom:1px solid rgba(0,240,255,0.16); font-size:36px; }}
.sc-left .row span{{ color:#9fe; font-weight:600; opacity:0.85; }}
.sc-left .row b{{ color:#fff; font-weight:800; }}
.sc-left .row.hl b{{ color:var(--green); text-shadow:0 0 12px rgba(57,255,20,0.6); }}
.sc-left .sc-inner{{ background:rgba(0,10,34,0.72); border:2px solid rgba(0,240,255,0.6); border-radius:20px; padding:22px 28px;
  box-shadow:0 0 30px rgba(0,240,255,0.3); }}
.sc-split{{ left:5%; right:5%; justify-content:center; align-items:center; text-align:center; }}
.split-wrap{{ display:flex; align-items:center; justify-content:space-between; gap:14px;
  background:rgba(0,10,34,0.74); border:2px solid rgba(0,240,255,0.55); border-radius:20px; padding:24px 22px;
  box-shadow:0 0 30px rgba(0,240,255,0.3); }}
.sp{{ flex:1; text-align:center; font-family:'Microsoft YaHei',sans-serif; font-weight:800; font-size:46px; color:#fff;
  line-height:1.3; padding:14px 8px; border-radius:14px; }}
.sp.old{{ background:rgba(40,0,40,0.5); border:2px dashed rgba(255,77,255,0.6); text-decoration:line-through;
  text-decoration-color:rgba(255,77,255,0.7); }}
.sp.new{{ background:rgba(0,30,10,0.5); border:2px solid rgba(57,255,20,0.7); color:var(--green); }}
.sp.node{{ border:2px solid rgba(0,240,255,0.6); background:rgba(0,10,34,0.6); }}
.sp.node.now{{ border-color:var(--green); box-shadow:0 0 24px rgba(57,255,20,0.4); }}
.sp-h{{ font-size:30px; color:var(--primary); margin-bottom:8px; letter-spacing:0.08em; }}
.sp.node.now .sp-h{{ color:var(--green); }}
.sp-arr{{ font-size:60px; color:var(--amber); text-shadow:0 0 16px var(--amber); }}
.sc-center .quote{{ background:rgba(0,10,34,0.8); border-left:9px solid var(--amber); border-radius:14px;
  padding:30px 36px; box-shadow:0 0 30px rgba(255,204,0,0.3); text-align:left; }}
.sc-center .qm{{ font-family:Georgia,serif; font-size:120px; color:var(--amber); line-height:0.45; opacity:0.65; }}
.sc-center .quote{{ font-family:'Microsoft YaHei',sans-serif; font-weight:800; font-size:54px; color:#fff; line-height:1.35; }}
.sc-right .pip{{ background:rgba(0,12,30,0.88); border:2px solid rgba(0,240,255,0.7); border-radius:14px; overflow:hidden;
  box-shadow:0 0 30px rgba(0,240,255,0.4); }}
.pip-bar{{ display:flex; align-items:center; gap:8px; padding:9px 13px; background:rgba(0,240,255,0.12); }}
.dot{{ width:13px; height:13px; border-radius:50%; }}
.dot.r{{background:#ff5f56;}} .dot.y{{background:#ffbd2e;}} .dot.g{{background:#27c93f;}}
.pip-t{{ margin-left:auto; color:var(--primary); font-weight:800; font-size:26px; }}
.pip-body{{ display:flex; align-items:center; padding:18px 12px; gap:8px; }}
.side{{ flex:1; text-align:center; }}
.side.open .big{{ color:var(--green); font-size:42px; font-weight:900; text-shadow:0 0 14px rgba(57,255,20,0.5); }}
.side.closed .big{{ color:var(--ink); font-size:42px; font-weight:900; text-shadow:0 0 14px rgba(255,42,109,0.5); }}
.side .sm{{ font-size:23px; color:#cde; margin-top:6px; }}
.vs{{ font-size:32px; font-weight:900; color:var(--amber); }}
.sc-center .cta-btn{{ display:inline-block; font-family:'Microsoft YaHei',sans-serif; font-weight:900; font-size:46px;
  color:#001018; background:linear-gradient(90deg,var(--primary),var(--green)); padding:18px 36px; border-radius:50px;
  box-shadow:0 0 30px rgba(0,240,255,0.5); }}
.sc-center .id-badge{{ margin-top:22px; font-size:36px; color:var(--primary); font-weight:800; letter-spacing:0.06em;
  text-shadow:0 0 14px rgba(0,240,255,0.5); }}
.sc-table{{ left:4%; right:4%; top:4%; justify-content:flex-start; align-items:center; }}
.cmp-box{{ width:100%; background:rgba(0,10,34,0.82); border:2px solid rgba(0,240,255,0.6); border-radius:18px;
  box-shadow:0 0 34px rgba(0,240,255,0.32); overflow:hidden; }}
.cmp{{ width:100%; border-collapse:collapse; font-family:'Microsoft YaHei',sans-serif; font-size:30px; }}
.cmp th{{ background:linear-gradient(90deg,rgba(0,240,255,0.22),rgba(0,240,255,0.06)); color:var(--primary);
  font-weight:900; padding:15px 16px; text-align:left; border-bottom:2px solid rgba(0,240,255,0.5); font-size:30px; }}
.cmp td{{ padding:13px 16px; color:#fff; border-bottom:1px solid rgba(0,240,255,0.14); font-weight:700; vertical-align:middle; }}
.cmp tr:last-child td{{ border-bottom:none; }}
.cmp tr:nth-child(even) td{{ background:rgba(0,240,255,0.05); }}
.cmp .hl td{{ background:rgba(57,255,20,0.12); }}
.cmp .hl, .cmp .hl td{{ color:var(--green); }}
.cmp .ico{{ display:inline-block; font-size:38px; margin-right:8px; vertical-align:middle; }}
.cmp .now{{ color:var(--green); text-shadow:0 0 14px rgba(57,255,20,0.55); }}
.cmp .old{{ color:var(--ink); text-decoration:line-through; text-decoration-color:rgba(255,42,109,0.6);
  text-shadow:0 0 12px rgba(255,42,109,0.5); }}
.cmp th.now{{ color:var(--green); }} .cmp th.old{{ color:var(--ink); }}
.cmp .num{{ font-size:44px; font-weight:900; color:var(--green); text-shadow:0 0 16px rgba(57,255,20,0.6); }}
#scrim{{ position:absolute; inset:0; z-index:10; background:#000; opacity:0; pointer-events:none; }}
"""

# ---------------- 字幕（外层 .clip 走引擎显隐窗口=与视频同主时钟；内层 .pill 走 GSAP 淡入淡出，硬 kill 防跳帧残留） ----------------
cap_divs = []
cap_lines = []
if SHOW_CAP:
    for it in tl:
        i = it["i"]; s = it["start"]; e = it["end"]; dur = max(round(e-s,2),0.6)
        txt = it["text"].replace('"','&quot;')
        cap_divs.append(f'<div id="cap{i}" class="clip cap" data-start="{s}" data-duration="{dur}" data-track-index="{i+10}">'
                        f'<div class="pill" id="cap{i}_i">{txt}</div></div>')
        cap_lines.append(f'tl.fromTo("#cap{i}_i",{{autoAlpha:0,y:14}},{{autoAlpha:1,y:0,duration:0.3,ease:"power1.out"}},{s:.2f})')
        out_t = max(e-0.3, s+0.5)
        cap_lines.append(f'tl.to("#cap{i}_i",{{autoAlpha:0,y:-10,duration:0.3,ease:"power1.in"}},{out_t:.2f})')
        cap_lines.append(f'tl.set("#cap{i}_i",{{autoAlpha:0}},{e:.2f})')

# ---------------- 富图层（v6.3：动效窗口由字幕句 cap 派生 → 与口播字幕【同主时钟】；内容=关键词+简图/图标/表格，不重复字幕） ----------------
# timeline 索引：i -> {start,end}
_cap_map = {it["i"]: it for it in tl}

def _beat_win(b):
    """动效窗口来源（优先级从高到低）：
    win=[t1,t2]  -> 真实秒数直接指定（whisper 提取的真实说话时间，最准，根治"快很多"）
    cap 索引      -> timeline.json 句索引（兼容旧用法）
    s/e           -> 手写秒数
    """
    win = b.get("win")
    if isinstance(win, list) and len(win) == 2:
        return float(win[0]), float(win[1])
    cap = b.get("cap")
    if cap is None:
        return float(b["s"]), float(b["e"])
    if isinstance(cap, list) and len(cap) == 2:
        a = _cap_map[cap[0]]; z = _cap_map[cap[1]]
        return float(a["start"]), float(z["end"])
    it = _cap_map[int(cap)]
    return float(it["start"]), float(it["end"])

scene_divs = []
scene_js = []
track = 200
for b in beats:
    s_raw, e_raw = _beat_win(b)
    # 同步核心（v6.4 根治"动效比字幕快"）：动效窗口基于真实说话时间，
    # 动效比真实说话【晚 0.1s】出现（对齐口播字幕通常的显示时刻，绝不会比字幕快），
    # 字幕结束后留 0.35s 余韵。
    s = round(max(s_raw + 0.1, 0.0), 2)
    e = round(e_raw + 0.35, 2)
    dur = round(e - s, 2)
    out_t = round(max(e - 0.35, s + 0.7), 2)
    layout = b.get("layout", "top")
    html = b.get("html", "")
    cam = b.get("cam", {"scale": 1.08, "x": 0, "y": 0, "rot": 0})
    inner_id = f'{b["id"]}_i'
    # 外层 .clip 走引擎窗口（与字幕同主时钟）→ 彻底同步；内层 .sc-inner 纯 GSAP 动效
    scene_divs.append(f'<div id="{b["id"]}" class="clip sc sc-{layout}" data-start="{s:.2f}" data-duration="{dur:.2f}" data-track-index="{track}">'
                       f'<div class="sc-inner" id="{inner_id}">{html}</div></div>')
    track += 1
    if layout == "left":
        frm = "{autoAlpha:0,x:-60,y:10,scale:0.94}"
    elif layout == "right":
        frm = "{autoAlpha:0,x:60,y:10,scale:0.94}"
    elif layout == "top":
        frm = "{autoAlpha:0,y:-24,scale:0.92}"
    else:
        frm = "{autoAlpha:0,y:28,scale:0.92}"
    SEL = f'"#{inner_id}"'
    # 入场 0.3s 内完成（窗口内），与字幕同时稳住；退场在结束前 0.3s
    scene_js.append(f'tl.fromTo({SEL},{frm},{{autoAlpha:1,x:0,y:0,scale:1,duration:0.3,ease:"back.out(1.6)"}},{s:.2f})')
    scene_js.append(f'tl.to({SEL},{{autoAlpha:0,y:-18,duration:0.35,ease:"power1.in"}},{out_t:.2f})')
    scene_js.append(f'tl.set({SEL},{{autoAlpha:0}},{e:.2f})')
    # 自动动效：数字滚动 (class="num" data-to) + 图标脉冲 (class="ico")
    if 'class="num"' in html or "class='num'" in html:
        mnum = re.search(r"class=[\"']num[\"'][^>]*data-to=[\"']([\d.]+)[\"']", html)
        if mnum:
            scene_js.append(f'countTo("#{inner_id} .num",0,{float(mnum.group(1)):.0f},1.0,{s+0.2:.2f});')
    if re.search(r"class=[\"']ico[\"']", html):
        scene_js.append(f'pulse("#{inner_id} .ico",{s+0.3:.2f});')
    if b.get("extra"):
        scene_js.append(b["extra"])
    if b.get("scrim"):
        scene_js.append(f'tl.to("#scrim",{{autoAlpha:0.4}},{s+0.05:.2f})')
        scene_js.append(f'tl.to("#scrim",{{autoAlpha:0}},{out_t:.2f})')

# 运镜：关键词出现时一次性推近强调（<0.5s），随后回稳，不持续放大挡脸
cam_js = ['gsap.set("#cam",{scale:1.0,x:0,y:0,rotation:0});']
for b in beats:
    s_raw, e_raw = _beat_win(b)
    s = round(max(s_raw + 0.1, 0.0), 2)
    c = b.get("cam", {"scale":1.08,"x":0,"y":0,"rot":0})
    cs = c.get("scale", 1.08)
    cam_js.append(f'tl.to("#cam",{{scale:{cs},duration:0.45,ease:"power2.out"}},{s+0.05:.2f})')
    cam_js.append(f'tl.to("#cam",{{scale:1.03,duration:0.75,ease:"power2.inOut"}},{s+0.5:.2f})')

badge = (f'<div id="cornerBadge" class="corner-badge">'
         f'<div class="cb-ring"></div><div class="cb-ring2"></div>'
         f'<div class="cb-core">{BADGE_CORE}</div><div class="cb-label">{BADGE_LABEL}</div></div>')

hud = ('<div id="hud" class="clip hud" data-start="0" data-duration="__DUR__" data-track-index="1">'
       '<div class="hud-corners"><div class="corner tl"></div><div class="corner tr"></div>'
       '<div class="corner bl"></div><div class="corner br"></div></div>'
       '<div class="sweep"></div><div class="vignette"></div></div>').replace("__DUR__",f"{DUR}")

# GSAP 来源：优先本地（脚本目录自带，自动拷到工程目录），否则 CDN（离线会不可见）
_bundled = os.path.join(BASE, "gsap.min.js")
_local = os.path.join(PROJ, "gsap.min.js")
if os.path.exists(_local):
    gsap_src = "gsap.min.js"
elif os.path.exists(_bundled):
    import shutil
    shutil.copy(_bundled, _local)
    gsap_src = "gsap.min.js"
    print("[gen_rich] 已自动拷贝自带 gsap.min.js 到工程目录（离线安全）")
else:
    gsap_src = "https://cdn.jsdelivr.net/npm/gsap@3/dist/gsap.min.js"
    print("[gen_rich] 警告：未找到本地 gsap.min.js，将用 CDN（离线会导致富图层不可见）")

gsap_all = ["'use strict';"]
gsap_all.append('''
function countTo(sel, from, to, dur, at){
  var el = document.querySelector(sel); if(!el) return;
  var o = {v:from};
  tl.to(o, {v:to, duration:dur, ease:"power1.out", onUpdate:function(){ el.textContent = Math.round(o.v); }}, at);
}
function pulse(sel, at){
  tl.fromTo(sel, {scale:1}, {scale:1.28, duration:0.18, yoyo:true, repeat:5, ease:"sine.inOut", transformOrigin:"center center"}, at);
}
function flashHi(sel, at){
  tl.fromTo(sel, {scale:1}, {scale:1.12, duration:0.22, yoyo:true, repeat:3, ease:"sine.inOut"}, at);
}
''')
gsap_all.append("gsap.set('.sc-inner',{autoAlpha:0});")   # 内层动效初始隐藏，由 tl 在各节拍点亮
gsap_all.append("gsap.set('.pill',{autoAlpha:0});")        # 字幕内层初始隐藏
gsap_all.append("const tl = gsap.timeline({paused:true});")
gsap_all += cap_lines
gsap_all += scene_js
gsap_all += cam_js
gsap_all.append('window.__timelines = window.__timelines || {};')
gsap_all.append('window.__timelines["edit"] = tl;')
gsap_all.append('if (!navigator.webdriver) tl.play();')
# 纯浏览器预览兜底：引擎不管理 .clip 窗口时，用 video 时间轴手动开关外层
# （render 模式下 navigator.webdriver=true，此段不执行，由引擎按 data-start/duration 锁定显隐→与字幕同主时钟）
gsap_all.append('''
if (!navigator.webdriver) {
  var __v = document.getElementById('clip');
  var __clips = Array.prototype.slice.call(document.querySelectorAll('.clip')).filter(function(el){return el.id!=='clip' && el.id!=='hud';});
  function __syncPrev(){ if(!__v) return; var t=__v.currentTime; for(var k=0;k<__clips.length;k++){var el=__clips[k];var s=parseFloat(el.dataset.start||0),d=parseFloat(el.dataset.duration||0);el.style.display=(t>=s&&t<=s+d)?'':'none';} }
  if(__v){ __v.addEventListener('timeupdate',__syncPrev); __v.addEventListener('play',__syncPrev); __syncPrev(); }
}
''')

html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="{W}, initial-scale=1" />
<title>口播动销 - 富图层导演版</title>
<style>{CSS}</style>
</head>
<body>
<div id="stage" data-composition-id="edit" data-start="0" data-width="{W}" data-height="{H}">
  <div id="cam">
    <video id="clip" class="clip" data-start="0" data-duration="{DUR}" data-has-audio="true" data-track-index="0" src="src_fixed.mp4" playsinline></video>
  </div>
  {hud}
  <div id="scrim"></div>
  {badge}
{chr(10).join("  "+d for d in scene_divs)}
{chr(10).join("  "+d for d in cap_divs)}
</div>
<script src="{gsap_src}"></script>
<script>
{chr(10).join(gsap_all)}
</script>
</body>
</html>'''

open("index.html","w",encoding="utf-8").write(html)
print(f"gen_rich.py 完成: DUR={DUR}s, {len(beats)} 关键节拍, {len(tl)} 字幕, 字幕={'开' if SHOW_CAP else '关'}, gsap={'本地' if gsap_src=='gsap.min.js' else 'CDN(离线风险!)'}")
