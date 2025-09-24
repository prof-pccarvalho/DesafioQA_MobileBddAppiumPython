#!/usr/bin/env python3
import types
import pytest
from unittest.mock import Mock

from features.steps import product_steps as ps_mod

def test_step_compare_products_calls_compare_when_enough(monkeypatch):
    ctx = types.SimpleNamespace()
    ctx.driver = object()
    # fake product_page com ensure_minimum_products que retorna >= required_count
    fake_page = Mock()
    fake_page.ensure_minimum_products.return_value = 2
    fake_page.get_all_product_titles.return_value = ["A", "B"]
    fake_page.compare_products.return_value = {"product_a": "A", "product_b": "B", "equal": False}
    ctx.product_page = fake_page

    # Executa step (com índices 1 e 2)
    ps_mod.step_compare_products(ctx, 1, 2)

    # Verifica que compare_products foi chamado com índices 0 e 1
    fake_page.compare_products.assert_called_once_with(0, 1)
    assert ctx.compare_result == {"product_a": "A", "product_b": "B", "equal": False}

def test_step_compare_products_fails_when_not_enough(monkeypatch, tmp_path):
    ctx = types.SimpleNamespace()
    ctx.driver = object()
    fake_page = Mock()
    # ensure_minimum_products retornou menos que o necessário
    fake_page.ensure_minimum_products.return_value = 1
    fake_page.get_all_product_titles.return_value = ["OnlyOne"]
    # Disponibilizamos _capture_debug_artifacts para checar se foi chamado
    called = {"flag": False}
    def capture(prefix=None):
        called["flag"] = True
    fake_page._capture_debug_artifacts = capture
    ctx.product_page = fake_page

    with pytest.raises(AssertionError) as exc:
        ps_mod.step_compare_products(ctx, 1, 2)

    assert "Não existem itens suficientes" in str(exc.value)
    assert called["flag"] is True
