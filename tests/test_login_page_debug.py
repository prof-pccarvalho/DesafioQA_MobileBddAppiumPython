#!/usr/bin/env python3
"""
<summary>
Testes para o comportamento de espera e captura de artefatos em pages/login_page.LoginPage.
</summary>
"""
import unittest
from unittest.mock import Mock, patch
from selenium.common.exceptions import TimeoutException
from pages.login_page import LoginPage

class TestLoginPageDebug(unittest.TestCase):
    def setUp(self):
        # Cria um driver mock simples
        self.mock_driver = Mock()
        # Instancia a page com timeout pequeno para testes
        self.page = LoginPage(self.mock_driver, default_wait_seconds=0.1)

    @patch("pages.login_page.WebDriverWait")
    def test_wait_for_element_timeout_captures_artifacts_and_raises(self, mock_wait):
        # Configura WebDriverWait.until para lançar TimeoutException
        mock_wait.return_value.until.side_effect = TimeoutException("timeout")
        # Patch no metodo interno de captura para verificar chamada (sem gravar ficheiros)
        with patch.object(self.page, "_capture_debug_artifacts") as mock_capture:
            with self.assertRaises(TimeoutException) as cm:
                self.page._wait_for_element(("id", "nonexistent"), timeout=0.01)
            # Asserções: capture foi chamada e exceção contém info sobre locator
            mock_capture.assert_called_once()
            self.assertIn("nonexistent", str(cm.exception))

if __name__ == "__main__":
    unittest.main()
