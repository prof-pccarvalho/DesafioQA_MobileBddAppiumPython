#!/usr/bin/env python3
"""
<summary>
Testes unitários para as step definitions de login (features/steps/login_steps.py).
Os testes verificam efeitos observáveis (atribuição de context.driver,
criação de context.login_page e verificação da tela inicial) em vez de
confiar em mocks de implementação interna, tornando os testes mais robustos.
</summary>
"""
import os
import unittest
from unittest.mock import Mock, patch
import importlib.util


def load_module_from_path(module_name, file_path):
    """
    <summary>
    Carrega dinamicamente um módulo a partir de um caminho de ficheiro.
    Usado para tornar os testes independentes de pacotes instalados.
    </summary>
    <param name="module_name">Nome a atribuir ao módulo carregado (p.ex. 'features.steps.login_steps')</param>
    <param name="file_path">Caminho absoluto do ficheiro .py a carregar</param>
    <returns>O módulo carregado</returns>
    """
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class DummyContext:
    """Objeto simples que simula o contexto do Behave (context)."""
    pass


class TestLoginSteps(unittest.TestCase):
    """
    <summary>
    Testes para as steps de login. Testam:
      - inicialização do app (step_open_app) cria context.driver e context.login_page
      - step_enter_credentials delega para os métodos do Page Object
      - step_click_login chama tap_login do Page Object
      - step_verify_home_screen usa driver.find_element para localizar elemento da home
    </summary>
    """

    def setUp(self):
        """
        <summary>
        Carrega o módulo features/steps/login_steps.py a partir do ficheiro,
        permitindo testes sem instalar o pacote como módulo Python.
        </summary>
        """
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        steps_path = os.path.join(base_dir, "features", "steps", "login_steps.py")
        # Carrega o módulo de steps que será testado
        self.login_steps = load_module_from_path("features.steps.login_steps", steps_path)

    @patch("features.steps.login_steps.webdriver.Remote")
    def test_step_open_app_initializes_driver_and_login_page(self, mock_remote):
        """
        <summary>
        Verifica que step_open_app atribui context.driver (retorno de webdriver.Remote)
        e cria context.login_page contendo esse driver.
        </summary>
        """
        # Configura o Remote para retornar um mock de driver
        mock_driver = Mock()
        mock_remote.return_value = mock_driver

        ctx = DummyContext()
        # Executa a step que inicializa o app
        self.login_steps.step_open_app(ctx)

        # Verifica que context.driver foi atribuído com o mock retornado pelo Remote
        self.assertTrue(hasattr(ctx, "driver"))
        self.assertIs(ctx.driver, mock_driver)

        # Verifica que context.login_page foi atribuído e contém o mesmo driver
        self.assertTrue(hasattr(ctx, "login_page"), "context.login_page deve existir após step_open_app")
        # Verifica que o Page Object recebeu o driver (efeito observável)
        self.assertIs(ctx.login_page.driver, mock_driver)

    def test_step_enter_credentials_calls_page_methods(self):
        """
        <summary>
        Verifica que step_enter_credentials chama enter_username e enter_password
        do Page Object armazenado em context.login_page.
        </summary>
        """
        ctx = DummyContext()
        mock_login_page = Mock()
        ctx.login_page = mock_login_page

        # Chama a step que insere credenciais
        self.login_steps.step_enter_credentials(ctx, "usuarioX", "senhaY")

        # Verifica que os métodos do Page Object foram chamados com os parâmetros corretos
        mock_login_page.enter_username.assert_called_once_with("usuarioX")
        mock_login_page.enter_password.assert_called_once_with("senhaY")

    def test_step_click_login_calls_page_method(self):
        """
        <summary>
        Verifica que step_click_login chama tap_login do Page Object.
        </summary>
        """
        ctx = DummyContext()
        mock_login_page = Mock()
        ctx.login_page = mock_login_page

        self.login_steps.step_click_login(ctx)

        mock_login_page.tap_login.assert_called_once()

    def test_step_verify_home_screen_uses_driver_find_element(self):
        """
        <summary>
        Verifica que step_verify_home_screen localiza um elemento da home
        através de driver.find_element e valida que is_displayed() é True.
        </summary>
        """
        ctx = DummyContext()
        # Mock do driver com find_element retornando um WebElement mock
        mock_driver = Mock()
        mock_element = Mock()
        mock_element.is_displayed.return_value = True
        # Configura find_element para retornar o elemento mockado
        mock_driver.find_element.return_value = mock_element
        ctx.driver = mock_driver

        # Executa a step de verificação; deve terminar sem exceção
        self.login_steps.step_verify_home_screen(ctx)

        # Verifica que find_element foi chamado com os argumentos esperados
        # (AppiumBy.ACCESSIBILITY_ID, "open menu") — confirmamos pelo primeiro arg sendo uma string ou objeto
        # Como o método usa AppiumBy.ACCESSIBILITY_ID, apenas asseguramos que find_element foi chamado uma vez
        mock_driver.find_element.assert_called_once()
        mock_element.is_displayed.assert_called_once()


if __name__ == "__main__":
    unittest.main()
