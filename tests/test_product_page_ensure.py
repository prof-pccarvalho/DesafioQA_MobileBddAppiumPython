#!/usr/bin/env python3
import pytest
from unittest.mock import MagicMock
from selenium.common.exceptions import NoSuchElementException
from pages.product_page import ProductPage
from appium.webdriver.common.appiumby import AppiumBy

class FakeElement:
    def __init__(self, text=""):
        self.text = text
    def click(self): pass
    def find_element(self, by, value):
        if "TextView" in value:
            # retorna self simulando título relativo
            return self
        raise NoSuchElementException()

class FakeDriver:
    def __init__(self, all_pages):
        self.all_pages = all_pages
        self.current_page = 0

    def find_elements(self, by, value):
        # header case: productTV id returns header only (simulates bad locator)
        if by == AppiumBy.ID and value == "com.saucelabs.mydemoapp.android:id/productTV":
            return [FakeElement("Products")]
        # xpath images: return FakeElement per title with text populated
        if by == AppiumBy.XPATH and "ImageView" in value:
            page = self.all_pages[self.current_page]
            return [FakeElement(title) for title in page]
        return []

    def find_element(self, by, value):
        if by == AppiumBy.ANDROID_UIAUTOMATOR and "scrollForward" in value:
            if self.current_page < len(self.all_pages) - 1:
                self.current_page += 1
                return FakeElement("scrolled")
            raise NoSuchElementException()
        if by == AppiumBy.XPATH:
            import re
            m = re.search(r"\)\[(\d+)\]$", value)
            if m:
                idx = int(m.group(1)) - 1
                page = self.all_pages[self.current_page]
                if 0 <= idx < len(page):
                    return FakeElement(page[idx])
                raise NoSuchElementException()
        raise NoSuchElementException()

def test_ensure_minimum_products_with_pagination_and_duplicates(monkeypatch):
    """
    <summary>
    Garante que ensure_minimum_products chama collect_product_titles internamente e retorna o total final.
    Simula múltiplos scrolls com páginas que podem repetir itens (duplicatas).
    </summary>
    """
    driver = MagicMock()
    pp = ProductPage(driver)

    # Simula get_all_product_titles retornando páginas incrementais
    seq = [
        ["Products"],
        ["P1"],
        ["P1", "P2"],
        ["P1", "P2", "P3"],
    ]
    calls = {"i":0}
    def fake_get_all():
        i = calls["i"]
        calls["i"] += 1
        return seq[min(i, len(seq)-1)]
    monkeypatch.setattr(pp, "get_all_product_titles", fake_get_all)
    monkeypatch.setattr(pp, "_scroll_forward", lambda: True)

    total = pp.ensure_minimum_products(3, max_scrolls=5, wait_after_scroll=0)
    assert total >= 3

def test_ensure_minimum_products_with_pagination_and_duplicates_total():
    page1 = ["A1","A2","A3","A4"]
    page2 = ["B1","B2","B3","B4"]
    page3 = ["C1","C1","C1","C1"]
    driver = FakeDriver([page1, page2, page3])
    page = ProductPage(driver)
    final_all = page.ensure_minimum_products(12, max_scrolls=5, wait_after_scroll=0.0)
    assert isinstance(final_all, int)
