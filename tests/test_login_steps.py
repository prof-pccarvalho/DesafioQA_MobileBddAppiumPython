#!/usr/bin/env python3
"""
<summary>
Testes unitários para features/steps/login_steps.py.
Usam load_module utilitário para carregar o módulo com nome canônico e mocks.
</summary>
"""
import os
import unittest
from unittest.mock import Mock, patch
from tests.utils.load_module import load_module

class DummyContext: pass

class TestLoginSteps(unittest.TestCase):
    def setUp(self):
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        steps_path = os.path.join(base_dir, "features", "steps", "login_steps.py")
        # Carrega com module_name canônico para permitir patches por string
        self.mod = load_module(steps_path, module_name="features.steps.login_steps")

    def test_step_open_app_raises_on_bad_env(self):
        # Substitui check_android_environment dentro do módulo carregado
        with patch("features.steps.login_steps.check_android_environment", return_value=(False, {"notes": "no adb"})):
            ctx = DummyContext()
            with self.assertRaises(RuntimeError):
                self.mod.step_open_app(ctx)

    def test_step_open_app_uses_fallback_desired_caps(self):
        with patch("features.steps.login_steps.check_android_environment", return_value=(True, {"notes": ""})), \
             patch("features.steps.login_steps._detect_appium_endpoint", return_value="http://localhost:4723"), \
             patch("features.steps.login_steps.webdriver.Remote") as mock_remote:
            # Forçar não ter UiAutomator2Options
            self.mod._HAS_UIAUTOMATOR2_OPTIONS = False
            ctx = DummyContext()
            mock_driver = Mock()
            mock_remote.return_value = mock_driver

            self.mod.step_open_app(ctx)

            self.assertTrue(hasattr(ctx, "driver"))
            self.assertIs(ctx.driver, mock_driver)
            mock_remote.assert_called()
            _, kwargs = mock_remote.call_args
            self.assertIn("desired_capabilities", kwargs)

    def test_step_open_app_uses_options_when_available(self):
        with patch("features.steps.login_steps.check_android_environment", return_value=(True, {"notes": ""})), \
             patch("features.steps.login_steps._detect_appium_endpoint", return_value="http://localhost:4723"), \
             patch("features.steps.login_steps.webdriver.Remote") as mock_remote, \
             patch("features.steps.login_steps.UiAutomator2Options") as mock_opts_cls:
            self.mod._HAS_UIAUTOMATOR2_OPTIONS = True
            mock_opts_instance = Mock()
            mock_opts_cls.return_value = mock_opts_instance
            mock_driver = Mock()
            mock_remote.return_value = mock_driver

            ctx = DummyContext()
            self.mod.step_open_app(ctx)

            self.assertTrue(hasattr(ctx, "driver"))
            mock_remote.assert_called()
            _, kwargs = mock_remote.call_args
            self.assertIn("options", kwargs)

    def test_step_enter_credentials_and_click(self):
        ctx = DummyContext()
        mock_page = Mock()
        ctx.login_page = mock_page
        self.mod.step_enter_credentials(ctx, "user", "pass")
        mock_page.enter_username.assert_called_once_with("user")
        mock_page.enter_password.assert_called_once_with("pass")
        self.mod.step_click_login(ctx)
        mock_page.tap_login.assert_called_once()

    def test_step_verify_home_screen_waits(self):
        with patch("features.steps.login_steps.WebDriverWait") as mock_wait:
            ctx = DummyContext()
            ctx.driver = Mock()
            mock_wait.return_value.until.return_value = Mock()
            self.mod.step_verify_home_screen(ctx)
            mock_wait.assert_called()

if __name__ == "__main__":
    unittest.main()
