#!/usr/bin/env python3
"""
<summary>
Conftest para pytest. Executa ações globais antes da coleta/execução de testes.
Aqui garantimos que login_steps esteja importado e registrado sob aliases
necessários, evitando erros de patch por nomes de módulos não encontrados.
</summary>
"""
from tests.utils.alias_helper import register_login_steps_aliases


def pytest_sessionstart(session):
    """
    <summary>
    Hook executado pelo pytest antes da coleta de testes. Chama o helper
    para registrar aliases para o módulo de steps.
    </summary>
    <param name="session">Objeto de sessão do pytest</param>
    <returns>None</returns>
    """
    try:
        # Importa e registra alias; se der erro, queremos que pytest mostre falha clara
        register_login_steps_aliases()
    except Exception as exc:
        # Falhar cedo com mensagem clara — pytest exibirá o erro de import se algo estiver mal
        raise RuntimeError(f"Falha ao registrar alias para login_steps: {exc}") from exc
