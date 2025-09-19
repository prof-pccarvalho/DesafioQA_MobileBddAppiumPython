#!/usr/bin/env python3
"""
<summary>
Step definitions do fluxo de Login integrando:
- checagem do ambiente Android (ANDROID_SDK_ROOT/ANDROID_HOME e adb no PATH),
- detecção automática do endpoint Appium (/status ou /wd/hub/status),
- uso da API de Options (UiAutomator2Options) quando disponível,
- fallback para desired_capabilities quando Options não estiverem disponíveis.
As steps expostas:
  - step_open_app (Given)
  - step_enter_credentials (When)
  - step_click_login (When)
  - step_verify_home_screen (Then)
</summary>
"""
from typing import Tuple, Dict, Optional
import os
import sys
import shutil
import subprocess
import requests  # usado para detectar /status no servidor Appium
from behave import given, when, then

# Appium / Selenium imports
from appium import webdriver
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Tenta importar Options modernos do client Appium (UiAutomator2Options).
# Se não existir, faremos fallback para desired_capabilities.
try:
    from appium.options.android import UiAutomator2Options  # type: ignore
    _HAS_UIAUTOMATOR2_OPTIONS = True
except Exception:
    UiAutomator2Options = None  # type: ignore
    _HAS_UIAUTOMATOR2_OPTIONS = False

# Registrar este módulo no sys.modules com o nome utilizado nos testes:
# muitos testes usam @patch("features.steps.login_steps.X") e, quando o módulo
# é carregado dinamicamente via importlib, precisamos garantir que sys.modules
# contenha esta chave apontando para o objeto módulo atual. Usamos __name__ para
# obter o nome atual do módulo. Esta linha evita KeyError em testes.
#sys.modules.setdefault("features.steps.login_steps", sys.modules[__name__])
sys.modules.setdefault("features.steps.login_steps", sys.modules[__name__]) 
sys.modules.setdefault("login_steps_mod", sys.modules[__name__])

def check_android_environment() -> Tuple[bool, Dict[str, str]]:
    """
    <summary>
    Verifica se o ambiente Android está adequadamente configurado para permitir que o Appium
    use adb e outras ferramentas do SDK.
    </summary>
    <returns>
      Tuple[bool, Dict[str, str]>:
        - bool: True se o ambiente parece OK (variáveis e adb disponíveis), False caso contrário.
        - Dict[str, str]: informações diagnósticas: android_sdk_root, android_home, adb_path, adb_version, notes
    </returns>
    """
    info = {
        "android_sdk_root": os.environ.get("ANDROID_SDK_ROOT", ""),
        "android_home": os.environ.get("ANDROID_HOME", ""),
        "adb_path": "",
        "adb_version": "",
        "notes": "",
    }

    # Preferência: ANDROID_SDK_ROOT então ANDROID_HOME
    sdk_root = info["android_sdk_root"] or info["android_home"]
    if not sdk_root:
        info["notes"] += "Nenhuma variável ANDROID_SDK_ROOT/ANDROID_HOME definida. "
    else:
        # Verifica se a pasta existe
        if not os.path.isdir(sdk_root):
            info["notes"] += f"ANDROID SDK path '{sdk_root}' não existe. "
        else:
            info["notes"] += f"ANDROID SDK encontrado em {sdk_root}. "

    # Verifica se 'adb' está no PATH
    adb_exec = shutil.which("adb")
    if adb_exec:
        info["adb_path"] = adb_exec
        try:
            # Tenta executar 'adb version' para obter versão
            completed = subprocess.run([adb_exec, "version"], capture_output=True, text=True, timeout=5)
            info["adb_version"] = completed.stdout.strip().splitlines()[0] if completed.stdout else ""
            info["notes"] += "adb encontrado. "
        except Exception as ex:
            info["notes"] += f"Erro ao executar 'adb version': {ex}. "
    else:
        info["notes"] += "adb não encontrado no PATH. "

    ok = bool(sdk_root and os.path.isdir(sdk_root) and adb_exec)
    return ok, info


def _detect_appium_endpoint(base_url: str, timeout: float = 2.0) -> str:
    """
    <summary>
    Detecta automaticamente a base URL do Appium que responde ao endpoint /status.
    Primeira tentativa: base_url (ex: http://localhost:4723) -> /status (Appium v2 padrão).
    Segunda tentativa: base_url + /wd/hub -> /wd/hub/status (compatibilidade).
    </summary>
    <param name="base_url">URL base informada (ex: http://localhost:4723)</param>
    <param name="timeout">Timeout em segundos por tentativa HTTP</param>
    <returns>Endpoint válido a usar como command_executor</returns>
    """
    base = base_url.rstrip("/")
    candidates = [f"{base}", f"{base}/wd/hub"]

    for candidate in candidates:
        try:
            status_url = f"{candidate}/status"
            resp = requests.get(status_url, timeout=timeout)
            if resp.status_code == 200:
                # Retorna o candidate que respondeu com 200
                return candidate
        except Exception:
            # Ignora e tenta próximo candidate
            continue

    # Se nenhum respondeu, retorna base original (quem chamar terá o erro para diagnosticar)
    return base


@given('que o app está aberto na tela de login')
def step_open_app(context):
    """
    <summary>
    Step Given que inicializa a sessão Appium e injeta context.login_page.
    Faz checagem do ambiente Android, detecta endpoint Appium e usa Options/fallback.
    Permite override das capabilities via variáveis de ambiente:
      - APPIUM_SERVER: URL do servidor Appium (ex: http://localhost:4723)
      - DEVICE_NAME: nome do emulador/device (ex: emulator-5554)
      - APP_PATH: caminho para o APK (padrão: resources/mda-2.2.0-25.apk)
      - LAUNCH_PACKAGE: (opcional) package a usar explicitamente
      - LAUNCH_ACTIVITY: (opcional) activity a usar explicitamente
    </summary>
    <param name="context">Contexto do Behave que receberá context.driver e context.login_page</param>
    <returns>None</returns>
    """
    # Lê variáveis de ambiente para parametrização
    appium_base = os.environ.get("APPIUM_SERVER", "http://localhost:4723")
    device_name = os.environ.get("DEVICE_NAME", "emulator-5554")
    app_path = os.environ.get("APP_PATH", os.path.join("resources", "mda-2.2.0-25.apk"))
    launch_pkg = os.environ.get("LAUNCH_PACKAGE")
    launch_activity = os.environ.get("LAUNCH_ACTIVITY")

    # 1) Checa o ambiente Android e aborta cedo se inválido
    ok, info = check_android_environment()
    if not ok:
        # Mensagem clara para o usuário / logs de CI
        raise RuntimeError(f"Android environment problem: {info['notes']}")

    # 2) Detecta qual base path do Appium usar (sem /wd/hub ou com /wd/hub)
    command_executor = _detect_appium_endpoint(appium_base)

    # 3) Monta capabilities básicas (não forçamos appPackage/appActivity por padrão)
    desired_caps = {
        "platformName": "Android",
        "deviceName": device_name,
        "app": app_path,
        "automationName": "UiAutomator2",
    }

    # Se o usuário forneceu package/activity via variáveis de ambiente, inclui nas caps
    if launch_pkg:
        desired_caps["appPackage"] = launch_pkg
    if launch_activity:
        desired_caps["appActivity"] = launch_activity
        # appWaitActivity com wildcard ajuda a tolerar atividades diferentes
        desired_caps["appWaitActivity"] = f"{launch_activity},*"

    # 4) Inicializa driver com Options quando disponível; caso contrário usa desired_capabilities
    if _HAS_UIAUTOMATOR2_OPTIONS:
        # Cria e popula o objeto options compatível com Appium client moderno
        opts = UiAutomator2Options()
        opts.platform_name = desired_caps["platformName"]
        opts.device_name = desired_caps["deviceName"]
        opts.app = desired_caps["app"]
        # Se appPackage/appActivity estiverem presentes, transfere para options via set_capability
        if "appPackage" in desired_caps:
            opts.set_capability("appPackage", desired_caps["appPackage"])
        if "appActivity" in desired_caps:
            opts.set_capability("appActivity", desired_caps["appActivity"])
            opts.set_capability("appWaitActivity", desired_caps.get("appWaitActivity", ""))

        # Inicializa o driver no Appium. Usamos keyword command_executor e options explicitamente.
        context.driver = webdriver.Remote(command_executor=command_executor, options=opts)
    else:
        # Fallback para clients/versões legadas: passam desired_capabilities como kwarg
        context.driver = webdriver.Remote(command_executor=command_executor, desired_capabilities=desired_caps)

    # 5) Instancia o Page Object de login e injeta no contexto
    from pages.login_page import LoginPage  # import local para evitar problemas de import circular em testes
    context.login_page = LoginPage(context.driver)


@when('eu digito o usuário "{usuario}" e a senha "{senha}"')
def step_enter_credentials(context, usuario: str, senha: str):
    """
    <summary>
    Step que insere usuário e senha na tela de login usando o Page Object.
    </summary>
    <param name="context">Contexto do Behave (deve conter context.login_page)</param>
    <param name="usuario">Nome do usuário a ser digitado</param>
    <param name="senha">Senha a ser digitada</param>
    <returns>None</returns>
    """
    # Delega para os métodos do Page Object (mantendo steps finas)
    context.login_page.enter_username(usuario)
    context.login_page.enter_password(senha)


@when('clico no botão de login')
def step_click_login(context):
    """
    <summary>
    Step que aciona o botão de login através do Page Object.
    </summary>
    <param name="context">Contexto do Behave</param>
    <returns>None</returns>
    """
    context.login_page.tap_login()


@then('devo ver a tela inicial do app')
def step_verify_home_screen(context, timeout: Optional[int] = None):
    """
    <summary>
    Step que valida a presença de um elemento característico da tela inicial.
    Usa espera explícita (WebDriverWait) para reduzir flakiness.
    </summary>
    <param name="context">Contexto do Behave com context.driver</param>
    <param name="timeout">Timeout em segundos para aguardar o elemento da home (opcional)</param>
    <returns>None</returns>
    """
    # Locator da tela inicial — ajuste se necessário
    home_locator = (AppiumBy.ACCESSIBILITY_ID, "open menu")
    wait_seconds = int(os.environ.get("HOME_WAIT_SECONDS", "10")) if timeout is None else timeout

    # Usa WebDriverWait para aguardar visibilidade do elemento representativo da home
    WebDriverWait(context.driver, wait_seconds).until(EC.visibility_of_element_located(home_locator))
