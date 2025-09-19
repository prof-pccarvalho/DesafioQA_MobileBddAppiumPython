#!/usr/bin/env python3
from typing import Optional, Tuple
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from appium.webdriver.common.appiumby import AppiumBy
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class LoginPage:
    """
    <summary>
    Page Object que representa a tela de Login do aplicativo.
    Encapsula localizadores e ações (inserir usuário/senha, clicar em login,
    verificar botão habilitado e recuperar mensagem de erro).
    </summary>
    <param name="driver">Instância do WebDriver/Appium usada para localizar elementos e executar ações.</param>
    <returns>None</returns>
    """

    # Locators como tuplas (By, value) para fácil manutenção e teste
    USERNAME_FIELD: Tuple[str, str] = (AppiumBy.ACCESSIBILITY_ID, "test-Username")
    PASSWORD_FIELD: Tuple[str, str] = (AppiumBy.ACCESSIBILITY_ID, "test-Password")
    LOGIN_BUTTON: Tuple[str, str] = (AppiumBy.ACCESSIBILITY_ID, "test-LOGIN")
    # Locator opcional para mensagem de erro — ajuste conforme o seu app, ou remova se não existir
    ERROR_MESSAGE: Tuple[str, str] = (AppiumBy.ACCESSIBILITY_ID, "test-Error")

    def __init__(self, driver: WebDriver, default_wait_seconds: int = 10) -> None:
        """
        <summary>
        Inicializa o LoginPage com um driver e um tempo padrão para esperas explícitas.
        </summary>
        <param name="driver">WebDriver/Appium</param>
        <param name="default_wait_seconds">Tempo padrão (em segundos) para WebDriverWait</param>
        <returns>None</returns>
        """
        # Guarda o driver e o timeout padrão como atributos da instância
        self.driver = driver
        self.default_wait_seconds = default_wait_seconds

    def _wait_for_element(self, locator: Tuple[str, str], timeout: Optional[int] = None) -> WebElement:
        """
        <summary>
        Aguarda até que o elemento identificado por 'locator' esteja visível na tela.
        Centraliza a política de espera para reduzir duplicação de código.
        </summary>
        <param name="locator">Tupla (By, value) que identifica o elemento</param>
        <param name="timeout">Tempo máximo (segundos) para esperar; se None usa default_wait_seconds</param>
        <returns>WebElement visível</returns>
        <raises>TimeoutException se o elemento não aparecer no tempo especificado</raises>
        """
        # Define o tempo de espera efetivo
        wait_time = self.default_wait_seconds if timeout is None else timeout
        # Usa WebDriverWait com expected_conditions de visibilidade
        return WebDriverWait(self.driver, wait_time).until(EC.visibility_of_element_located(locator))

    def enter_username(self, username: str) -> None:
        """
        <summary>
        Insere o texto do usuário no campo username da tela de login.
        </summary>
        <param name="username">Texto do usuário a ser inserido</param>
        <returns>None</returns>
        """
        # Localiza o campo com espera explícita (reduz flakiness)
        el = self._wait_for_element(self.USERNAME_FIELD)
        # Limpa o campo antes de digitar para evitar concatenação
        el.clear()
        # Insere o username
        el.send_keys(username)

    def enter_password(self, password: str) -> None:
        """
        <summary>
        Insere o texto da senha no campo password da tela de login.
        </summary>
        <param name="password">Texto da senha a ser inserido</param>
        <returns>None</returns>
        """
        # Localiza o campo de senha com espera explícita
        el = self._wait_for_element(self.PASSWORD_FIELD)
        # Limpa o campo
        el.clear()
        # Insere a senha
        el.send_keys(password)

    def tap_login(self) -> None:
        """
        <summary>
        Clica/toca no botão de login.
        </summary>
        <returns>None</returns>
        """
        # Localiza o botão e clica
        btn = self._wait_for_element(self.LOGIN_BUTTON)
        # Se for necessário aguardar que esteja clicável, considere EC.element_to_be_clickable
        btn.click()

    def login(self, username: str, password: str) -> None:
        """
        <summary>
        Fluxo composto que realiza o login: inserir usuário, inserir senha e clicar em login.
        </summary>
        <param name="username">Username</param>
        <param name="password">Password</param>
        <returns>None</returns>
        """
        # Reuso dos métodos unitários aumenta a testabilidade e legibilidade
        self.enter_username(username)
        self.enter_password(password)
        self.tap_login()

    def is_login_button_enabled(self) -> bool:
        """
        <summary>
        Verifica se o botão de login está habilitado (is_enabled).
        Retorna False se o botão não for encontrado dentro do timeout.
        </summary>
        <returns>True se habilitado; False caso contrário</returns>
        """
        try:
            btn = self._wait_for_element(self.LOGIN_BUTTON)
            return btn.is_enabled()
        except TimeoutException:
            # Retorna False se o botão não aparecer no tempo esperado
            return False

    def get_error_message(self, timeout: int = 3) -> Optional[str]:
        """
        <summary>
        Obtém o texto da mensagem de erro na tela de login, se presente.
        </summary>
        <param name="timeout">Tempo máximo (segundos) para aguardar a mensagem de erro</param>
        <returns>Texto da mensagem sem espaços adjacentes, ou None se não for encontrada</returns>
        """
        try:
            el = self._wait_for_element(self.ERROR_MESSAGE, timeout=timeout)
            # Retorna o texto com strip para remover espaços extras
            return el.text.strip() if el.text is not None else ""
        except TimeoutException:
            # Se não houver mensagem de erro visível, retorna None
            return None
