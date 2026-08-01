@echo off
chcp 65001 >nul
title hyperframes.edit v6.4 - 预处理（转码 + 时间轴 + 生成叠层）
setlocal EnableDelayedExpansion
echo ============================================================
echo   hyperframes.edit v6.4  预处理
echo   把 src.mp4 变成 index.html（渲染前的所有准备）
echo ============================================================
echo.

REM 定位运行时（优先环境变量，否则按 install.bat 的默认规则找）
if defined HF_RUNTIME (set "RT=%HF_RUNTIME%") else (
  if exist "D:\hyperframes-edit-runtime" (set "RT=D:\hyperframes-edit-runtime") else (set "RT=%USERPROFILE%\.workbuddy\hyperframes-edit-runtime")
)
set "FF=%RT%\ffmpeg\bin\ffmpeg.exe"
if not exist "%FF%" (
  echo [FAIL] 找不到 ffmpeg（%FF%）
  echo   请先双击 install.bat 完成安装，再重跑本脚本。
  pause & exit /b 1
)

REM 检查 Python
where python >nul 2>nul
if errorlevel 1 (
  echo [FAIL] 找不到 python。请到微软商店装 Python 3.9+ 后重跑。
  pause & exit /b 1
)
set "PY=python"

REM 检查工程输入（脚本需放在「当前文件夹」；最简单就是直接在本仓库文件夹里操作，
REM 或把 scripts/ 和本 bat 一起复制到你的视频文件夹里）
if not exist "src.mp4" (
  echo [FAIL] 当前文件夹缺少 src.mp4（你的口播原视频，需改名为 src.mp4，不要中文名）
  pause & exit /b 1
)
if not exist "script_segments.txt" (
  echo [FAIL] 当前文件夹缺少 script_segments.txt（口播稿，一句一行，UTF-8）
  pause & exit /b 1
)
if not exist "beats.json" (
  echo [WARN] 没找到 beats.json，先用范例生成（请随后改成你自己的 win 时间）
  if exist "scripts\beats.example.json" (copy /Y "scripts\beats.example.json" "beats.json" >nul)
)

echo.
echo [1/5] 转码 H.264（HEVC 源必须，否则黑屏）...
"%FF%" -y -i src.mp4 -c:v libx264 -crf 18 -preset fast -pix_fmt yuv420p -r 30 src_fixed.mp4
if errorlevel 1 (echo [FAIL] 转码失败 & pause & exit /b 1)

echo [2/5] 抽音频（给静音检测用）...
"%FF%" -y -i src.mp4 -vn -ac 1 -ar 16000 _audio.wav
if errorlevel 1 (echo [FAIL] 抽音频失败 & pause & exit /b 1)

echo [3/5] 静音检测生成 _silence.txt（时间轴的来源）...
"%FF%" -y -i _audio.wav -af silencedetect=noise=-26dB:d=0.12 -f null - 2>_silence.txt
if errorlevel 1 (echo [FAIL] 静音检测失败 & pause & exit /b 1)

echo [4/5] 生成字幕时间轴 timeline.json...
"%PY%" scripts/make_timeline.py _silence.txt script_segments.txt
if not exist "timeline.json" (echo [FAIL] timeline.json 未生成 & pause & exit /b 1)

echo [5/5] 生成叠层 index.html...
"%PY%" scripts/gen_rich.py
if not exist "index.html" (echo [FAIL] index.html 未生成 & pause & exit /b 1)

echo.
echo ============================================================
echo   ✅ 预处理完成！
echo   接下来双击 render.bat 渲染成片（输出 out.mp4）。
echo ============================================================
pause
