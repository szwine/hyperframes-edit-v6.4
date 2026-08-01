# install_chrome.ps1 - 下载并安装 Chrome Headless Shell
$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

$rt = Join-Path $env:USERPROFILE ".workbuddy\hyperframes-edit-runtime"
$chromeDir = Join-Path $rt "chrome-headless-shell"

if (Test-Path $chromeDir) {
    Write-Output "CHROME_ALREADY_OK"
    exit 0
}

Write-Output "正在下载 Chrome Headless Shell (约 120MB)，请耐心等待..."
try {
    $jsonUrl = "https://storage.googleapis.com/chrome-for-testing-public/last-known-good-versions-with-downloads.json"
    $json = (Invoke-WebRequest -Uri $jsonUrl -UseBasicParsing).Content | ConvertFrom-Json
    $dl = $json.channels.Stable.downloads."chrome-headless-shell" | Where-Object { $_.platform -eq "win64" }
    if (-not $dl) { throw "找不到 win64 版本下载链接" }

    $zip = Join-Path $env:TEMP "chrome-headless.zip"
    Invoke-WebRequest -Uri $dl.url -OutFile $zip -UseBasicParsing
    Expand-Archive -Path $zip -DestinationPath $rt -Force

    if (-not (Test-Path $chromeDir)) { throw "chrome-headless-shell 解压失败" }
    Remove-Item $zip -Force -ErrorAction SilentlyContinue
    Write-Output "CHROME_OK"
} catch {
    Write-Output "CHROME_FAIL: $($_.Exception.Message)"
    exit 1
}
