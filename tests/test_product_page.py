#!/usr/bin/env python3
import pytest
from pages.product_page import ProductPage
from selenium.common.exceptions import TimeoutException

class FakeElement:
    def __init__(self, text=""):
        self.text = text
        self.clicked = False

    def click(self):
        # registra que o elemento foi clicado
        self.clicked = True

class FakeDriver:
    def __init__(self, texts):
        # texts é uma lista de strings que serão retornadas como elementos
        self._texts = texts

    def find_elements(self, by, value):
        # Retorna FakeElement para cada texto configurado
        return [FakeElement(t) for t in self._texts]


def test_get_all_product_titles():
    driver = FakeDriver(["Produto A", "Produto B", "Produto C"])
    page = ProductPage(driver)
    titles = page.get_all_product_titles()
    assert titles == ["Produto A", "Produto B", "Produto C"]

def test_get_product_title_by_index_valid():
    driver = FakeDriver(["X", "Y"])
    page = ProductPage(driver)
    assert page.get_product_title_by_index(1) == "Y"

def test_get_product_title_by_index_out_of_range():
    driver = FakeDriver(["A"])
    page = ProductPage(driver)
    with pytest.raises(IndexError):
        page.get_product_title_by_index(5)

def test_select_product_clicks_and_returns_element():
    driver = FakeDriver(["P1", "P2"])
    page = ProductPage(driver)
    el = page.select_product(0)
    # FakeElement.click sets clicked True; but select_product returns an element from a new list instance,
    # so we verify by calling click on returned element again to assert behavior in this fake context.
    assert hasattr(el, "clicked")
    # clicking was invoked inside select_product; in our fake, el.clicked should be True
    assert el.clicked is True

def test_compare_products_equal_and_not_equal():
    driver_eq = FakeDriver(["Same", "Same"])
    page_eq = ProductPage(driver_eq)
    res = page_eq.compare_products(0,1)
    assert res["equal"] is True

    driver_neq = FakeDriver(["One", "Two"])
    page_neq = ProductPage(driver_neq)
    res2 = page_neq.compare_products(0,1)
    assert res2["equal"] is False
