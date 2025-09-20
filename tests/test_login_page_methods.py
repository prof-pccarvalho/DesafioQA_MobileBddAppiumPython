#!/usr/bin/env python3
import pytest
from selenium.common.exceptions import TimeoutException

# importa a classe que implementamos
from pages.login_page import LoginPage


class FakeElement:
    """
    <summary>
    Elemento falso para testes que registra chamadas de clear/send_keys/click.
    </summary>
    </summary>
    """
    def __init__(self):
        self.cleared = False
        self.sent_text = None
        self.clicked = False

    def clear(self):
        # marca que clear foi chamado
        self.cleared = True

    def send_keys(self, txt):
        # registra o texto que foi enviado ao elemento
        self.sent_text = txt

    def click(self):
        # registra que click ocorreu
        self.clicked = True


class FakeDriver:
    """
    <summary>
    Driver falso para testes. Fornece hide_keyboard, page_source e métodos auxiliares.
    </summary>
    </summary>
    """
    def __init__(self):
        self.page_source = "<xml></xml>"
        self.screenshot_saved = False
        self.hide_keyboard_called = False

    def get_screenshot_as_file(self, path):
        # simula salvar screenshot
        self.screenshot_saved = True
        return True

    def hide_keyboard(self):
        # registra chamada para esconder teclado
        self.hide_keyboard_called = True

    def find_element(self, by, value):
        # não usado diretamente nos testes (pois _wait_for_clickable é monkeypatchado),
        # mas implementado para compatibilidade se necessário
        raise RuntimeError("find_element should not be called in this test harness")


@pytest.fixture
def fake_driver():
    """
    <summary>
    Fixture que retorna um FakeDriver para injeção no LoginPage.
    </summary>
    </returns>
    """
    return FakeDriver()


def test_enter_username_calls_send_keys(monkeypatch, fake_driver):
    """
    <summary>
    Verifica que enter_username usa _wait_for_clickable e envia o texto correto.
    </summary>
    </summary>
    """
    page = LoginPage(fake_driver)

    # Prepara um elemento falso e monkeypatch em _wait_for_clickable para retorná-lo
    fake_elem = FakeElement()

    def fake_wait(locator, timeout=None):
        # garante que o locator recebido é o USERNAME_FIELD
        assert locator == page.USERNAME_FIELD
        return fake_elem

    # Substitui o método privado para não depender de WebDriverWait real
    monkeypatch.setattr(page, "_wait_for_clickable", fake_wait)

    # Executa o método sob teste
    page.enter_username("meu_usuario")

    # Valida que o elemento recebeu o clear e o send_keys corretos
    assert fake_elem.cleared is True
    assert fake_elem.sent_text == "meu_usuario"


def test_enter_password_calls_send_keys(monkeypatch, fake_driver):
    """
    <summary>
    Verifica que enter_password usa _wait_for_clickable e envia a senha correta.
    </summary>
    </summary>
    """
    page = LoginPage(fake_driver)
    fake_elem = FakeElement()

    def fake_wait(locator, timeout=None):
        assert locator == page.PASSWORD_FIELD
        return fake_elem

    monkeypatch.setattr(page, "_wait_for_clickable", fake_wait)

    page.enter_password("minha_senha")

    assert fake_elem.cleared is True
    assert fake_elem.sent_text == "minha_senha"


def test_tap_login_success(monkeypatch, fake_driver):
    """
    <summary>
    Verifica que tap_login clica diretamente quando o botão está disponível.
    </summary>
    </summary>
    """
    page = LoginPage(fake_driver)
    fake_elem = FakeElement()

    # _wait_for_clickable deve retornar o botão de login
    def fake_wait(locator, timeout=None):
        assert locator == page.LOGIN_BUTTON
        return fake_elem

    monkeypatch.setattr(page, "_wait_for_clickable", fake_wait)

    # Executa tap_login; não deve lançar exceção
    page.tap_login()

    # Verifica que o botão foi clicado
    assert fake_elem.clicked is True


def test_tap_login_recovery(monkeypatch, fake_driver):
    """
    <summary>
    Simula falha inicial (_wait_for_clickable lança TimeoutException), 
    seguido por hide_keyboard e scroll bem sucedido e novo clique.
    </summary>
    </summary>
    """
    page = LoginPage(fake_driver)
    fake_elem = FakeElement()

    # Controle de chamadas para simular primeiro Timeout, depois sucesso
    call_count = {"n": 0}

    def fake_wait(locator, timeout=None):
        # A primeira chamada simula Timeout (para o login button)
        if call_count["n"] == 0:
            call_count["n"] += 1
            raise TimeoutException("simulated timeout")
        # Nas chamadas seguintes, retorna o elemento clicável
        return fake_elem

    # Substitui _wait_for_clickable
    monkeypatch.setattr(page, "_wait_for_clickable", fake_wait)
    # Substitui _scroll_to_element_by_id para simular que o elemento foi encontrado após scroll
    monkeypatch.setattr(page, "_scroll_to_element_by_id", lambda resource_id: True)
    # Substitui _capture_debug_artifacts para evitar escrita de arquivos reais (opcional)
    monkeypatch.setattr(page, "_capture_debug_artifacts", lambda prefix=None: None)

    # Adiciona hide_keyboard no fake_driver (já presente)
    # Executa; não deve levantar exceção pois a segunda tentativa deve ter sucesso
    page.tap_login()

    # Verifica que o fake_driver escondeu teclado (chamado no fluxo de recuperação)
    assert fake_driver.hide_keyboard_called is True
    # Verifica que o botão final foi clicado
    assert fake_elem.clicked is True


def test_login_via_menu_calls_menu_and_login(monkeypatch, fake_driver):
    """
    <summary>
    Verifica que login_via_menu clica no menu, no item "Log In" e então chama login().
    </summary>
    </summary>
    """
    page = LoginPage(fake_driver)
    menu_elem = FakeElement()
    menu_login_elem = FakeElement()

    # Monkeypatch de _wait_for_clickable para retornar elementos diferentes conforme o locator
    def fake_wait(locator, timeout=None):
        if locator == page.MENU_BUTTON:
            return menu_elem
        elif locator == page.MENU_LOGIN_TEXT:
            return menu_login_elem
        else:
            # Para qualquer outra chamada (p.ex. campos de credenciais), devolvemos um FakeElement simples
            return FakeElement()

    monkeypatch.setattr(page, "_wait_for_clickable", fake_wait)

    # Monitoramos se login() foi chamado com os argumentos esperados
    called = {"args": None}

    def fake_login(u, p):
        # registra os argumentos para verificar mais adiante
        called["args"] = (u, p)

    # Substitui o método login real por um fake para evitar chamadas adicionais
    monkeypatch.setattr(page, "login", fake_login)

    # Executa o fluxo via menu
    page.login_via_menu("usuarioX", "senhaY")

    # Verifica que o menu e o item de login foram clicados
    assert menu_elem.clicked is True
    assert menu_login_elem.clicked is True
    # Verifica que login() foi chamado com os parâmetros corretos
    assert called["args"] == ("usuarioX", "senhaY")
