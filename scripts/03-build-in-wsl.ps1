<#
Run Buildozer inside WSL and copy resulting APK(s) back to Windows `release\android`.

Usage (from Windows PowerShell):
    .\scripts\03-build-in-wsl.ps1

Requirements:
 - WSL with Ubuntu installed and set up (run scripts/02-setup-wsl-packages.ps1 first)
 - buildozer installed in WSL (~/.local/bin/buildozer)
#>

param(
    [string]$Distro = 'Ubuntu'
)

Write-Host "Running Buildozer inside WSL distro: $Distro"

# Convert current Windows path to WSL path
$winPath = (Get-Location).ProviderPath
$wslPathCmd = "python3 - <<'PY'
import sys, subprocess
print(subprocess.run(['wslpath', '-a', '%CD%'], capture_output=True, text=True).stdout.strip())
PY"

Write-Host "Starting buildozer (may take a long time)..."
wsl -d $Distro -- bash -lc "cd \"$(wslpath '%CD%')\" && export PATH=\$HOME/.local/bin:\$PATH && ~/.local/bin/buildozer android debug"

Write-Host "Copying APK(s) to Windows release\android ..."
if (-not (Test-Path -Path 'release\android')) { New-Item -ItemType Directory -Path 'release\android' | Out-Null }
# Copy any APK from bin/ to release/android
Get-ChildItem -Path .\bin -Filter *.apk -Recurse -ErrorAction SilentlyContinue | ForEach-Object {
    Copy-Item -Path $_.FullName -Destination .\release\android\ -Force
}

Write-Host "Done. Check release\android for APK files."
