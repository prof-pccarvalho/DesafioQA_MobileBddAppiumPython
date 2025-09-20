#!/usr/bin/env python3
"""
<summary>
Testes unitários para garantir que step_enter_credentials faz fallback
para abrir o menu + abrir login quando a primeira tentativa de inserir
username falha com TimeoutException.
</summary>
"""
from unittest.mock import Mock
import pytest
from selenium.common.exceptions import TimeoutException

# Importa o step que vamos testar
from features.steps.login_steps import step_enter_credentials


class DummyContext:
    pass


def test_step_enter_credentials_falls_back_to_menu():
    """
    <summary>
    Simula o cenário onde a primeira chamada enter_username lança TimeoutException.
    Esperamos que o step:
      - chame open_menu()
      - chame open_login_from_menu()
      - chame enter_username() e enter_password() novamente (segunda vez succeeds)
    </summary>
    """
    ctx = DummyContext()
    mock_page = Mock()

    # Configura enter_username para falhar na primeira chamada e ter sucesso na segunda
    mock_page.enter_username.side_effect = [TimeoutException("initial timeout"), None]
    # enter_password deve ser chamada apenas na segunda fase e não ser bloqueada
    mock_page.enter_password.return_value = None

    # open_menu / open_login_from_menu devem existir e serão chamadas no fallback
    mock_page.open_menu.return_value = None
    mock_page.open_login_from_menu.return_value = None

    ctx.login_page = mock_page

    # Executa o step
    step_enter_credentials(ctx, "usuarioX", "senhaX")

    # Verificações:
    # enter_username chamada duas vezes (primeira raise, segunda succeed)
    assert mock_page.enter_username.call_count == 2
    # open_menu e open_login_from_menu devem ter sido chamados uma vez cada
    mock_page.open_menu.assert_called_once()
    mock_page.open_login_from_menu.assert_called_once()
    # enter_password deve ter sido chamado uma vez com a senha correta
    mock_page.enter_password.assert_called_once_with("senhaX")
