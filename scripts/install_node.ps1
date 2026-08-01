# install_node.ps1 - 下载并安装 Node.js（整个发行目录复制到 bin\）
$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

$binDir = Join-Path $env:USERPROFILE ".workbuddy\hyperframes-edit-runtime\bin"
$nodeExe = Join-Path $binDir "node.exe"

if (Test-Path $nodeExe) {
    Write-Output "NODE_ALREADY_OK"
    exit 0
}

Write-Output "正在下载 Node.js LTS (约 30MB)..."
$url = "https://nodejs.org/dist/v22.13.1/node-v22.13.1-win-x64.zip"
$zip = Join-Path $env:TEMP "node.zip"
$extract = Join-Path $env:TEMP "node_extract"

try {
    Invoke-WebRequest -Uri $url -OutFile $zip -UseBasicParsing
    if (Test-Path $extract) { Remove-Item $extract -Recurse -Force }
    Expand-Archive -Path $zip -DestinationPath $extract -Force

    $srcDir = Get-ChildItem -Path $extract -Directory | Where-Object { $_.Name -match "^node-v" } | Select-Object -First 1
    if (-not $srcDir) { throw "解压后找不到 node 目录" }

    New-Item -ItemType Directory -Force -Path $binDir | Out-Null
    Copy-Item -Path "$($srcDir.FullName)\*" -Destination $binDir -Recurse -Force

    if (-not (Test-Path $nodeExe)) { throw "node.exe 复制失败" }
    Remove-Item $zip -Force -ErrorAction SilentlyContinue
    Remove-Item $extract -Recurse -Force -ErrorAction SilentlyContinue
    Write-Output "NODE_OK"
} catch {
    Write-Output "NODE_FAIL: $($_.Exception.Message)"
    exit 1
}
