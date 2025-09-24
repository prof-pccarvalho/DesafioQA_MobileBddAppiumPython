#!/usr/bin/env python3
from unittest.mock import Mock
import types
import pytest

from features.steps import product_steps as ps_mod

def test_step_app_on_products_requires_driver():
    ctx = types.SimpleNamespace()
    # driver ausente -> RuntimeError
    with pytest.raises(RuntimeError):
        ps_mod.step_app_on_products(ctx)

def test_step_compare_products_delegates_to_product_page(monkeypatch):
    ctx = types.SimpleNamespace()
    # cria driver dummy e um product_page fake
    ctx.driver = object()
    fake_page = Mock()
    fake_page.compare_products.return_value = {"product_a": "A", "product_b": "B", "equal": False}
    ctx.product_page = fake_page

    # chama step (feature usa 1-based)
    ps_mod.step_compare_products(ctx, 1, 2)
    assert ctx.compare_result == {"product_a": "A", "product_b": "B", "equal": False}
    fake_page.compare_products.assert_called_once_with(0, 1)

def test_then_assert_titles_different_and_equal():
    ctx = types.SimpleNamespace()
    ctx.compare_result = {"product_a": "A", "product_b": "B", "equal": False}
    # não deve levantar
    ps_mod.step_assert_titles_different(ctx)

    ctx.compare_result = {"product_a": "Same", "product_b": "Same", "equal": True}
    ps_mod.step_assert_titles_equal(ctx)

    # se resultado não está presente, deve lançar
    ctx2 = types.SimpleNamespace()
    with pytest.raises(AssertionError):
        ps_mod.step_assert_titles_different(ctx2)
