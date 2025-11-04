# Download and install PowerShell 7
$url = "https://github.com/PowerShell/PowerShell/releases/download/v7.4.0/PowerShell-7.4.0-win-x64.msi"
$output = "$env:TEMP\PowerShell-7.4.0-win-x64.msi"

Write-Host "Downloading PowerShell 7.4.0..."
Invoke-WebRequest -Uri $url -OutFile $output

Write-Host "Installing PowerShell 7.4.0..."
Start-Process msiexec.exe -ArgumentList "/i `"$output`" /quiet /norestart ADD_EXPLORER_CONTEXT_MENU_OPENPOWERSHELL=1 ADD_FILE_CONTEXT_MENU_RUNPOWERSHELL=1 ENABLE_PSREMOTING=1 REGISTER_MANIFEST=1 USE_MU=1 ENABLE_MU=1" -Wait

Write-Host "PowerShell 7 installation complete!"
Write-Host "You may need to restart your terminal or add it to PATH."
