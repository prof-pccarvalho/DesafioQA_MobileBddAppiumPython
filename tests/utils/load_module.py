#!/usr/bin/env python3
"""
<summary>
Utility para carregar dinamicamente um ficheiro .py como módulo usando um nome canônico.
Garante que o módulo seja registrado em sys.modules com o nome fornecido antes de executar
o código do ficheiro — isso permite que unittest.mock.patch por string (ex.: 
"features.steps.login_steps") funcione corretamente em testes que carregam o ficheiro dinamicamente.
</summary>
<remarks>
Uso típico:
    from tests.utils.load_module import load_module
    module = load_module(path_to_file, module_name="features.steps.login_steps")
</remarks>
"""
from typing import Optional
import importlib.util
import sys
import os


def load_module(file_path: str, module_name: Optional[str] = None):
    """
    <summary>
    Carrega um ficheiro Python (.py) a partir de 'file_path' como um módulo nomeado.
    Registra o objecto módulo em sys.modules antes de executar o código para que
    mocks/patche(s) que apontem para esse nome funcionem corretamente.
    </summary>
    <param name="file_path">Caminho absoluto ou relativo para o ficheiro .py a carregar.</param>
    <param name="module_name">
        Nome de módulo a usar em sys.modules. Ex.: "features.steps.login_steps".
        Se None, será usado o nome "loaded_module_<basename>" gerado automaticamente.
    </param>
    <returns>
        O objecto módulo carregado (module).
    </returns>
    <raises>FileNotFoundError se file_path não existir.</raises>
    """
    # Normaliza e valida o caminho do ficheiro
    abs_path = os.path.abspath(file_path)
    if not os.path.isfile(abs_path):
        # Falha cedo se o ficheiro não existir
        raise FileNotFoundError(f"File not found: {abs_path}")

    # Se nenhum nome de módulo for fornecido, cria um nome único baseado no nome do ficheiro
    if module_name is None:
        base = os.path.splitext(os.path.basename(abs_path))[0]
        module_name = f"loaded_module_{base}"

    # Cria um spec para o ficheiro, usando o module_name desejado
    spec = importlib.util.spec_from_file_location(module_name, abs_path)
    module = importlib.util.module_from_spec(spec)

    # Regista o módulo em sys.modules sob module_name ANTES de executar o ficheiro.
    # Isto é crucial para que unittest.mock.patch("features.steps.login_steps.X") funcione,
    # pois patch procura o objecto módulo no sys.modules.
    sys.modules[module_name] = module

    # Executa o código do ficheiro para popular o módulo com os atributos definidos no ficheiro
    spec.loader.exec_module(module)

    # Retorna o módulo já carregado e registado
    return module
