#!/usr/bin/env python3
import unittest
from unittest.mock import Mock, MagicMock, patch
from selenium.common.exceptions import TimeoutException
from pages.login_page import LoginPage

class TestLoginPage(unittest.TestCase):
    def setUp(self):
        self.mock_driver = Mock()
        self.page = LoginPage(self.mock_driver, default_wait_seconds=0.1)

    def _make_element(self):
        el = MagicMock()
        el.clear = MagicMock()
        el.send_keys = MagicMock()
        el.click = MagicMock()
        el.is_enabled = MagicMock(return_value=True)
        el.text = " msg "
        return el

    @patch("pages.login_page.WebDriverWait")
    def test_enter_username_and_hide_keyboard(self, mock_wait):
        el = self._make_element()
        mock_wait.return_value.until.return_value = el
        # driver.hide_keyboard pode existir ou não
        self.mock_driver.hide_keyboard = Mock()
        self.page.enter_username("visual@example.com")
        el.clear.assert_called_once()
        el.send_keys.assert_called_once_with("visual@example.com")
        self.mock_driver.hide_keyboard.assert_called_once()

    @patch("pages.login_page.WebDriverWait")
    def test_enter_password_and_hide_keyboard(self, mock_wait):
        el = self._make_element()
        mock_wait.return_value.until.return_value = el
        self.mock_driver.hide_keyboard = Mock()
        self.page.enter_password("10203040")
        el.clear.assert_called_once()
        el.send_keys.assert_called_once_with("10203040")
        self.mock_driver.hide_keyboard.assert_called_once()

    @patch("pages.login_page.WebDriverWait")
    def test_tap_login_clicks(self, mock_wait):
        el = self._make_element()
        mock_wait.return_value.until.return_value = el
        self.page.tap_login()
        el.click.assert_called_once()

    @patch("pages.login_page.WebDriverWait")
    def test_login_sequence(self, mock_wait):
        user_el = self._make_element()
        pass_el = self._make_element()
        btn_el = self._make_element()
        mock_wait.return_value.until.side_effect = [user_el, pass_el, btn_el]
        self.page.login("u", "p")
        user_el.send_keys.assert_called_once_with("u")
        pass_el.send_keys.assert_called_once_with("p")
        btn_el.click.assert_called_once()

    @patch("pages.login_page.WebDriverWait")
    def test_is_login_button_enabled_true(self, mock_wait):
        btn = self._make_element()
        mock_wait.return_value.until.return_value = btn
        self.assertTrue(self.page.is_login_button_enabled())

    @patch("pages.login_page.WebDriverWait")
    def test_is_login_button_enabled_false_on_timeout(self, mock_wait):
        mock_wait.return_value.until.side_effect = TimeoutException()
        self.assertFalse(self.page.is_login_button_enabled())

    @patch("pages.login_page.WebDriverWait")
    def test_open_menu_and_login_from_menu_and_login(self, mock_wait):
        menu_el = self._make_element()
        login_item = self._make_element()
        username_el = self._make_element()
        password_el = self._make_element()
        btn_el = self._make_element()
        mock_wait.return_value.until.side_effect = [menu_el, login_item, username_el, password_el, btn_el]
        self.page.login_via_menu("visual@example.com", "10203040")
        # verify sequence
        self.assertTrue(menu_el.click.called)
        self.assertTrue(login_item.click.called)
        self.assertEqual(username_el.sent_keys, "visual@example.com")
        self.assertEqual(password_el.sent_keys, "10203040")
        self.assertTrue(btn_el.click.called)

    @patch("pages.login_page.WebDriverWait")
    def test_wait_timeout_captures_artifacts_and_raises(self, mock_wait):
        mock_wait.return_value.until.side_effect = TimeoutException()
        with patch.object(self.page, "_capture_debug_artifacts") as mock_capture:
            with self.assertRaises(TimeoutException):
                self.page.open_menu()
            mock_capture.assert_called_once()

if __name__ == "__main__":
    unittest.main()
