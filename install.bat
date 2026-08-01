@echo off
title hyperframes.edit v6.4 - 一键安装
echo ============================================================
echo   hyperframes.edit v6.4  ^| 一键安装
echo   老李出品 ^| 自动安装所有依赖
echo ============================================================
echo.

set "HF_RUNTIME=%USERPROFILE%\.workbuddy\hyperframes-edit-runtime"
set "HF_ROOT=%~dp0"
set "SKILL_DST=%USERPROFILE%\.workbuddy\skills\hyperframes-edit"

echo [1/6] 检查 Python...
where python >nul 2>nul
if errorlevel 1 (
    echo   [!] 未找到 Python，请到微软商店搜索 Python 安装，然后重跑本脚本。
    start ms-windows-store://pdp/?ProductId=9NRWMJP3717K
    pause
    exit /b 1
)
for /f "tokens=2 delims= " %%v in ('python --version 2^>^&1') do echo   [OK] Python %%v

echo.
echo [2/6] 创建运行时目录...
if not exist "%HF_RUNTIME%" mkdir "%HF_RUNTIME%"

echo.
echo [3/6] 下载 FFmpeg...
powershell -NoProfile -ExecutionPolicy Bypass -File "%HF_ROOT%scripts\install_ffmpeg.ps1"
if exist "%HF_RUNTIME%\ffmpeg\bin\ffmpeg.exe" (
    echo   [OK] FFmpeg 已就绪
) else (
    echo   [FAIL] FFmpeg 安装失败，请检查网络后重试。
    pause
    exit /b 1
)

echo.
echo [4/6] 下载 Node.js...
powershell -NoProfile -ExecutionPolicy Bypass -File "%HF_ROOT%scripts\install_node.ps1"
if exist "%HF_RUNTIME%\bin\node.exe" (
    echo   [OK] Node.js 已就绪
) else (
    echo   [FAIL] Node.js 安装失败，请检查网络后重试。
    pause
    exit /b 1
)

echo.
echo [5/6] 下载 Chrome 无头浏览器...
powershell -NoProfile -ExecutionPolicy Bypass -File "%HF_ROOT%scripts\install_chrome.ps1"
if exist "%HF_RUNTIME%\chrome-headless-shell\" (
    echo   [OK] Chrome Headless 已就绪
) else (
    echo   [FAIL] Chrome Headless 安装失败，请检查网络后重试。
    pause
    exit /b 1
)

echo.
echo [6/6] 安装 hyperframes 渲染引擎...
powershell -NoProfile -ExecutionPolicy Bypass -File "%HF_ROOT%scripts\install_hyperframes.ps1"
if exist "%HF_RUNTIME%\hyperframes-install\node_modules\hyperframes\dist\cli.js" (
    echo   [OK] hyperframes 渲染引擎已就绪
) else (
    echo   [WARN] hyperframes 未自动装好，详见上方提示。
)

echo.
echo 复制技能文件到 WorkBuddy 目录...
if not exist "%SKILL_DST%" mkdir "%SKILL_DST%"
xcopy /E /I /Y "%HF_ROOT%scripts" "%SKILL_DST%\scripts\" >nul 2>&1
xcopy /E /I /Y "%HF_ROOT%assets" "%SKILL_DST%\assets\" >nul 2>&1
xcopy /E /I /Y "%HF_ROOT%references" "%SKILL_DST%\references\" >nul 2>&1
copy /Y "%HF_ROOT%SKILL.md" "%SKILL_DST%\SKILL.md" >nul 2>&1

echo.
echo 设置环境变量 HF_RUNTIME...
setx HF_RUNTIME "%HF_RUNTIME%" >nul 2>&1

echo.
echo ============================================================
echo   安装完成！
echo.
echo   运行时位置: %HF_RUNTIME%
echo   技能位置:   %SKILL_DST%
echo.
echo   下一步：看 README.md 或教学视频，照着用。
echo ============================================================
pause
