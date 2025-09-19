#!/usr/bin/env python3
import os
import unittest
from unittest.mock import Mock
import importlib.util


def load_module_from_path(module_name, file_path):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class DummyContext:
    pass


class TestEnvironment(unittest.TestCase):
    def setUp(self):
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        env_path = os.path.join(base_dir, "features", "environment.py")
        self.env = load_module_from_path("features.environment", env_path)

    def test_after_scenario_quits_driver_if_present(self):
        ctx = DummyContext()
        mock_driver = Mock()
        ctx.driver = mock_driver

        # Chama a função after_scenario — deve tentar chamar driver.quit()
        self.env.after_scenario(ctx, None)

        mock_driver.quit.assert_called_once()

    def test_after_scenario_no_error_if_no_driver(self):
        ctx = DummyContext()
        # Deve simplesmente não levantar exceção quando não houver driver
        self.env.after_scenario(ctx, None)


if __name__ == "__main__":
    unittest.main()
