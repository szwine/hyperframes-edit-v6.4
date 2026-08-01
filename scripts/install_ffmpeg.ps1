# install_ffmpeg.ps1 - 下载并安装 FFmpeg
$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

$binDir = Join-Path $env:USERPROFILE ".workbuddy\hyperframes-edit-runtime\ffmpeg\bin"
$ffmpegExe = Join-Path $binDir "ffmpeg.exe"
$ffprobeExe = Join-Path $binDir "ffprobe.exe"

if ((Test-Path $ffmpegExe) -and (Test-Path $ffprobeExe)) {
    Write-Output "FFMPEG_ALREADY_OK"
    exit 0
}

Write-Output "正在下载 ffmpeg (约 90MB)，请耐心等待..."
$url = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
$zip = Join-Path $env:TEMP "ffmpeg.zip"
$extract = Join-Path $env:TEMP "ffmpeg_extract"

try {
    Invoke-WebRequest -Uri $url -OutFile $zip -UseBasicParsing
    if (Test-Path $extract) { Remove-Item $extract -Recurse -Force }
    Expand-Archive -Path $zip -DestinationPath $extract -Force

    New-Item -ItemType Directory -Force -Path $binDir | Out-Null
    $exe = Get-ChildItem -Path $extract -Recurse -Filter ffmpeg.exe | Select-Object -First 1
    $probe = Get-ChildItem -Path $extract -Recurse -Filter ffprobe.exe | Select-Object -First 1
    if (-not $exe -or -not $probe) { throw "解压后找不到 ffmpeg/ffprobe" }

    Copy-Item -Path $exe.FullName -Destination $ffmpegExe -Force
    Copy-Item -Path $probe.FullName -Destination $ffprobeExe -Force
    Remove-Item $zip -Force -ErrorAction SilentlyContinue
    Remove-Item $extract -Recurse -Force -ErrorAction SilentlyContinue
    Write-Output "FFMPEG_OK"
} catch {
    Write-Output "FFMPEG_FAIL: $($_.Exception.Message)"
    exit 1
}
