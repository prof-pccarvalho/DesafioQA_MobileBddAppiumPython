#!/usr/bin/env python3
"""
<summary>
Testes unitários para o step 'que estou logado como ...' implementado em product_steps.py.
Cobre caminho direto (login() bem-sucedido) e caminho de fallback quando login() lança TimeoutException.
</summary>
"""
from types import SimpleNamespace
from unittest.mock import Mock
import pytest
from selenium.common.exceptions import TimeoutException

# Importa a função do arquivo de steps (caminho relativo)
from features.steps.product_steps import step_logged_in


def test_step_logged_in_calls_login_when_succeeds():
    """
    <summary>
    Quando login() funciona sem erro, login_via_menu() não deve ser chamado.
    </summary>
    """
    ctx = SimpleNamespace()
    mock_page = Mock()
    ctx.login_page = mock_page

    # Executa o step
    step_logged_in(ctx, "usuario@test.com", "senha123")

    # Valida que login foi chamado e fallback não
    mock_page.login.assert_called_once_with("usuario@test.com", "senha123")
    mock_page.login_via_menu.assert_not_called()


def test_step_logged_in_falls_back_to_menu_when_login_timeout():
    """
    <summary>
    Simula login() lançando TimeoutException na primeira tentativa, então valida
    que login_via_menu() é chamado como fallback.
    </summary>
    """
    ctx = SimpleNamespace()
    mock_page = Mock()
    # Simula TimeoutException ao chamar login()
    mock_page.login.side_effect = TimeoutException("timeout")
    ctx.login_page = mock_page

    # Executa o step
    step_logged_in(ctx, "usuario@test.com", "senha123")

    # Valida que login foi chamado e que fallback (login_via_menu) também foi invocado
    mock_page.login.assert_called_once_with("usuario@test.com", "senha123")
    mock_page.login_via_menu.assert_called_once_with("usuario@test.com", "senha123")
