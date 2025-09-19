#!/usr/bin/env python3
import unittest
from unittest.mock import Mock, MagicMock, patch
from selenium.common.exceptions import TimeoutException
from pages.login_page import LoginPage


class TestLoginPage(unittest.TestCase):
    def setUp(self):
        # Mock do driver para injeção no Page Object
        self.mock_driver = Mock()
        # Instância da page com timeout pequeno para testes rápidos
        self.page = LoginPage(self.mock_driver, default_wait_seconds=0.1)

    def _make_element(self):
        """
        Cria um mock de WebElement com os métodos usados (clear, send_keys, click, is_enabled, text)
        """
        el = MagicMock()
        el.clear = MagicMock()
        el.send_keys = MagicMock()
        el.click = MagicMock()
        el.is_enabled = MagicMock(return_value=True)
        el.text = " mensagem de erro "
        return el

    @patch("pages.login_page.WebDriverWait")
    def test_enter_username_calls_clear_and_send_keys(self, mock_wait):
        username_el = self._make_element()
        # WebDriverWait(...).until(...) retornará nosso elemento
        mock_wait.return_value.until.return_value = username_el

        self.page.enter_username("standard_user")

        username_el.clear.assert_called_once()
        username_el.send_keys.assert_called_once_with("standard_user")

    @patch("pages.login_page.WebDriverWait")
    def test_enter_password_calls_clear_and_send_keys(self, mock_wait):
        password_el = self._make_element()
        mock_wait.return_value.until.return_value = password_el

        self.page.enter_password("secret_sauce")

        password_el.clear.assert_called_once()
        password_el.send_keys.assert_called_once_with("secret_sauce")

    @patch("pages.login_page.WebDriverWait")
    def test_tap_login_clicks_button(self, mock_wait):
        btn_el = self._make_element()
        mock_wait.return_value.until.return_value = btn_el

        self.page.tap_login()

        btn_el.click.assert_called_once()

    @patch("pages.login_page.WebDriverWait")
    def test_login_sequence_calls_all_steps(self, mock_wait):
        # Simular retorno de três elementos diferentes (username, password, button)
        user_el = self._make_element()
        pass_el = self._make_element()
        button_el = self._make_element()
        mock_wait.return_value.until.side_effect = [user_el, pass_el, button_el]

        self.page.login("u", "p")

        user_el.clear.assert_called_once()
        user_el.send_keys.assert_called_once_with("u")
        pass_el.clear.assert_called_once()
        pass_el.send_keys.assert_called_once_with("p")
        button_el.click.assert_called_once()

    @patch("pages.login_page.WebDriverWait")
    def test_is_login_button_enabled_true(self, mock_wait):
        btn_el = self._make_element()
        btn_el.is_enabled.return_value = True
        mock_wait.return_value.until.return_value = btn_el

        result = self.page.is_login_button_enabled()
        self.assertTrue(result)

    @patch("pages.login_page.WebDriverWait")
    def test_is_login_button_enabled_false_on_timeout(self, mock_wait):
        # Simular TimeoutException do WebDriverWait
        mock_wait.return_value.until.side_effect = TimeoutException()

        result = self.page.is_login_button_enabled()
        self.assertFalse(result)

    @patch("pages.login_page.WebDriverWait")
    def test_get_error_message_returns_trimmed_text(self, mock_wait):
        error_el = self._make_element()
        error_el.text = "  Erro de autenticação  "
        mock_wait.return_value.until.return_value = error_el

        msg = self.page.get_error_message()
        self.assertEqual(msg, "Erro de autenticação")

    @patch("pages.login_page.WebDriverWait")
    def test_get_error_message_returns_none_on_timeout(self, mock_wait):
        mock_wait.return_value.until.side_effect = TimeoutException()

        msg = self.page.get_error_message()
        self.assertIsNone(msg)


if __name__ == "__main__":
    unittest.main()
