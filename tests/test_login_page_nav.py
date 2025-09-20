#!/usr/bin/env python3
import unittest
from unittest.mock import Mock, patch
from selenium.common.exceptions import TimeoutException
from pages.login_page import LoginPage

class DummyElement:
    def __init__(self):
        self.clicked = False
        self.cleared = False
        self.sent_keys = None
        self.text = ""

    def click(self):
        self.clicked = True

    def clear(self):
        self.cleared = True

    def send_keys(self, value):
        self.sent_keys = value

    def is_enabled(self):
        return True

class TestLoginPageNav(unittest.TestCase):
    def setUp(self):
        self.mock_driver = Mock()
        self.page = LoginPage(self.mock_driver, default_wait_seconds=0.1)

    @patch("pages.login_page.WebDriverWait")
    def test_open_menu_and_open_login_from_menu(self, mock_wait):
        # Simula elementos retornados para o menu e o item Log In
        menu_el = DummyElement()
        login_item_el = DummyElement()
        # WebDriverWait().until será chamado duas vezes: menu, login item
        mock_wait.return_value.until.side_effect = [menu_el, login_item_el]

        # Abre menu e escolhe Login
        self.page.open_menu()
        self.page.open_login_from_menu()

        self.assertTrue(menu_el.clicked)
        self.assertTrue(login_item_el.clicked)

    @patch("pages.login_page.WebDriverWait")
    def test_login_via_menu_sequence(self, mock_wait):
        # Simula: menu, login item, username field, password field, login button
        menu_el = DummyElement()
        login_item_el = DummyElement()
        username_el = DummyElement()
        password_el = DummyElement()
        login_btn_el = DummyElement()
        mock_wait.return_value.until.side_effect = [menu_el, login_item_el, username_el, password_el, login_btn_el]

        self.page.login_via_menu("visual@example.com", "10203040")

        # Verifica chamadas e valores
        self.assertTrue(menu_el.clicked)
        self.assertTrue(login_item_el.clicked)
        self.assertTrue(username_el.cleared)
        self.assertEqual(username_el.sent_keys, "visual@example.com")
        self.assertTrue(password_el.cleared)
        self.assertEqual(password_el.sent_keys, "10203040")
        self.assertTrue(login_btn_el.clicked)

    @patch("pages.login_page.WebDriverWait")
    def test_wait_timeout_captures_artifacts(self, mock_wait):
        mock_wait.return_value.until.side_effect = TimeoutException()
        with patch.object(self.page, "_capture_debug_artifacts") as mock_capture:
            with self.assertRaises(TimeoutException):
                self.page.open_menu()  # tentará esperar pelo MENU_BUTTON e falhará
            mock_capture.assert_called_once()

if __name__ == "__main__":
    unittest.main()
