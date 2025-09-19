#!/usr/bin/env python3
"""
<summary>
Testes unitários para features/steps/login_steps.py (arquivo gerado).
Os testes usam unittest + mocks para cobrir:
- check_android_environment
- _detect_appium_endpoint
- step_open_app (fluxos: options disponível e fallback; erro quando ambiente inválido)
- step_enter_credentials, step_click_login (verifica delegação ao Page Object)
- step_verify_home_screen (mocka WebDriverWait)
</summary>
"""
import os
import unittest
from unittest.mock import patch, Mock
# Importa o utilitário load_module que garante registrar o módulo com o nome canônico em sys.modules
from tests.utils.load_module import load_module


class DummyContext:
    """Contexto simples para simular context do Behave."""
    pass


class TestLoginStepsGenerated(unittest.TestCase):
    """
    <summary>
    Caso de teste para as steps de login. setUp carrega o módulo 'features.steps.login_steps'
    usando o utilitário que inscreve o módulo em sys.modules com o nome canônico, permitindo que
    @patch('features.steps.login_steps.X') seja aplicado corretamente.
    </summary>
    """

    def setUp(self):
        """
        <summary>
        Prepara o módulo a testar carregando o ficheiro de steps com nome canônico.
        Isso garante que patches que usem 'features.steps.login_steps' atinjam o módulo carregado.
        </summary>
        <returns>None</returns>
        """
        # Calcula o diretório-base do projeto (um nível acima de tests/)
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        # Constrói o caminho absoluto para features/steps/login_steps.py
        steps_path = os.path.join(base_dir, "features", "steps", "login_steps.py")
        # Carrega o módulo e registra em sys.modules com o nome canônico
        # (module_name deve coincidir com as strings usadas nos decorators @patch)
        self.mod = load_module(steps_path, module_name="features.steps.login_steps")

    # Tests for check_android_environment
    @patch.dict(os.environ, {}, clear=True)
    @patch("shutil.which", return_value=None)
    def test_check_android_environment_missing(self, mock_which):
        """
        <summary>
        Verifica que check_android_environment retorna False quando variáveis e adb faltam.
        </summary>
        """
        ok, info = self.mod.check_android_environment()
        self.assertFalse(ok)
        self.assertIn("Nenhuma variável", info["notes"])

    @patch.dict(os.environ, {"ANDROID_SDK_ROOT": "C:\\fake\\sdk"}, clear=False)
    @patch("os.path.isdir", return_value=True)
    @patch("shutil.which", return_value="C:\\fake\\sdk\\platform-tools\\adb.exe")
    @patch("subprocess.run")
    def test_check_android_environment_ok(self, mock_run, mock_which, mock_isdir):
        """
        <summary>
        Verifica que check_android_environment retorna True quando SDK e adb aparentam existir.
        </summary>
        """
        # Mock do subprocess.run simulando saída do 'adb version'
        mock_run.return_value = Mock(stdout="Android Debug Bridge version 1.0.41\n", returncode=0)
        ok, info = self.mod.check_android_environment()
        self.assertTrue(ok)
        self.assertIn("adb encontrado", info["notes"])

    # Tests for _detect_appium_endpoint
    @patch("requests.get")
    def test_detect_appium_endpoint_base_ok(self, mock_get):
        """
        <summary>
        Simula /status respondendo 200 no base sem /wd/hub e valida retorno.
        </summary>
        """
        mock_get.return_value = Mock(status_code=200)
        endpoint = self.mod._detect_appium_endpoint("http://localhost:4723")
        self.assertEqual(endpoint.rstrip("/"), "http://localhost:4723")

    @patch("requests.get")
    def test_detect_appium_endpoint_fallback_wd_hub(self, mock_get):
        """
        <summary>
        Simula falha no primeiro candidato e sucesso no /wd/hub, validando fallback.
        </summary>
        """
        def side_effect(url, timeout):
            if "/wd/hub" in url:
                return Mock(status_code=200)
            raise Exception("failed")
        mock_get.side_effect = side_effect
        endpoint = self.mod._detect_appium_endpoint("http://localhost:4723")
        self.assertTrue(endpoint.endswith("/wd/hub"))

    # Tests for step_open_app flows
    @patch("features.steps.login_steps.check_android_environment")
    @patch("features.steps.login_steps.webdriver.Remote")
    def test_step_open_app_fails_when_env_bad(self, mock_remote, mock_check_env):
        """
        <summary>
        Simula ambiente inválido e espera que step_open_app levante RuntimeError.
        </summary>
        """
        mock_check_env.return_value = (False, {"notes": "missing adb"})
        ctx = DummyContext()
        with self.assertRaises(RuntimeError):
            self.mod.step_open_app(ctx)

    @patch("features.steps.login_steps.check_android_environment")
    @patch("features.steps.login_steps._detect_appium_endpoint", return_value="http://localhost:4723")
    @patch("features.steps.login_steps.webdriver.Remote")
    def test_step_open_app_fallback_uses_desired_caps(self, mock_remote, mock_detect, mock_check_env):
        """
        <summary>
        Verifica que quando Options não estão disponíveis o fallback usa desired_capabilities.
        </summary>
        """
        mock_check_env.return_value = (True, {"notes": ""})
        # Força flag de módulo para não usar UiAutomator2Options
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
        caps = kwargs["desired_capabilities"]
        self.assertIn("app", caps)

    @patch("features.steps.login_steps.check_android_environment")
    @patch("features.steps.login_steps._detect_appium_endpoint", return_value="http://localhost:4723")
    @patch("features.steps.login_steps.webdriver.Remote")
    @patch("features.steps.login_steps.UiAutomator2Options")
    def test_step_open_app_uses_options_when_available(self, mock_opts_cls, mock_remote, mock_detect, mock_check_env):
        """
        <summary>
        Verifica que quando UiAutomator2Options está disponível, options é passado para Remote.
        </summary>
        """
        mock_check_env.return_value = (True, {"notes": ""})
        self.mod._HAS_UIAUTOMATOR2_OPTIONS = True

        mock_opts_instance = Mock()
        mock_opts_cls.return_value = mock_opts_instance

        mock_driver = Mock()
        mock_remote.return_value = mock_driver

        ctx = DummyContext()
        self.mod.step_open_app(ctx)

        self.assertTrue(hasattr(ctx, "driver"))
        self.assertIs(ctx.driver, mock_driver)
        mock_remote.assert_called()
        _, kwargs = mock_remote.call_args
        self.assertIn("options", kwargs)
        self.assertTrue(hasattr(kwargs["options"], "app"))

    # Tests for delegation steps
    def test_step_enter_credentials_and_click_delegation(self):
        """
        <summary>
        Verifica que step_enter_credentials e step_click_login delegam ao Page Object.
        </summary>
        """
        ctx = DummyContext()
        mock_page = Mock()
        ctx.login_page = mock_page

        self.mod.step_enter_credentials(ctx, "user1", "pass1")
        mock_page.enter_username.assert_called_once_with("user1")
        mock_page.enter_password.assert_called_once_with("pass1")

        self.mod.step_click_login(ctx)
        mock_page.tap_login.assert_called_once()

    @patch("features.steps.login_steps.WebDriverWait")
    def test_step_verify_home_screen_waits(self, mock_wait):
        """
        <summary>
        Verifica que step_verify_home_screen usa WebDriverWait e chama until().
        </summary>
        """
        ctx = DummyContext()
        mock_driver = Mock()
        ctx.driver = mock_driver
        # Configura WebDriverWait(...).until(...) para retornar um mock (sem exceção)
        mock_wait.return_value.until.return_value = Mock()

        # Executa (deve terminar sem exceção)
        self.mod.step_verify_home_screen(ctx)

        # Verifica que o WebDriverWait foi usado
        mock_wait.assert_called()


if __name__ == "__main__":
    unittest.main()
