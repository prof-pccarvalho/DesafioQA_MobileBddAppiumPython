#!/usr/bin/env python3
import pytest
from selenium.common.exceptions import TimeoutException
from pages.login_page import LoginPage

class FakeElem:
    def __init__(self):
        self.clicked = False
        self.cleared = False
        self.sent_keys = None
        self.sent_text = None

    def click(self): self.clicked = True
    def clear(self): self.cleared = True
    def send_keys(self, t): 
        # registra também via atributo (simula FakeElement de testes)
        self.sent_keys = t
        self.sent_text = t

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
        return FakeElem()

@pytest.fixture
def page():
    return LoginPage(FakeDriver())

def test_open_login_from_menu(monkeypatch, page):
    menu_elem = FakeElem()
    login_item = FakeElem()

    def fake_wait(locator, timeout=None):
        if locator == page.MENU_BUTTON:
            return menu_elem
        if locator == page.MENU_LOGIN_TEXT:
            return login_item
        return FakeElem()

    monkeypatch.setattr(page, "_wait_for_clickable", fake_wait)
    # open_menu + open_login_from_menu are used by login_via_menu, but test the primitive explicitly
    res = page.open_login_from_menu()
    assert login_item.clicked is True

def test_enter_username_sets_sent_keys(monkeypatch, page):
    fake_elem = FakeElem()
    def fake_wait(locator, timeout=None):
        assert locator == page.USERNAME_FIELD
        return fake_elem
    monkeypatch.setattr(page, "_wait_for_clickable", fake_wait)
    page.enter_username("visual@example.com")
    # garante que setamos os atributos auxiliares no elemento
    assert getattr(fake_elem, "sent_keys", None) == "visual@example.com"
    assert getattr(fake_elem, "sent_text", None) == "visual@example.com"
