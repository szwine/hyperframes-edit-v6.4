@echo off
chcp 65001 >nul
title hyperframes.edit v6.4 - 渲染（cmd 版，无需 Git Bash）
setlocal EnableDelayedExpansion
echo ============================================================
echo   hyperframes.edit v6.4  渲染
echo   读取 index.html + 音频兜底 -> out.mp4
echo ============================================================
echo.

REM 定位运行时
if defined HF_RUNTIME (set "RT=%HF_RUNTIME%") else (
  if exist "D:\hyperframes-edit-runtime" (set "RT=D:\hyperframes-edit-runtime") else (set "RT=%USERPROFILE%\.workbuddy\hyperframes-edit-runtime")
)
set "FFBIN=%RT%\ffmpeg\bin"
set "PATH=%FFBIN%;%PATH%"
set "HYPERFRAMES_FFMPEG_PATH=%FFBIN%\ffmpeg.exe"

REM 找 chrome-headless-shell
set "CHROME="
for /f "delims=" %%f in ('dir /s /b "%RT%\chrome-headless-shell\*chrome-headless-shell.exe" 2^>nul') do set "CHROME=%%f"
if "%CHROME%"=="" (
  echo [FATAL] 找不到 chrome-headless-shell（%RT%\chrome-headless-shell\...）
  echo   请重跑 install.bat 完成浏览器下载。
  pause & exit /b 1
)
set "HYPERFRAMES_BROWSER_PATH=%CHROME%"
set "PRODUCER_LOW_MEMORY_MODE=false"

REM Node + hyperframes CLI
set "NODE=%RT%\bin\node.exe"
if not exist "%NODE%" (set "NODE=node")
set "CLI=%RT%\hyperframes-install\node_modules\hyperframes\dist\cli.js"
if not exist "%CLI%" (
  echo [FATAL] 找不到 hyperframes（%CLI%）
  echo   请检查 install.bat 第⑥步是否装成功（黑窗口有无 WARN 提示）。
  pause & exit /b 1
)

if not exist "index.html" (echo [FAIL] 当前文件夹缺少 index.html，请先双击 prep.bat & pause & exit /b 1)
if not exist "src_fixed.mp4" (echo [FAIL] 缺少 src_fixed.mp4（音频兜底用）& pause & exit /b 1)

echo === render start ===
"%NODE%" "%CLI%" render -o out.mp4
set RENDER_EXIT=%errorlevel%
echo RENDER_EXIT=%RENDER_EXIT%

REM ---------- 兜底 1：out.mp4 无视频流 / 渲染非 0 -> 从 video-only.mp4 恢复 ----------
set "HASV="
for /f "tokens=*" %%a in ('"%FFBIN%\ffprobe.exe" -v error -select_streams v:0 -show_entries stream=codec_type -of csv=p=0 out.mp4 2^>nul') do set "HASV=%%a"
if "%HASV%"=="" (
  echo [兜底] out.mp4 无视频流(exit=%RENDER_EXIT%)，尝试从 video-only.mp4 恢复
  set "VID="
  for /f "delims=" %%d in ('dir /b /ad /o-d work-* 2^>nul') do (
    if not defined VID if exist "%%d\video-only.mp4" set "VID=%%d\video-only.mp4"
  )
  if "%VID%"=="" (echo [FATAL] 找不到 video-only.mp4，无法兜底 & pause & exit /b 1)
  echo [兜底] 用 %VID% + src_fixed.mp4 原声 -> out.mp4
  "%FFBIN%\ffmpeg.exe" -y -i "%VID%" -i src_fixed.mp4 -map 0:v:0 -map 1:a:0 -c:v copy -c:a copy -movflags +faststart -shortest out.mp4
)

REM ---------- 兜底 2：out.mp4 仍缺音轨 -> 从 src_fixed.mp4 混回原声 ----------
set "HASA="
for /f "tokens=*" %%a in ('"%FFBIN%\ffprobe.exe" -v error -select_streams a -show_entries stream=index -of csv=p=0 out.mp4 2^>nul') do set "HASA=%%a"
if "%HASA%"=="" (
  echo [兜底] out.mp4 无音轨，从 src_fixed.mp4 混回
  "%FFBIN%\ffmpeg.exe" -y -i out.mp4 -i src_fixed.mp4 -map 0:v:0 -map 1:a:0 -c:v copy -c:a copy -shortest final_mux.mp4
  if exist "final_mux.mp4" (move /Y final_mux.mp4 out.mp4 >nul & echo [兜底] 已混回原声)
) else (
  echo audio already present, keep as-is
)

echo === final verify ===
"%FFBIN%\ffprobe.exe" -v error -show_entries format=duration:stream=index,codec_type,codec_name,width,height,r_frame_rate -of default=noprint_wrappers=1 out.mp4
echo === DONE ===
if exist "out.mp4" (echo ✅ 成片已生成：out.mp4) else (echo [FATAL] out.mp4 未生成)
pause
