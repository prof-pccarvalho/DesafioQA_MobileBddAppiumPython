#!/usr/bin/env python3
"""
<summary>
Testes unitários para tests.utils.load_module.load_module.
Os testes garantem que:
- o módulo é carregado com o nome pedido;
- sys.modules contém a entrada com esse nome;
- FileNotFoundError é levantado para ficheiro inexistente.
</summary>
"""
import os
import sys
import unittest
from tests.utils.load_module import load_module


class TestLoadModuleUtility(unittest.TestCase):
    def setUp(self):
        # Caminho para o ficheiro de steps existente no projeto (assume a estrutura fornecida)
        self.project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        self.login_steps_path = os.path.join(self.project_root, "features", "steps", "login_steps.py")

    def tearDown(self):
        # Remove entradas que possamos ter adicionado a sys.modules para evitar poluir o ambiente de testes
        for key in list(sys.modules.keys()):
            if key.startswith("loaded_module_") or key == "features.steps.login_steps" or key == "login_steps_mod":
                # Não removemos módulos essenciais do sistema, apenas limpamos aliases usados por estes testes
                try:
                    del sys.modules[key]
                except KeyError:
                    pass

    def test_load_module_with_explicit_name(self):
        # Carrega o ficheiro com o nome canônico usado nos patches
        module = load_module(self.login_steps_path, module_name="features.steps.login_steps")
        # Verificações:
        self.assertIn("features.steps.login_steps", sys.modules)
        self.assertIs(sys.modules["features.steps.login_steps"], module)
        self.assertTrue(hasattr(module, "step_open_app"))  # função definida no ficheiro de steps

    def test_load_module_auto_name_and_not_found(self):
        # Carrega com nome automático (baseado em filename)
        module_auto = load_module(self.login_steps_path)
        self.assertTrue(module_auto.__name__.startswith("loaded_module_"))

        # Tenta carregar ficheiro inexistente -> FileNotFoundError
        fake_path = os.path.join(self.project_root, "nonexistent_abcdefg.py")
        with self.assertRaises(FileNotFoundError):
            load_module(fake_path)


if __name__ == "__main__":
    unittest.main()
