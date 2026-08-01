# install_hyperframes.ps1 - 安装 hyperframes CLI 到 hyperframes-install
$ErrorActionPreference = "Continue"
$ProgressPreference = "SilentlyContinue"

$rt = Join-Path $env:USERPROFILE ".workbuddy\hyperframes-edit-runtime"
$installDir = Join-Path $rt "hyperframes-install"
$cliPath = Join-Path $installDir "node_modules\hyperframes\dist\cli.js"

if (Test-Path $cliPath) {
    Write-Output "HYPERFRAMES_ALREADY_OK"
    exit 0
}

$nodeExe = Join-Path $rt "bin\node.exe"
$npmCli = Join-Path $rt "bin\node_modules\npm\bin\npm-cli.js"

if ((Test-Path $nodeExe) -and (Test-Path $npmCli)) {
    Write-Output "正在安装 hyperframes 渲染引擎..."
    & $nodeExe $npmCli install --prefix $installDir hyperframes 2>&1 | Out-Null
}

if (Test-Path $cliPath) {
    Write-Output "HYPERFRAMES_OK"
    exit 0
}

# 备用：下载 tgz
Write-Output "尝试备用方式下载 hyperframes..."
try {
    $tgz = Join-Path $env:TEMP "hyperframes.tgz"
    Invoke-WebRequest -Uri "https://registry.npmjs.org/hyperframes/-/hyperframes-latest.tgz" -OutFile $tgz -UseBasicParsing
    New-Item -ItemType Directory -Force -Path $installDir | Out-Null
    Copy-Item $tgz (Join-Path $installDir "package.tgz") -Force
    Write-Output "HYPERFRAMES_NEED_MANUAL: 请进入 hyperframes-install 目录运行 npm install"
    exit 1
} catch {
    Write-Output "HYPERFRAMES_FAIL: $($_.Exception.Message)"
    exit 1
}
