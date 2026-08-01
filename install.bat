@echo off
chcp 65001 >nul
title hyperframes.edit v6.4 - 一键安装
echo ============================================================
echo   hyperframes.edit v6.4  富图层·动效剪辑版 - 一键安装
echo   老李出品 | 自动安装所有依赖
echo ============================================================
echo.

set "HF_RUNTIME=%USERPROFILE%\.workbuddy\hyperframes-edit-runtime"
set "HF_ROOT=%~dp0"
set "SKILL_SRC=%HF_ROOT%"
set "SKILL_DST=%USERPROFILE%\.workbuddy\skills\hyperframes-edit"

echo [1/6] 检查 Python...
where python >nul 2>nul
if errorlevel 1 (
    echo   [!] 未找到 Python，正在从微软商店安装...
    echo   请在弹出的窗口点「获取」，装完 Python 后重新运行本脚本。
    start ms-windows-store://pdp/?ProductId=9NRWMJP3717K
    pause
    exit /b 1
)
for /f "tokens=2 delims= " %%v in ('python --version 2^>^&1') do echo   [OK] Python %%v

echo.
echo [2/6] 创建运行时目录...
if not exist "%HF_RUNTIME%" mkdir "%HF_RUNTIME%"
if not exist "%HF_RUNTIME%\bin" mkdir "%HF_RUNTIME%\bin"
if not exist "%HF_RUNTIME%\ffmpeg" mkdir "%HF_RUNTIME%\ffmpeg"

echo.
echo [3/6] 下载 FFmpeg（视频处理引擎）...
if not exist "%HF_RUNTIME%\ffmpeg\bin\ffmpeg.exe" (
    echo   正在下载 ffmpeg (约 90MB)，请耐心等待...
    powershell -Command "& {
        $ProgressPreference = 'SilentlyContinue'
        $url = 'https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip'
        $zip = \"$env:TEMP\\ffmpeg.zip\"
        Invoke-WebRequest -Uri $url -OutFile $zip -UseBasicParsing
        Expand-Archive -Path $zip -DestinationPath \"$env:TEMP\\ffmpeg_extract\" -Force
        $exe = Get-ChildItem -Path \"$env:TEMP\\ffmpeg_extract\" -Recurse -Filter ffmpeg.exe | Select-Object -First 1
        $binDir = \"$env:USERPROFILE\\.workbuddy\\hyperframes-edit-runtime\\ffmpeg\\bin\"
        New-Item -ItemType Directory -Force -Path $binDir | Out-Null
        Copy-Item -Path $exe.FullName -Destination \"$binDir\\ffmpeg.exe\" -Force
        $p = Get-ChildItem -Path \"$env:TEMP\\ffmpeg_extract\" -Recurse -Filter ffprobe.exe | Select-Object -First 1
        Copy-Item -Path $p.FullName -Destination \"$binDir\\ffprobe.exe\" -Force
    }"
    if exist "%HF_RUNTIME%\ffmpeg\bin\ffmpeg.exe" (
        echo   [OK] FFmpeg 安装完成
    ) else (
        echo   [FAIL] FFmpeg 下载失败，请检查网络或手动下载
        echo   手动下载: https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip
        pause
        exit /b 1
    )
) else (
    echo   [OK] FFmpeg 已存在
)

echo.
echo [4/6] 下载 Node.js（渲染引擎运行环境）...
if not exist "%HF_RUNTIME%\bin\node.exe" (
    echo   正在下载 Node.js LTS (约 30MB)...
    powershell -Command "& {
        $ProgressPreference = 'SilentlyContinue'
        $url = 'https://nodejs.org/dist/v22.13.1/node-v22.13.1-win-x64.zip'
        $zip = \"$env:TEMP\node.zip\"
        Invoke-WebRequest -Uri $url -OutFile $zip -UseBasicParsing
        Expand-Archive -Path $zip -DestinationPath \"$env:TEMP\node_extract\" -Force
        # 复制整个 node 发行目录（含 node.exe + npm + node_modules）到 bin\
        $srcDir = Get-ChildItem -Path \"$env:TEMP\node_extract\" -Directory | Where-Object { $_.Name -match '^node-v' } | Select-Object -First 1
        $binDir = \"$env:USERPROFILE\.workbuddy\hyperframes-edit-runtime\bin\"
        New-Item -ItemType Directory -Force -Path $binDir | Out-Null
        Copy-Item -Path \"$($srcDir.FullName)\*\" -Destination $binDir -Recurse -Force
    }"
    if exist "%HF_RUNTIME%\bin\node.exe" (
        echo   [OK] Node.js 安装完成
    ) else (
        echo   [FAIL] Node.js 下载失败，请检查网络
        pause
        exit /b 1
    )
) else (
    echo   [OK] Node.js 已存在
)

echo.
echo [5/6] 下载 Chrome 无头浏览器（渲染用）...
if not exist "%HF_RUNTIME%\chrome-headless-shell\" (
    echo   正在下载 Chrome Headless Shell (约 120MB)，请耐心等待...
    powershell -Command "& {
        $ProgressPreference = 'SilentlyContinue'
        $url = 'https://storage.googleapis.com/chrome-for-testing-public/last-known-good-versions-with-downloads.json'
        $json = (Invoke-WebRequest -Uri $url -UseBasicParsing).Content | ConvertFrom-Json
        $dl = $json.channels.Stable.downloads.'chrome-headless-shell' | Where-Object { $_.platform -eq 'win64' }
        $zip = \"$env:TEMP\\chrome-headless.zip\"
        Invoke-WebRequest -Uri $dl.url -OutFile $zip -UseBasicParsing
        Expand-Archive -Path $zip -DestinationPath \"$env:USERPROFILE\\.workbuddy\\hyperframes-edit-runtime\" -Force
    }"
    if exist "%HF_RUNTIME%\chrome-headless-shell\" (
        echo   [OK] Chrome Headless 安装完成
    ) else (
        echo   [FAIL] Chrome Headless 下载失败，请检查网络
        pause
        exit /b 1
    )
) else (
    echo   [OK] Chrome Headless 已存在
)

echo.
echo [6/6] 安装 hyperframes CLI 和技能文件...
if not exist "%HF_RUNTIME%\hyperframes-install\node_modules\hyperframes\dist\cli.js" (
    echo   正在下载 hyperframes 渲染引擎...
    if exist "%HF_RUNTIME%\bin\node_modules\npm\bin\npm-cli.js" (
        "%HF_RUNTIME%\bin\node.exe" "%HF_RUNTIME%\bin\node_modules\npm\bin\npm-cli.js" install --prefix "%HF_RUNTIME%\hyperframes-install" hyperframes 2>nul
    )
    if not exist "%HF_RUNTIME%\hyperframes-install\node_modules\hyperframes\dist\cli.js" (
        echo   尝试备用方式下载 hyperframes...
        powershell -Command "& {
            $ProgressPreference = 'SilentlyContinue'
            $url = 'https://registry.npmjs.org/hyperframes/-/hyperframes-latest.tgz'
            $tgz = \"$env:TEMP\hyperframes.tgz\"
            Invoke-WebRequest -Uri $url -OutFile $tgz -UseBasicParsing
            New-Item -ItemType Directory -Force -Path \"$env:USERPROFILE\.workbuddy\hyperframes-edit-runtime\hyperframes-install\" | Out-Null
            Copy-Item $tgz \"$env:USERPROFILE\.workbuddy\hyperframes-edit-runtime\hyperframes-install\package.tgz\"
        }"
        echo   [WARN] hyperframes 需手动安装：进入 hyperframes-install 目录运行 npm install
    )
    if exist "%HF_RUNTIME%\hyperframes-install\node_modules\hyperframes\dist\cli.js" (
        echo   [OK] hyperframes 渲染引擎安装完成
    ) else (
        echo   [WARN] hyperframes 未自动安装完成，请稍后手动处理
    )
)

echo.
echo 复制技能文件到 WorkBuddy 目录...
if not exist "%SKILL_DST%" mkdir "%SKILL_DST%"
xcopy /E /I /Y "%SKILL_SRC%scripts" "%SKILL_DST%\scripts\" >nul 2>&1
xcopy /E /I /Y "%SKILL_SRC%assets" "%SKILL_DST%\assets\" >nul 2>&1
xcopy /E /I /Y "%SKILL_SRC%references" "%SKILL_DST%\references\" >nul 2>&1
copy /Y "%SKILL_SRC%SKILL.md" "%SKILL_DST%\SKILL.md" >nul 2>&1

echo.
echo 设置环境变量（HF_RUNTIME）...
setx HF_RUNTIME "%HF_RUNTIME%" >nul 2>&1

echo.
echo ============================================================
echo   ✅ 安装完成！
echo.
echo   运行时位置: %HF_RUNTIME%
echo   技能位置:   %SKILL_DST%
echo.
echo   下一步：
echo   1. 打开 老李的教学视频/教程 看用法
echo   2. 新建一个文件夹，放入你的口播视频 src.mp4 和口播稿
echo   3. 复制 scripts/beats.example.json 为 beats.json 改内容
echo   4. 按教程运行 render 命令
echo ============================================================
pause
