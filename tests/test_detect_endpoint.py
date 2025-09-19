#!/usr/bin/env python3
"""
<summary>
Testes unitários para a função _detect_appium_endpoint em features/steps/login_steps.py.
Os testes mockam requests.get diretamente para simular diferentes respostas do servidor Appium.
</summary>
"""
import unittest
from unittest.mock import patch, Mock
import importlib.util
import os


def load_module(path):
    """
    <summary>
    Carrega dinamicamente um módulo Python a partir do caminho de ficheiro.
    </summary>
    <param name="path">Caminho absoluto para o módulo .py</param>
    <returns>módulo carregado</returns>
    """
    spec = importlib.util.spec_from_file_location("login_steps_mod", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class TestDetectEndpoint(unittest.TestCase):
    """
    <summary>
    Testa a função de detecção do endpoint do Appium.
    </summary>
    """

    def setUp(self):
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        steps_path = os.path.join(base_dir, "features", "steps", "login_steps.py")
        self.module = load_module(steps_path)

    @patch("requests.get")
    def test_detect_no_wd_hub_but_base_ok(self, mock_get):
        """
        <summary>
        Simula que o endpoint '<base>/status' responde 200 e valida que a função retorna a URL base.
        </summary>
        """
        # Mock de resposta com status_code 200
        mock_get.return_value = Mock(status_code=200)

        endpoint = self.module._detect_appium_endpoint("http://localhost:4723")
        self.assertEqual(endpoint.rstrip("/"), "http://localhost:4723")

    @patch("requests.get")
    def test_detect_fallback_to_wd_hub(self, mock_get):
        """
        <summary>
        Simula falha na consulta sem /wd/hub e sucesso em /wd/hub/status.
        </summary>
        """
        # Implementa side_effect: primeira chamada -> exceção; segunda -> Mock(200)
        def side_effect(url, timeout):
            if url.endswith("/status") and "/wd/hub" not in url:
                # simula falha na primeira tentativa
                raise Exception("connection failed")
            return Mock(status_code=200)

        mock_get.side_effect = side_effect

        endpoint = self.module._detect_appium_endpoint("http://localhost:4723")
        self.assertTrue(endpoint.endswith("/wd/hub"))


if __name__ == "__main__":
    unittest.main()
