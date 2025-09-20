#!/usr/bin/env python3
"""
<summary>
Step definitions do fluxo de Login:
- Inicializa sessão Appium (detecta endpoint /status vs /wd/hub/status)
- Usa UiAutomator2Options quando disponível, com fallback para desired_capabilities
- Integra checagem prévia do ambiente Android para evitar falhas silenciosas
</summary>
"""
from typing import Tuple, Dict, Optional
import os
import requests
from behave import given, when, then

from appium import webdriver
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC

# Import opcional: UiAutomator2Options quando disponível
try:
    from appium.options.android import UiAutomator2Options  # type: ignore
    _HAS_UIAUTOMATOR2_OPTIONS = True
except Exception:
    UiAutomator2Options = None  # type: ignore
    _HAS_UIAUTOMATOR2_OPTIONS = False

# importar utilitário de checagem (criado em D)
from features.steps.android_env_check import check_android_environment  # type: ignore

# Registrar alias em sys.modules foi resolvido em testes via utilitário load_module,
# portanto não fazemos sys.modules manipulations aqui — mantemos o código limpo.

def wait_for_any_locator(driver, locators, timeout: int):
    """
    <summary>
    Aguarda que qualquer um dos locators fornecidos fique visível dentro do timeout.
    Tenta os locators sequencialmente: para cada locator executa WebDriverWait(...).until(EC.visibility_of_element_located(locator)).
    Retorna o locator que foi encontrado e o elemento retornado pela espera.
    </summary>
    <param name="driver">Instância do WebDriver/Appium</param>
    <param name="locators">Lista de tuplas (By, locator_string) a serem testadas</param>
    <param name="timeout">Timeout em segundos para cada tentativa</param>
    <returns>Tuple(locator, element) onde locator é a tupla que teve sucesso e element é o WebElement</returns>
    <raises>TimeoutException se nenhum dos locators estiver visível no tempo</raises>
    """
    # Itera sobre os locators e tenta aguardar cada um ser visível.
    for locator in locators:
        try:
            # Usa WebDriverWait com expected_conditions para validar visibilidade.
            elem = WebDriverWait(driver, timeout).until(EC.visibility_of_element_located(locator))
            # Se chegou aqui sem exceção, retornamos o locator bem-sucedido e o elemento
            return locator, elem
        except TimeoutException:
            # Caso o locator atual não tenha sido encontrado, passamos para o próximo.
            continue

    # Se terminou o loop sem encontrar nenhum locator, levantamos TimeoutException.
    raise TimeoutException(f"Nenhum locator visível dentre os candidatos: {locators}")



def _detect_appium_endpoint(base_url: str, timeout: float = 2.0) -> str:
    """
    <summary>
    Detecta qual base path do Appium responde ao endpoint /status.
    </summary>
    <param name="base_url">URL base do servidor Appium</param>
    <param name="timeout">Timeout para a checagem</param>
    <returns>Endpoint válido para usar como command_executor</returns>
    """
    base = base_url.rstrip("/")
    candidates = [f"{base}", f"{base}/wd/hub"]
    for candidate in candidates:
        try:
            status_url = f"{candidate}/status"
            resp = requests.get(status_url, timeout=timeout)
            if resp.status_code == 200:
                return candidate
        except Exception:
            continue
    return base


@given('que o app está aberto na tela de login')
def step_open_app(context):
    """
    <summary>
    Inicializa sessão Appium e coloca o Page Object de login no context.
    Lança RuntimeError se a checagem do ambiente Android falhar.
    </summary>
    <param name="context">Context do Behave</param>
    <returns>None</returns>
    """
    appium_base = os.environ.get("APPIUM_SERVER", "http://localhost:4723")
    device_name = os.environ.get("DEVICE_NAME", "emulator-5554")
    app_path = os.environ.get("APP_PATH", os.path.join("resources", "mda-2.2.0-25.apk"))
    launch_pkg = os.environ.get("LAUNCH_PACKAGE")
    launch_activity = os.environ.get("LAUNCH_ACTIVITY")

    # 1) Checagem do ambiente Android para evitar falhas posteriores
    ok, info = check_android_environment()
    if not ok:
        raise RuntimeError(f"Android environment problem: {info['notes']}")

    # 2) Detectar endpoint Appium (com/sem /wd/hub)
    command_executor = _detect_appium_endpoint(appium_base)

    # 3) Montar capabilities básicas
    desired_caps = {
        "platformName": "Android",
        "deviceName": device_name,
        "app": app_path,
        "automationName": "UiAutomator2",
    }
    if launch_pkg:
        desired_caps["appPackage"] = launch_pkg
    if launch_activity:
        desired_caps["appActivity"] = launch_activity
        desired_caps["appWaitActivity"] = f"{launch_activity},*"

    # 4) Inicializar driver: preferir Options quando disponível
    if _HAS_UIAUTOMATOR2_OPTIONS:
        opts = UiAutomator2Options()
        opts.platform_name = desired_caps["platformName"]
        opts.device_name = desired_caps["deviceName"]
        opts.app = desired_caps["app"]
        if "appPackage" in desired_caps:
            opts.set_capability("appPackage", desired_caps["appPackage"])
        if "appActivity" in desired_caps:
            opts.set_capability("appActivity", desired_caps["appActivity"])
            opts.set_capability("appWaitActivity", desired_caps.get("appWaitActivity", ""))
        context.driver = webdriver.Remote(command_executor=command_executor, options=opts)
    else:
        context.driver = webdriver.Remote(command_executor=command_executor, desired_capabilities=desired_caps)

    # 5) Instanciar Page Object
    from pages.login_page import LoginPage  # import local
    context.login_page = LoginPage(context.driver)


@when('eu digito o usuário "{usuario}" e a senha "{senha}"')
def step_enter_credentials(context, usuario, senha):
    """
    <summary>
    Insere credenciais nos campos de login. Primeiro tenta digitar diretamente
    (caso a tela de login já esteja visível). Se ocorrer TimeoutException ao
    localizar o campo (p.ex. o app abriu em outra tela), navega pelo menu até
    a opção "Log In" e então preenche os campos sem acionar o botão de login.
    Isso mantém os testes unitários determinísticos (quando enter_username não
    lança) e permite execução real via Behave quando é necessário navegar.
    </summary>
    <param name="context">Contexto do Behave com context.login_page</param>
    <param name="usuario">String com o usuário</param>
    <param name="senha">String com a senha</param>
    <returns>None</returns>
    """
    # Tentativa otimista: preencher diretamente. Em testes unitários com Mock esta
    # chamada normalmente não levantará exceção e os asserts esperados permanecerão.
    try:
        context.login_page.enter_username(usuario)
        context.login_page.enter_password(senha)
        # Observação: não acionamos o login aqui; o passo de clique é separado
        return
    except TimeoutException:
        # Caso o campo não exista (ex.: app abriu em outra tela), fazemos a navegação:
        # 1) abrir menu
        # 2) abrir o item "Log In" no menu
        # 3) preencher username e password (não clicar em login)
        try:
            # open_menu e open_login_from_menu são primitives do Page Object
            context.login_page.open_menu()
            context.login_page.open_login_from_menu()
            context.login_page.enter_username(usuario)
            context.login_page.enter_password(senha)
        except Exception as exc:
            # relança exceção para que o Behave registre o erro original (útil para debugging)
            raise



@when('clico no botão de login')
def step_click_login(context):
    """
    <summary>
    Usa o Page Object para acionar o botão de login.
    </summary>
    """
    context.login_page.tap_login()


@then('devo ver a tela inicial do app')
def step_verify_home_screen(context):
    """
    <summary>
    Aguarda um elemento representativo da tela inicial do app.
    Tenta múltiplos locators plausíveis (acessibility id do menu e id dos elementos da tela de produtos).
    Em caso de falha captura artifacts para diagnóstico e relança TimeoutException com contexto.
    </summary>
    <param name="context">Contexto do Behave com context.driver e context.login_page (quando disponível)</param>
    <returns>None</returns>
    <raises>TimeoutException se nenhum dos locators for encontrado</raises>
    """
    # Lista de locators candidatos que representam a "tela inicial" após login.
    # Ordene do mais específico ao mais genérico. Ajuste conforme sua versão do app.
    locators_to_try = [
        # 1) botão "open menu" usado em algumas versões (accessibility id)
        (AppiumBy.ACCESSIBILITY_ID, "open menu"),
        # 2) elemento de produto exibido na tela de produtos (id conhecido na sua build)
        (AppiumBy.ID, "com.saucelabs.mydemoapp.android:id/productTV"),
        # 3) lista de produtos (se existir)
        (AppiumBy.ID, "com.saucelabs.mydemoapp.android:id/productList"),
    ]

    # Timeout por tentativa (em segundos) - permita configurar via env var
    per_locator_timeout = int(os.environ.get("HOME_WAIT_SECONDS", "10"))

    try:
        # Tenta qualquer dos locators; se algum for encontrado retorna imediatamente
        found_locator, element = wait_for_any_locator(context.driver, locators_to_try, per_locator_timeout)
        # Se desejarmos podemos logar qual locator obteve sucesso (útil para debugging)
        # Ex.: logger.debug(f"Home screen detected by locator {found_locator}")
        return
    except TimeoutException as exc:
        # Ao falhar, captura artifacts para diagnóstico, se possível usando o Page Object
        try:
            # Se o context.login_page implementa _capture_debug_artifacts, use-o (tem screenshots + page_source)
            if hasattr(context, "login_page") and hasattr(context.login_page, "_capture_debug_artifacts"):
                context.login_page._capture_debug_artifacts(prefix="verify_home_screen_timeout")
            else:
                # Caso não exista login_page/no capture helper, tente um screenshot direto (silencioso)
                try:
                    context.driver.get_screenshot_as_file(os.path.join(os.getcwd(), "artifacts", "verify_home_screen_timeout.png"))
                except Exception:
                    pass
        except Exception:
            # Não deixe a captura de artifacts mascarar a falha original
            pass

        # Re-lança TimeoutException com mensagem mais informativa (incluindo locators testados)
        raise TimeoutException(f"Não foi possível detectar a tela inicial. Tentados locators: {locators_to_try}") from exc