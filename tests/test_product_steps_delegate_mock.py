#!/usr/bin/env python3
import types
from unittest.mock import Mock
import pytest

from features.steps import product_steps as ps_mod

def test_step_compare_products_delegates_to_product_page_with_mock():
    """
    <summary>
    Mock mínimo com apenas compare_products configurado deve delegar diretamente.
    </summary>
    """
    ctx = types.SimpleNamespace()
    ctx.driver = object()
    fake_page = Mock()
    # apenas configure compare_products explicitamente
    fake_page.compare_products = Mock(return_value={"product_a": "A", "product_b": "B", "equal": False})
    ctx.product_page = fake_page

    ps_mod.step_compare_products(ctx, 1, 2)

    fake_page.compare_products.assert_called_once_with(0, 1)
    assert ctx.compare_result == {"product_a": "A", "product_b": "B", "equal": False}

def test_step_compare_products_fails_when_not_enough(monkeypatch, tmp_path):
    """
    <summary>
    Mock configurado com ensure_minimum_products/get_all_product_titles,
    mas get_all retorna apenas 1 item -> espera AssertionError e capture chamado.
    </summary>
    """
    ctx = types.SimpleNamespace()
    ctx.driver = object()
    fake_page = Mock()
    # configura explicitamente os métodos relevantes no Mock
    fake_page.ensure_minimum_products = Mock(return_value=1)
    fake_page.get_all_product_titles = Mock(return_value=["OnlyOne"])
    called = {"flag": False}
    def capture(prefix=None):
        called["flag"] = True
    fake_page._capture_debug_artifacts = capture
    # garante compare_products existe (para fallback não ser usado)
    fake_page.compare_products = Mock(return_value={})
    ctx.product_page = fake_page

    with pytest.raises(AssertionError):
        ps_mod.step_compare_products(ctx, 1, 2)

    assert called["flag"] is True
