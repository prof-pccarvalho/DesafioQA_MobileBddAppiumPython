# PowerShell script para preparar variáveis Android temporárias (sessão atual)
# Uso: Execute no PowerShell: .\scripts\setup_env.ps1
$sdk = "C:\Users\pcbar\AppData\Local\Android\Sdk"
$env:ANDROID_SDK_ROOT = $sdk
$env:ANDROID_HOME = $sdk
$env:Path += ";" + "$sdk\platform-tools" + ";" + "$sdk\emulator" + ";" + "$sdk\tools\bin"
Write-Host "ANDROID_SDK_ROOT set to $sdk"
Write-Host "Executando adb devices..."
& "$sdk\platform-tools\adb.exe" devices
Write-Host "Inicie um AVD no Android Studio ou via emulator CLI se necessário."
