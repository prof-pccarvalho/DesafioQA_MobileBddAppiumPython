#!/usr/bin/env python3
"""
<summary>
Testes unitários para tests.utils.alias_helper.register_login_steps_aliases.
Verifica que o módulo é importado e que sys.modules contém os aliases esperados.
</summary>
"""
import sys
import importlib.util
import os
import unittest

from tests.utils import alias_helper


class TestAliasHelper(unittest.TestCase):
    def test_register_login_steps_aliases(self):
        """
        <summary>
        Garante que register_login_steps_aliases retorna um módulo e registra as chaves
        'features.steps.login_steps' e 'login_steps_mod' no sys.modules.
        </summary>
        """
        # Executa a função
        mod = alias_helper.register_login_steps_aliases()
        # Verifica retorno e registro em sys.modules
        self.assertIsNotNone(mod)
        self.assertIn("features.steps.login_steps", sys.modules)
        self.assertIn("login_steps_mod", sys.modules)
        # Checagem adicional: os dois nomes apontam para o mesmo objeto módulo
        self.assertIs(sys.modules["features.steps.login_steps"], sys.modules["login_steps_mod"])


if __name__ == "__main__":
    unittest.main()
