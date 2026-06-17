<#
Run this AFTER reboot and after opening your WSL distro for the first time.

Usage (from Windows PowerShell, non-admin):
    .\scripts\02-setup-wsl-packages.ps1

This script will run the necessary apt installs inside the WSL distro (Ubuntu)
and install user Python packages (cython, buildozer).
#>

Write-Host "This script will run package installation commands inside the default WSL distro (Ubuntu)."
Write-Host "Make sure you have opened the Ubuntu app once to complete first-time setup."

try {
    # detect default distro
    $distro = wsl -l -v | Select-String -Pattern "^\s*\S" | ForEach-Object { $_.ToString().Trim() } | Select-Object -First 1
    if (-not $distro) { $distro = 'Ubuntu' }
} catch {
    $distro = 'Ubuntu'
}

Write-Host "Using WSL distro: $distro"

$cmd = @'
set -e
apt update
apt upgrade -y
apt install -y python3 python3-pip python3-venv openjdk-11-jdk git zip unzip zlib1g-dev libncurses5 libncurses5-dev libffi-dev libssl-dev libsqlite3-dev libjpeg-dev build-essential curl
python3 -m pip install --user --upgrade pip
python3 -m pip install --user cython buildozer
echo "export PATH=\$HOME/.local/bin:\$PATH" >> ~/.profile
'@

Write-Host "Running setup inside WSL (this may take a while)..."
wsl -d $distro -- bash -lc $cmd

Write-Host "WSL package setup finished. Ensure ~/.local/bin is on your PATH in WSL (logout/login), then run buildozer inside WSL in the project directory."
Write-Host "Example (inside WSL): cd /mnt/c/Users/gabri/Documents/GitHub/Guns\ and\ boots && ~/.local/bin/buildozer android debug"
