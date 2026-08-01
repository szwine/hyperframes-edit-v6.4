#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
hyperframes-edit v4 — 生成字幕时间轴 timeline.json
用法: python make_timeline.py <silence_log> <segments_txt> [T0] [T1]
  silence_log : silencedetect 输出 (silence_start / silence_end 各占一行)
  segments_txt: 每行一句口播文案 (UTF-8)
  T0 / T1     : 语音区间起止(秒)，默认取 silence 首起 / 尾止
输出: timeline.json  -> [{"i":1,"text":"...","start":0.37,"end":2.10}, ...]
"""
import sys, re, json


def parse_silence(path):
    starts, ends = [], []
    for line in open(path, encoding="utf-8", errors="ignore"):
        ms = re.search(r"silence_start:\s*([\d.]+)", line)
        me = re.search(r"silence_end:\s*([\d.]+)", line)
        if ms:
            starts.append(float(ms.group(1)))
        if me:
            ends.append(float(me.group(1)))
    n = min(len(starts), len(ends))
    centers = sorted([(starts[k] + ends[k]) / 2 for k in range(n)])
    T0 = starts[0] if starts else 0.377
    T1 = ends[-1] if ends else 186.0
    return centers, T0, T1


def load_segments(path):
    return [ln.strip() for ln in open(path, encoding="utf-8") if ln.strip()]


def main():
    if len(sys.argv) < 3:
        print("用法: python make_timeline.py <silence_log> <segments_txt> [T0] [T1]")
        sys.exit(1)
    gc, defT0, defT1 = parse_silence(sys.argv[1])
    segs = load_segments(sys.argv[2])
    T0 = float(sys.argv[3]) if len(sys.argv) > 3 else defT0
    T1 = float(sys.argv[4]) if len(sys.argv) > 4 else defT1
    D = T1 - T0
    C = sum(len(s) for s in segs)
    if C == 0:
        print("ERR: 文案为空")
        sys.exit(1)

    # 累计字符起点
    cum = [0]
    for s in segs:
        cum.append(cum[-1] + len(s))          # 长度 N+1
    b = [T0 + (cum[k] / C) * D for k in range(len(cum))]  # b[0..N]

    # 把内部边界吸附到最近的真实停顿中心（窗口 ±4.0s）
    MIND = 1.3
    used = [False] * len(gc)
    for i in range(1, len(b) - 1):
        best, bd, bi = None, 1e9, -1
        for j, c in enumerate(gc):
            if used[j]:
                continue
            d = abs(c - b[i])
            if d < bd:
                bd, best, bi = d, c, j
        if best is not None and bd <= 4.0:
            b[i], used[bi] = best, True

    # 单调 + 最短可读 1.3s
    for i in range(1, len(b)):
        if b[i] < b[i - 1] + MIND:
            b[i] = b[i - 1] + MIND
    b[-1] = T1
    for i in range(len(b) - 2, 0, -1):
        if b[i] > b[i + 1] - MIND:
            b[i] = b[i + 1] - MIND
    for i in range(1, len(b)):
        if b[i] <= b[i - 1]:
            b[i] = b[i - 1] + MIND
    b[-1] = T1

    out = [{"i": i + 1, "text": segs[i], "start": round(b[i], 2), "end": round(b[i + 1], 2)}
           for i in range(len(segs))]
    json.dump(out, open("timeline.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    mind = min(b[i + 1] - b[i] for i in range(len(b) - 1))
    print(f"timeline.json 写入: {len(out)} 段, T0={T0:.2f} T1={T1:.2f} 最短段={mind:.2f}s")


if __name__ == "__main__":
    main()
