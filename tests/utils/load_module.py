#!/usr/bin/env python3
"""
<summary>
Utility para carregar um ficheiro Python como módulo com nome canônico em sys.modules.
Garante que mocks/patches por string (ex.: "features.steps.login_steps") funcionem.
</summary>
"""
from typing import Optional
import importlib.util
import sys
import os

def load_module(file_path: str, module_name: Optional[str] = None):
    """
    <summary>
    Carrega 'file_path' como módulo nomeado 'module_name' e registra em sys.modules
    antes de executar o código do ficheiro.
    </summary>
    <param name="file_path">Caminho para o ficheiro .py</param>
    <param name="module_name">Nome a usar em sys.modules (ex: 'features.steps.login_steps')</param>
    <returns>O módulo carregado</returns>
    """
    abs_path = os.path.abspath(file_path)
    if not os.path.isfile(abs_path):
        raise FileNotFoundError(f"File not found: {abs_path}")

    if module_name is None:
        base = os.path.splitext(os.path.basename(abs_path))[0]
        module_name = f"loaded_module_{base}"

    spec = importlib.util.spec_from_file_location(module_name, abs_path)
    module = importlib.util.module_from_spec(spec)

    # Registrar no sys.modules antes de executar para permitir patch string-based funcionar
    sys.modules[module_name] = module

    spec.loader.exec_module(module)
    return module
