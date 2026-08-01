#!/bin/bash
set -e
# 在工程目录(含 src_fixed.mp4 / index.html / timeline.json)下运行本脚本
# ===== 粉丝分发版：自动定位运行时 =====
# 运行时根目录：优先用环境变量 HF_RUNTIME（install.bat 设置的），否则用 ~/.workbuddy/hyperframes-edit-runtime
if [ -n "$HF_RUNTIME" ]; then
  RT="$HF_RUNTIME"
else
  RT="$HOME/.workbuddy/hyperframes-edit-runtime"
fi
# ffmpeg 二进制目录（BtbN 版），install.bat 下载后放在 $RT/ffmpeg/bin
FFBIN="$RT/ffmpeg/bin"
# 转成 Windows 原生路径再塞进 PATH，确保 node/hyperframes 子进程能找到 ffmpeg/ffprobe
FFBIN_WIN=$(cygpath -w "$FFBIN" 2>/dev/null || echo "$FFBIN")
export PATH="$FFBIN_WIN:$PATH"
export HYPERFRAMES_FFMPEG_PATH="$FFBIN_WIN/ffmpeg.exe"
FFPROBE="$FFBIN/ffprobe.exe"
FFMPEG="$FFBIN/ffmpeg.exe"

# 自动定位 chrome-headless-shell（版本号可变）
CHROME=$(ls "$RT"/chrome-headless-shell/*/chrome-headless-shell-win64/chrome-headless-shell.exe 2>/dev/null | head -1)
if [ -z "$CHROME" ]; then echo "FATAL: 找不到 chrome-headless-shell"; exit 1; fi
export HYPERFRAMES_BROWSER_PATH="$CHROME"
export PRODUCER_LOW_MEMORY_MODE=false

# Node：install.bat 会把 node.exe 装到 $RT/bin/node/node.exe
NODE="$RT/bin/node/node.exe"
if [ ! -x "$NODE" ]; then NODE=$(command -v node || echo ""); fi
CLI="$RT/hyperframes-install/node_modules/hyperframes/dist/cli.js"
SRCSRC="src_fixed.mp4"

if [ ! -x "$FFPROBE" ]; then echo "FATAL: ffprobe 不在 $FFBIN"; exit 1; fi

echo "=== render start $(date) ==="
"$NODE" "$CLI" render -o out.mp4
RENDER_EXIT=$?
echo "RENDER_EXIT=$RENDER_EXIT"

# ---------- 兜底 1：out.mp4 缺视频流 / 渲染非 0 退出 → 从 video-only.mp4 恢复 ----------
has_video=$("$FFPROBE" -v error -select_streams v:0 -show_entries stream=codec_type -of csv=p=0 out.mp4 2>/dev/null || true)
if [ -z "$has_video" ] || [ "$RENDER_EXIT" -ne 0 ]; then
  echo "[兜底] out.mp4 无效(exit=$RENDER_EXIT, video='$has_video')，尝试从 hyperframes 的 video-only.mp4 恢复"
  VID=""
  # 找最新的 work-* 目录里的 video-only.mp4
  for d in $(ls -dt work-* 2>/dev/null); do
    if [ -f "$d/video-only.mp4" ]; then VID="$d/video-only.mp4"; break; fi
  done
  if [ -z "$VID" ]; then
    echo "FATAL: 找不到 video-only.mp4，无法兜底，请检查 render 日志"
    exit 1
  fi
  echo "[兜底] 使用 $VID (无音频预编码帧) + $SRCSRC 原声 → out.mp4"
  "$FFMPEG" -y -i "$VID" -i "$SRCSRC" -map 0:v:0 -map 1:a:0 -c:v copy -c:a copy -movflags +faststart -shortest out.mp4
  echo "[兜底] 已用 video-only.mp4 重新合成 out.mp4"
fi

# ---------- 兜底 2：out.mp4 仍缺音轨 → 从 src_fixed.mp4 混回原声 ----------
HAS_AUD=$("$FFPROBE" -v error -select_streams a -show_entries stream=index -of csv=p=0 out.mp4 2>/dev/null || true)
if [ -z "$HAS_AUD" ]; then
  echo "NO audio in out.mp4 -> mux from $SRCSRC"
  "$FFMPEG" -y -i out.mp4 -i "$SRCSRC" -map 0:v:0 -map 1:a:0 -c:v copy -c:a copy -shortest final_mux.mp4
  mv -f final_mux.mp4 out.mp4
  echo "MUXED audio from $SRCSRC"
else
  echo "audio already present, keep as-is"
fi

echo "=== final verify ==="
"$FFPROBE" -v error -show_entries format=duration:stream=index,codec_type,codec_name,width,height,r_frame_rate -of default=noprint_wrappers=1 out.mp4
echo "=== DONE $(date) ==="
