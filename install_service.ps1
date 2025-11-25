param(
  [string]$Action = 'install'
)

# This script installs or uninstalls the backend as a Windows Service.
# It prefers NSSM (Non-Sucking Service Manager) if available, otherwise uses sc.exe.

$serviceName = 'OriunBackend'
$exePath = Join-Path -Path (Get-Location) -ChildPath 'dist\backend.exe'

function Install-WithNSSM {
  $nssm = 'nssm.exe'
  if (Get-Command $nssm -ErrorAction SilentlyContinue) {
    & $nssm install $serviceName $exePath
    & $nssm set $serviceName AppDirectory (Split-Path $exePath)
    & $nssm set $serviceName Start SERVICE_AUTO_START
    Write-Host "Service $serviceName installed via NSSM"
  } else {
    Write-Host "NSSM not found. Falling back to sc.exe"
    sc.exe create $serviceName binPath= "`"$exePath`"" start= auto
    Write-Host "Service $serviceName created via sc.exe"
  }
}

function Uninstall-Service {
  if (Get-Command nssm.exe -ErrorAction SilentlyContinue) {
    & nssm remove $serviceName confirm
  } else {
    sc.exe delete $serviceName
  }
  Write-Host "Service $serviceName removed"
}

if ($Action -eq 'install') { Install-WithNSSM } elseif ($Action -eq 'uninstall') { Uninstall-Service } else { Write-Host "Unknown action $Action" }
