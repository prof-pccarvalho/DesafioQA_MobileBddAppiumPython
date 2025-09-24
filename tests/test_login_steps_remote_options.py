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
import sys
import types
import importlib.util
import unittest
from unittest.mock import Mock, patch


def load_module_from_path(module_name, file_path):
    """
    <summary>
    Carrega dinamicamente um módulo Python a partir de um caminho de ficheiro.
    Registra o módulo (e pacotes pais) em sys.modules ANTES de executar o código do módulo,
    garantindo que mocks aplicados por @patch com o target em string funcionem corretamente.
    </summary>
    <param name="module_name">Nome a atribuir ao módulo carregado</param>
    <param name="file_path">Caminho absoluto para o ficheiro .py</param>
    <returns>módulo carregado</returns>
    """
    # Cria o spec e o objeto do módulo sem ainda executá-lo
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)

    # Garante que os pacotes pai existam em sys.modules. Isso permite que imports internos
    # no módulo funcionem como se fosse importado via package (ex.: features.steps.x)
    parts = module_name.split(".")
    for i in range(1, len(parts)):
        pkg_name = ".".join(parts[:i])
        if pkg_name not in sys.modules:
            pkg = types.ModuleType(pkg_name)
            # marcar como pacote (opcional): facilita ferramentas que checam __path__
            pkg.__path__ = []
            sys.modules[pkg_name] = pkg

    # Registra o módulo no sys.modules ANTES de executar seu código.
    # Importante para que patch("features.steps.login_steps...") consiga encontrar o alvo.
    sys.modules[module_name] = module

    # Executa o módulo agora que está registrado
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

    @patch("features.steps.login_steps.check_android_environment")
    @patch("features.steps.login_steps.webdriver.Remote")
    def test_uses_options_when_available(self, mock_remote, mock_check_env):
        """
        <summary>
        Garante que quando o módulo estiver configurado para usar Options,
        webdriver.Remote é chamado com kwargs contendo 'options' e que esse
        options tem o campo 'app' definido conforme o APP_PATH esperado.
        </summary>
        """
        # 1) Mocka a checagem do ambiente Android para evitar RuntimeError causado por falta de SDK/local adb.
        # Retornamos (True, ...) como se o ambiente estivesse OK.
        mock_check_env.return_value = (True, {"notes": "ok"})

        # 2) Força o código do módulo a tomar o caminho de 'options'
        self.login_steps._HAS_UIAUTOMATOR2_OPTIONS = True

        # 3) Mock do retorno do webdriver.Remote
        mock_driver = Mock()
        mock_remote.return_value = mock_driver

        ctx = DummyContext()

        # 4) Executa o step (webdriver.Remote está mockado; check_android_environment também)
        self.login_steps.step_open_app(ctx)

        # 5) Asserts (idênticos aos do teste original)
        self.assertTrue(hasattr(ctx, "driver"))
        self.assertIs(ctx.driver, mock_driver)
        mock_remote.assert_called()
        _, kwargs = mock_remote.call_args
        self.assertIn("options", kwargs)
        options_obj = kwargs["options"]
        self.assertTrue(hasattr(options_obj, "app"))
        self.assertEqual(options_obj.app, self.expected_app_path)

    @patch("features.steps.login_steps.check_android_environment")
    @patch("features.steps.login_steps.webdriver.Remote")
    def test_fallback_to_desired_caps_when_options_not_available(self, mock_remote, mock_check_env):
        """
        <summary>
        Força o caminho de fallback (no qual _HAS_UIAUTOMATOR2_OPTIONS == False)
        e assegura que webdriver.Remote recebeu 'desired_capabilities' nos kwargs.
        </summary>
        """
        # Mocka a checagem do ambiente Android para evitar RuntimeError.
        mock_check_env.return_value = (True, {"notes": "ok"})

        # Força o uso do fallback
        self.login_steps._HAS_UIAUTOMATOR2_OPTIONS = False

        mock_driver = Mock()
        mock_remote.return_value = mock_driver

        ctx = DummyContext()
        # Executa o step com checagem do ambiente mockada
        self.login_steps.step_open_app(ctx)

        # Verificações (idênticas ao teste original)
        mock_remote.assert_called()
        _, kwargs = mock_remote.call_args
        self.assertIn("desired_capabilities", kwargs)
        self.assertIsInstance(kwargs["desired_capabilities"], dict)
        self.assertIn("app", kwargs["desired_capabilities"])
        self.assertEqual(kwargs["desired_capabilities"]["app"], self.expected_app_path)

if __name__ == "__main__":
    unittest.main()
