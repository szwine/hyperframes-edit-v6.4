@echo off
title hyperframes.edit v6.4 - “ªº¸∞≤◊∞
echo ============================================================
echo   hyperframes.edit v6.4  ^| “ªº¸∞≤◊∞
echo   ¿œ¿Ó≥ˆ∆∑ ^| ◊‘∂Ø∞≤◊∞À˘”–“¿¿µ
echo ============================================================
echo.

REM ÈªòËÆ§Ë£Ö D ÁõòÔºàÈÅøÂºÄ C ÁõòÁî®Êà∑ÂêçÂê´ÁâπÊÆäÂ≠óÁ¨¶Ë∑ØÂæÑÂ∏¶Êù•ÁöÑÈöêÊÇ£ÔºâÔºõËã•Êú∫Âô®Êó† D ÁõòÂàôÂõûÈÄÄ USERPROFILE
if exist "D:\" (set "HF_RUNTIME=D:\hyperframes-edit-runtime") else (set "HF_RUNTIME=%USERPROFILE%\.workbuddy\hyperframes-edit-runtime")
set "HF_ROOT=%~dp0"
set "SKILL_DST=%USERPROFILE%\.workbuddy\skills\hyperframes-edit"

echo [1/6] ºÏ≤È Python...
where python >nul 2>nul
if errorlevel 1 (
    echo   [!] Œ¥’“µΩ Python£¨«ÎµΩŒ¢»Ì…ÃµÍÀ—À˜ Python ∞≤◊∞£¨»ª∫Û÷ÿ≈‹±æΩ≈±æ°£
    start ms-windows-store://pdp/?ProductId=9NRWMJP3717K
    pause
    exit /b 1
)
for /f "tokens=2 delims= " %%v in ('python --version 2^>^&1') do echo   [OK] Python %%v

echo.
echo [2/6] ¥¥Ω®‘À–– ±ƒø¬º...
if not exist "%HF_RUNTIME%" mkdir "%HF_RUNTIME%"

echo.
echo [3/6] œ¬‘ÿ FFmpeg...
powershell -NoProfile -ExecutionPolicy Bypass -File "%HF_ROOT%scripts\install_ffmpeg.ps1"
if exist "%HF_RUNTIME%\ffmpeg\bin\ffmpeg.exe" (
    echo   [OK] FFmpeg “—æÕ–˜
) else (
    echo   [FAIL] FFmpeg ∞≤◊∞ ß∞‹£¨«ÎºÏ≤ÈÕ¯¬Á∫Û÷ÿ ‘°£
    pause
    exit /b 1
)

echo.
echo [4/6] œ¬‘ÿ Node.js...
powershell -NoProfile -ExecutionPolicy Bypass -File "%HF_ROOT%scripts\install_node.ps1"
if exist "%HF_RUNTIME%\bin\node.exe" (
    echo   [OK] Node.js “—æÕ–˜
) else (
    echo   [FAIL] Node.js ∞≤◊∞ ß∞‹£¨«ÎºÏ≤ÈÕ¯¬Á∫Û÷ÿ ‘°£
    pause
    exit /b 1
)

echo.
echo [5/6] œ¬‘ÿ Chrome ŒﬁÕ∑‰Ø¿¿∆˜...
powershell -NoProfile -ExecutionPolicy Bypass -File "%HF_ROOT%scripts\install_chrome.ps1"
if exist "%HF_RUNTIME%\chrome-headless-shell\" (
    echo   [OK] Chrome Headless “—æÕ–˜
) else (
    echo   [FAIL] Chrome Headless ∞≤◊∞ ß∞‹£¨«ÎºÏ≤ÈÕ¯¬Á∫Û÷ÿ ‘°£
    pause
    exit /b 1
)

echo.
echo [6/6] ∞≤◊∞ hyperframes ‰÷»æ“˝«Ê...
powershell -NoProfile -ExecutionPolicy Bypass -File "%HF_ROOT%scripts\install_hyperframes.ps1"
if exist "%HF_RUNTIME%\hyperframes-install\node_modules\hyperframes\dist\cli.js" (
    echo   [OK] hyperframes ‰÷»æ“˝«Ê“—æÕ–˜
) else (
    echo   [WARN] hyperframes Œ¥◊‘∂Ø◊∞∫√£¨œÍº˚…œ∑ΩÃ· æ°£
)

echo.
echo ∏¥÷∆ººƒ‹Œƒº˛µΩ WorkBuddy ƒø¬º...
if not exist "%SKILL_DST%" mkdir "%SKILL_DST%"
xcopy /E /I /Y "%HF_ROOT%scripts" "%SKILL_DST%\scripts\" >nul 2>&1
xcopy /E /I /Y "%HF_ROOT%assets" "%SKILL_DST%\assets\" >nul 2>&1
xcopy /E /I /Y "%HF_ROOT%references" "%SKILL_DST%\references\" >nul 2>&1
copy /Y "%HF_ROOT%SKILL.md" "%SKILL_DST%\SKILL.md" >nul 2>&1

echo.
echo …Ë÷√ª∑æ≥±‰¡ø HF_RUNTIME...
setx HF_RUNTIME "%HF_RUNTIME%" >nul 2>&1

echo.
echo ============================================================
echo   ∞≤◊∞ÕÍ≥…£°
echo.
echo   ‘À–– ±Œª÷√: %HF_RUNTIME%
echo   ººƒ‹Œª÷√:   %SKILL_DST%
echo.
echo   œ¬“ª≤Ω£∫ø¥ README.md ªÚΩÃ—ß ”∆µ£¨’’◊≈”√°£
echo ============================================================
pause
