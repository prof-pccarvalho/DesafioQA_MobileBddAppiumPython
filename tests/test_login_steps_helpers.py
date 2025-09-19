#!/usr/bin/env python3
"""
<summary>
Testes unitários para helpers de login_steps.py: check_android_environment e _detect_appium_endpoint.
Usam mocks para isolar IO/sistema.
</summary>
"""
import os
import importlib.util
import unittest
from unittest.mock import patch, Mock


def load_module(path):
    spec = importlib.util.spec_from_file_location("features.steps.login_steps", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class TestLoginStepsHelpers(unittest.TestCase):
    def setUp(self):
        base_dir = os.path.abspath(importlib.util.find_spec("os").origin)
        # Ajuste do caminho do módulo para carregar a partir da pasta do projecto
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        steps_path = os.path.join(project_root, "features", "steps", "login_steps.py")
        self.mod = load_module(steps_path)

    @patch.dict(os.environ, {}, clear=True)
    @patch("shutil.which", return_value=None)
    def test_check_android_environment_missing(self, mock_which):
        ok, info = self.mod.check_android_environment()
        self.assertFalse(ok)
        self.assertIn("Nenhuma variável", info["notes"])

    @patch.dict(os.environ, {"ANDROID_SDK_ROOT": "C:\\fake\\sdk"}, clear=False)
    @patch("os.path.isdir", return_value=True)
    @patch("shutil.which", return_value="C:\\fake\\sdk\\platform-tools\\adb.exe")
    @patch("subprocess.run")
    def test_check_android_environment_ok(self, mock_run, mock_which, mock_isdir):
        mock_run.return_value = Mock(stdout="Android Debug Bridge version 1.0.41\n")
        ok, info = self.mod.check_android_environment()
        self.assertTrue(ok)
        self.assertIn("adb encontrado", info["notes"])

    @patch("requests.get")
    def test_detect_appium_endpoint_base_ok(self, mock_get):
        # Simula status OK no base sem /wd/hub
        mock_get.return_value = Mock(status_code=200)
        endpoint = self.mod._detect_appium_endpoint("http://localhost:4723")
        self.assertEqual(endpoint.rstrip("/"), "http://localhost:4723")

    @patch("requests.get")
    def test_detect_appium_endpoint_fallback(self, mock_get):
        # Primeiro falha, segundo OK (com /wd/hub)
        def side_effect(url, timeout):
            if "/wd/hub" in url:
                return Mock(status_code=200)
            raise Exception("fail")
        mock_get.side_effect = side_effect
        endpoint = self.mod._detect_appium_endpoint("http://localhost:4723")
        self.assertTrue(endpoint.endswith("/wd/hub"))


if __name__ == "__main__":
    unittest.main()
