#!/usr/bin/env python3
"""
<summary>
Testes unitários para a lógica de inicialização da sessão Appium em
features/steps/login_steps.py. Valida que:
- quando o caminho das Options for usado, webdriver.Remote recebe um kwarg 'options'
  cuja propriedade 'app' corresponde ao APK esperado;
- quando for usado o fallback, webdriver.Remote recebe 'desired_capabilities'.
</summary>
"""
import os
import importlib.util
import unittest
from unittest.mock import Mock, patch


def load_module_from_path(module_name, file_path):
    """
    <summary>
    Carrega dinamicamente um módulo Python a partir de um caminho de ficheiro.
    </summary>
    <param name="module_name">Nome a atribuir ao módulo carregado</param>
    <param name="file_path">Caminho absoluto para o ficheiro .py</param>
    <returns>módulo carregado</returns>
    """
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class DummyContext:
    """Contexto simples para simular o context do Behave."""
    pass


class TestStepOpenApp(unittest.TestCase):
    """
    <summary>
    Valida a inicialização do driver Appium no step_open_app:
      - chamada a webdriver.Remote com 'options' quando _HAS_UIAUTOMATOR2_OPTIONS == True;
      - fallback para desired_capabilities quando _HAS_UIAUTOMATOR2_OPTIONS == False.
    </summary>
    """

    def setUp(self):
        """
        <summary>
        Carrega o módulo features/steps/login_steps.py para testar suas functions.
        </summary>
        """
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        steps_path = os.path.join(base_dir, "features", "steps", "login_steps.py")
        self.login_steps = load_module_from_path("features.steps.login_steps", steps_path)
        # Calcula o APP_PATH que o step espera por default (mesma lógica usada no step)
        self.expected_app_path = os.environ.get("APP_PATH", os.path.join("resources", "mda-2.2.0-25.apk"))

    @patch("features.steps.login_steps.webdriver.Remote")
    def test_uses_options_when_available(self, mock_remote):
        """
        <summary>
        Garante que quando o módulo estiver configurado para usar Options,
        webdriver.Remote é chamado com kwargs contendo 'options' e que esse
        options tem o campo 'app' definido conforme o APP_PATH esperado.
        </summary>
        """
        # Força o código do módulo a tomar o caminho de 'options'
        self.login_steps._HAS_UIAUTOMATOR2_OPTIONS = True

        # Mock que será retornado por webdriver.Remote()
        mock_driver = Mock()
        mock_remote.return_value = mock_driver

        ctx = DummyContext()

        # Executa o step (não inicia Appium de verdade porque webdriver.Remote está mockado)
        self.login_steps.step_open_app(ctx)

        # Verifica que context.driver foi atribuído
        self.assertTrue(hasattr(ctx, "driver"))
        self.assertIs(ctx.driver, mock_driver)

        # Verifica que Remote foi chamado pelo menos uma vez e inspeciona os kwargs da última chamada
        mock_remote.assert_called()
        _, kwargs = mock_remote.call_args

        # Checa que 'options' foi passado como keyword argument
        self.assertIn("options", kwargs, "Espera-se que kwargs contenha 'options' quando se usa UiAutomator2Options")

        # Verifica que o objeto options tem atributo 'app' com o caminho esperado.
        # Isso funciona tanto para um Mock quanto para um objeto UiAutomator2Options real,
        # pois o código atribui opts.app = desired_caps['app'] sempre.
        options_obj = kwargs["options"]
        # A propriedade pode ser armazenada como atributo 'app' — asseguramos que existe e bate com expected_app_path
        self.assertTrue(hasattr(options_obj, "app"), "O objeto options deve possuir atributo 'app'")
        self.assertEqual(options_obj.app, self.expected_app_path)

    @patch("features.steps.login_steps.webdriver.Remote")
    def test_fallback_to_desired_caps_when_options_not_available(self, mock_remote):
        """
        <summary>
        Força o caminho de fallback (no qual _HAS_UIAUTOMATOR2_OPTIONS == False)
        e assegura que webdriver.Remote recebeu 'desired_capabilities' nos kwargs.
        </summary>
        """
        # Força o uso do fallback
        self.login_steps._HAS_UIAUTOMATOR2_OPTIONS = False

        mock_driver = Mock()
        mock_remote.return_value = mock_driver

        ctx = DummyContext()
        # Executa o step
        self.login_steps.step_open_app(ctx)

        # Verifica que Remote foi chamado
        mock_remote.assert_called()
        _, kwargs = mock_remote.call_args

        # Esperamos que desired_capabilities seja passadas como kwarg no fallback
        self.assertIn("desired_capabilities", kwargs)
        self.assertIsInstance(kwargs["desired_capabilities"], dict)
        # Checa que o app path dentro das desired_caps bate com o esperado
        self.assertIn("app", kwargs["desired_capabilities"])
        self.assertEqual(kwargs["desired_capabilities"]["app"], self.expected_app_path)


if __name__ == "__main__":
    unittest.main()
