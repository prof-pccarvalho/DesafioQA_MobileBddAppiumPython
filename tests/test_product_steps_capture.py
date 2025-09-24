#!/usr/bin/env python3
"""
<summary>
Valida que steps.product_steps.step_compare_products captura artifacts
quando não existem produtos suficientes visíveis (visible_count < required_count).
</summary>
"""
from types import SimpleNamespace
from unittest.mock import MagicMock
import pytest

# importa o módulo de steps (já disponível no seu tree: features/steps/product_steps.py)
import features.steps.product_steps as product_steps


def test_step_compare_products_calls_capture_when_insufficient():
    """
    <summary>
    Cria um contexto com product_page mockado que:
      - garante ensure_minimum_products existe (não lança)
      - get_all_product_titles retorna lista curta (header-like ou insuficiente)
      - tem método _capture_debug_artifacts (MagicMock)
    Ao executar step_compare_products(1, 2) deve lançar AssertionError e
    produto_page._capture_debug_artifacts deve ter sido chamado com prefix esperado.
    </summary>
    """
    # Contexto simples para Behave
    ctx = SimpleNamespace()

    # Monta um mock de ProductPage com os métodos necessários
    pp_mock = MagicMock()
    # ensure_minimum_products deve existir e não falhar (apenas simula scroll)
    pp_mock.ensure_minimum_products.return_value = None
    # get_all_product_titles devolve lista insuficiente (ex.: só header)
    pp_mock.get_all_product_titles.return_value = ["Products"]  # header-like -> visible_count == 1
    # define _capture_debug_artifacts como MagicMock para verificar a chamada
    pp_mock._capture_debug_artifacts = MagicMock()

    # injeta no contexto
    ctx.product_page = pp_mock

    # Executa o step e espera AssertionError (insuficientes produtos)
    with pytest.raises(AssertionError) as excinfo:
        product_steps.step_compare_products(ctx, 1, 2)  # pede 2 produtos, só há 1 visível

    # Verifica que o prefixo esperado foi passado para captura
    pp_mock._capture_debug_artifacts.assert_called_once_with(prefix="compare_products_insufficient")

    # Verifica que a mensagem do AssertionError contém informação útil
    msg = str(excinfo.value)
    assert "Não existem itens suficientes no catálogo" in msg
