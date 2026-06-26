$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $Root

Write-Host "ARDR Windows bootstrap"

$Python = Get-Command py -ErrorAction SilentlyContinue
if (-not $Python) {
  $Python = Get-Command python -ErrorAction SilentlyContinue
}
if (-not $Python) {
  throw "Python is required. Install Python 3 from https://www.python.org/downloads/windows/ and rerun this script."
}

$ToolsDir = Join-Path $Root "tools"
$SteamCmdDir = Join-Path $ToolsDir "steamcmd"
$SteamCmdExe = Join-Path $SteamCmdDir "steamcmd.exe"

if (-not (Test-Path $SteamCmdExe)) {
  New-Item -ItemType Directory -Force -Path $SteamCmdDir | Out-Null
  $Zip = Join-Path $ToolsDir "steamcmd.zip"
  Write-Host "Downloading SteamCMD..."
  Invoke-WebRequest -Uri "https://steamcdn-a.akamaihd.net/client/installer/steamcmd.zip" -OutFile $Zip
  Expand-Archive -Path $Zip -DestinationPath $SteamCmdDir -Force
  Remove-Item $Zip
}

if (-not (Test-Path (Join-Path $Root "deployer.json"))) {
  & $Python.Source .\ardr.py init
}

$Config = Get-Content .\deployer.json -Raw | ConvertFrom-Json
$Config.steamcmd = $SteamCmdExe
$Config | ConvertTo-Json -Depth 20 | Set-Content .\deployer.json -Encoding utf8

& $Python.Source .\ardr.py validate
& $Python.Source .\ardr.py render

Write-Host ""
Write-Host "Next steps:"
Write-Host "  1. Edit $Root\deployer.json for names, admin password, ports, and scenarios."
Write-Host "  2. Run: py .\ardr.py install"
Write-Host "  3. Run one server: py .\ardr.py start --instance reforger-1"
Write-Host "  4. Show firewall rules: py .\ardr.py ports"

