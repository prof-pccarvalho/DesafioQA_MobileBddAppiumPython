#!/usr/bin/env python3
import pytest
from selenium.common.exceptions import TimeoutException
from pages.login_page import LoginPage

class FakeElem:
    def __init__(self):
        self.clicked = False
        self.cleared = False
        self.sent_text = None

    def click(self): self.clicked = True
    def clear(self): self.cleared = True
    def send_keys(self, t): self.sent_text = t
    def is_enabled(self): return True

class FakeDriver:
    def __init__(self):
        self.page_source = "<xml></xml>"
        self.hide_keyboard_called = False
        self.screenshot_saved = False

    def get_screenshot_as_file(self, path):
        self.screenshot_saved = True
        return True

    def hide_keyboard(self):
        self.hide_keyboard_called = True

    def find_element(self, by, value):
        # Simplified behavior for is_login_button_enabled when driver.find_element called directly
        return FakeElem()

@pytest.fixture
def page():
    return LoginPage(FakeDriver())

def test_open_menu_and_login_via_menu_calls_login(monkeypatch, page):
    # prepara fake elements
    menu_elem = FakeElem()
    menu_login_elem = FakeElem()
    called = {"login": None}

    def fake_wait(locator, timeout=None):
        if locator == page.MENU_BUTTON:
            return menu_elem
        if locator == page.MENU_LOGIN_TEXT:
            return menu_login_elem
        # fallback: return a generic element for fields/buttons
        return FakeElem()

    monkeypatch.setattr(page, "_wait_for_clickable", fake_wait)
    def fake_login(u, p):
        called["login"] = (u, p)
    monkeypatch.setattr(page, "login", fake_login)

    page.login_via_menu("visual@example.com", "10203040")

    assert menu_elem.clicked is True
    assert menu_login_elem.clicked is True
    assert called["login"] == ("visual@example.com", "10203040")

def test_is_login_button_enabled_true(monkeypatch, page):
    # retorna elemento com is_enabled True
    monkeypatch.setattr(page, "_wait_for_element", lambda locator, timeout=None: FakeElem())
    assert page.is_login_button_enabled() is True

def test_wait_for_element_timeout_captures_artifacts_and_raises(monkeypatch, tmp_path, page):
    """
    <summary>
    Garante que _wait_for_element captura artifacts em caso de Timeout.
    Em vez de monkeypatchar o próprio método (o que invalidaria o teste),
    monkeypatchamos WebDriverWait no módulo para forçar Timeout na espera.
    </summary>
    """
    # DummyWait simula o objeto retornado por WebDriverWait(driver, timeout)
    class DummyWait:
        def __init__(self, driver, timeout):
            # ignoramos driver/timeout, pois apenas queremos controlar until()
            pass

        def until(self, condition):
            # força TimeoutException para simular timeout no wait
            raise TimeoutException("simulated timeout")

    # Importa o módulo onde _wait_for_element usa WebDriverWait
    import pages.login_page as lp_mod

    # Substitui WebDriverWait no módulo por nossa DummyWait para forçar timeout
    monkeypatch.setattr(lp_mod, "WebDriverWait", DummyWait)

    # Substitui _capture_debug_artifacts para marcar um flag em vez de escrever em disco
    monkeypatch.setattr(page, "_capture_debug_artifacts", lambda prefix=None: setattr(page, "_captured_test_flag", True))

    # Executa o método que deverá usar a DummyWait e, ao falhar, chamar _capture_debug_artifacts
    with pytest.raises(TimeoutException):
        page._wait_for_element(("by", "val"))

    # Verifica se a captura foi acionada
    assert getattr(page, "_captured_test_flag", False) is True
