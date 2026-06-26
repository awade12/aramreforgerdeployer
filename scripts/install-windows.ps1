$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $Root

Write-Host "Reforger Windows bootstrap"

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
  & $Python.Source .\reforger.py init
}

$Config = Get-Content .\deployer.json -Raw | ConvertFrom-Json
$Config.steamcmd = $SteamCmdExe
$Config | ConvertTo-Json -Depth 20 | Set-Content .\deployer.json -Encoding utf8

& $Python.Source .\reforger.py validate
& $Python.Source .\reforger.py render

$BinDir = Join-Path $env:USERPROFILE ".local\bin"
New-Item -ItemType Directory -Force -Path $BinDir | Out-Null
$CmdPath = Join-Path $BinDir "reforger.cmd"
$Cmd = "@echo off`r`n`"$($Python.Source)`" `"$Root\reforger.py`" %*`r`n"
Set-Content -Path $CmdPath -Value $Cmd -Encoding ASCII

$UserPath = [Environment]::GetEnvironmentVariable("Path", "User")
if (-not (($UserPath -split ";") -contains $BinDir)) {
  $NewPath = if ($UserPath) { "$UserPath;$BinDir" } else { $BinDir }
  [Environment]::SetEnvironmentVariable("Path", $NewPath, "User")
  $env:Path = "$env:Path;$BinDir"
  Write-Host "Added $BinDir to your user PATH. Open a new terminal if reforger is not found."
}

Write-Host ""
Write-Host "Next steps:"
Write-Host "  1. Run: reforger setup"
Write-Host "  2. Run: reforger install"
Write-Host "  3. Run one server: reforger start reforger-1"
Write-Host "  4. Show firewall rules: reforger ports"
