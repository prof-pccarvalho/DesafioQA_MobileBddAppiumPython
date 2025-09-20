#!/usr/bin/env python3
"""
<summary>
Testes unitários do android_env_check.verify.
</summary>
"""
import os
import unittest
from unittest.mock import patch, Mock
import importlib.util

def load_mod(path):
    spec = importlib.util.spec_from_file_location("android_env_check_mod", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

class TestAndroidEnvCheck(unittest.TestCase):
    def setUp(self):
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        path = os.path.join(base_dir, "features", "steps", "android_env_check.py")
        self.mod = load_mod(path)

    @patch.dict(os.environ, {}, clear=True)
    @patch("shutil.which", return_value=None)
    def test_no_adb(self, mock_which):
        ok, info = self.mod.check_android_environment()
        self.assertFalse(ok)
        self.assertIn("Nenhuma variável", info["notes"])

    @patch.dict(os.environ, {"ANDROID_SDK_ROOT": "C:\\fake\\sdk"}, clear=False)
    @patch("os.path.isdir", return_value=True)
    @patch("shutil.which", return_value="C:\\fake\\sdk\\platform-tools\\adb.exe")
    @patch("subprocess.run")
    def test_with_adb(self, mock_run, mock_which, mock_isdir):
        mock_run.return_value = Mock(stdout="Android Debug Bridge version 1.0.41\n")
        ok, info = self.mod.check_android_environment()
        self.assertTrue(ok)
        self.assertIn("adb encontrado", info["notes"])
