<#
Install WSL and Ubuntu (run as Administrator).

Usage: Open PowerShell as Administrator and run:
    .\scripts\01-install-wsl.ps1

This script will:
 - enable Developer Mode registry key (recommended for developer tools)
 - install WSL and the Ubuntu distro
 - prompt for reboot if required

Note: enabling Developer Mode modifies the registry; you may prefer to
enable it via Settings -> Privacy & security -> For developers.
#>

function Assert-Administrator {
    $isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
    if (-not $isAdmin) {
        Write-Error "This script must be run as Administrator. Right-click PowerShell and choose 'Run as Administrator'."
        exit 1
    }
}

Assert-Administrator

Write-Host "Enabling Developer Mode (registry key) ..."
try {
    New-Item -Path HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\AppModelUnlock -Force | Out-Null
    New-ItemProperty -Path HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\AppModelUnlock -Name AllowDevelopmentWithoutDevLicense -Value 1 -PropertyType DWord -Force | Out-Null
    Write-Host "Developer Mode registry key set. You may still want to enable it in Settings -> For developers." -ForegroundColor Green
} catch {
    Write-Warning "Could not set Developer Mode registry key: $_"
}

Write-Host "Installing WSL + Ubuntu (this may take a few minutes)..."
try {
    wsl --install -d Ubuntu
    if ($LASTEXITCODE -ne 0) {
        Write-Warning "wsl --install returned exit code $LASTEXITCODE. You may need to enable optional features manually or reboot."
    }
} catch {
    Write-Warning "Error invoking wsl --install: $_"
}

Write-Host "If installation completed, please reboot the machine now and run scripts\02-setup-wsl-packages.ps1 as your regular user." -ForegroundColor Yellow
Write-Host "Press Enter to exit."
Read-Host | Out-Null
