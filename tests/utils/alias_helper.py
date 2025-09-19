#!/usr/bin/env python3
"""
<summary>
Helpers para registrar aliases de módulos em sys.modules para facilitar testes
quando módulos são carregados dinamicamente. Fornece uma função para garantir
que o módulo 'features.steps.login_steps' esteja importado e também registrado
sob o alias 'login_steps_mod'.
</summary>
"""
from typing import Any, List
import importlib
import sys


def register_login_steps_aliases() -> Any:
    """
    <summary>
    Importa o módulo 'features.steps.login_steps' e garante que ele também esteja
    disponível em sys.modules sob o alias 'login_steps_mod'. Retorna o objeto de módulo.
    </summary>
    <returns>
      O objeto módulo importado (module)
    </returns>
    """
    # Importar com o nome canônico (estrutura de package deve existir: features/steps/__init__.py)
    mod = importlib.import_module("features.steps.login_steps")
    # Registrar alias adicional usado por alguns testes
    sys.modules.setdefault("login_steps_mod", mod)
    # Garante também que a chave canônica exista (defensivo)
    sys.modules.setdefault("features.steps.login_steps", mod)
    # Retorna o módulo para que o chamador possa inspecioná-lo se necessário
    return mod
