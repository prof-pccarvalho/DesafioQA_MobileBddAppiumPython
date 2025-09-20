

seção "Como rodar localmente (Windows / PowerShell)"

Preparar ambiente Android (PowerShell):

Defina SDK/adb (temporariamente nesta sessão): $env:ANDROID_SDK_ROOT = "C:\Users<seu_usuario>\AppData\Local\Android\Sdk" $env:ANDROID_HOME = $env:ANDROID_SDK_ROOT $env:Path = $env:Path + ";" + "$env:ANDROID_SDK_ROOT\platform-tools"
Verifique: adb version adb devices
Iniciar Appium (em outro terminal): appium (ou appium --base-path /wd/hub se necessário)

Rodar unit tests: py -m pytest -q

Rodar BDD: behave -f pretty