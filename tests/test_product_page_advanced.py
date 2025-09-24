#!/usr/bin/env python3
import pytest
from unittest.mock import MagicMock
from selenium.common.exceptions import NoSuchElementException
from pages.product_page import ProductPage
from appium.webdriver.common.appiumby import AppiumBy

class FakeElement:
    def __init__(self, text=""):
        self.text = text
        self.clicked = False

    def click(self):
        self.clicked = True

class FakeDriver:
    """
    Simula um driver minimalista suportando:
      - find_elements(by, value)
      - find_element(by, value)
      - get_window_size()
      - execute_script (simular mobile: swipe/dragGesture/scroll)
      - swipe (legacy)
    O comportamento simula um catálogo dividido em 'all_titles' e 'visible_count'.
    """
    def __init__(self, all_titles, support_ui_automator=True, support_execute_script=True):
        self.all_titles = list(all_titles)
        # quantos elementos inicialmente visíveis
        self.visible_count = min(1, len(self.all_titles))
        self.support_ui_automator = support_ui_automator
        self.support_execute_script = support_execute_script
        self.swipe_called = 0
        self.execute_calls = []

    def find_elements(self, by, value):
        if by == AppiumBy.ID and value == "com.saucelabs.mydemoapp.android:id/productTV":
            return [FakeElement(t) for t in self.all_titles[: self.visible_count]]
        return []

    def find_element(self, by, value):
        # Simula UiAutomator scroll: se a expressão vier com scrollForward e suportado, aumenta visible_count
        if by == AppiumBy.ANDROID_UIAUTOMATOR and "scrollForward" in value:
            if self.support_ui_automator:
                # aumenta visualização, simulando que scroll trouxe mais itens
                self.visible_count = min(len(self.all_titles), self.visible_count + 2)
                return FakeElement("scrolled")
            raise NoSuchElementException("UiAutomator not supported")
        # XPath image index handling
        if by == AppiumBy.XPATH:
            # extrai índice do final do xpath (simples)
            import re
            m = re.search(r"\)\[(\d+)\]$", value)
            if m:
                idx = int(m.group(1)) - 1
                if 0 <= idx < self.visible_count:
                    return FakeElement(self.all_titles[idx])
                raise NoSuchElementException("XPath index out of visible range")
        raise NoSuchElementException("not found")

    def get_window_size(self):
        return {"width": 1080, "height": 1920}

    def execute_script(self, name, params=None):
        # Registra a chamada e, se suportado, simula que o scroll trouxe mais itens
        self.execute_calls.append((name, params))
        if not self.support_execute_script:
            raise Exception("execute_script not supported")
        # Simula que execute_script trouxe +2 itens visíveis
        self.visible_count = min(len(self.all_titles), self.visible_count + 2)
        return True

    def swipe(self, sx, sy, ex, ey, duration):
        self.swipe_called += 1
        # cada swipe aumenta 1 item visível (simulação)
        self.visible_count = min(len(self.all_titles), self.visible_count + 1)
        return True

# -----------------------
# Testes
# -----------------------
def test_ensure_minimum_products_with_ui_automator_scroll():
    driver = FakeDriver(["A", "B", "C", "D"], support_ui_automator=True, support_execute_script=False)
    page = ProductPage(driver)
    final = page.ensure_minimum_products(3, max_scrolls=3)
    assert final >= 3
    assert len(page.get_all_product_titles()) >= 3

def test_ensure_minimum_products_with_execute_script_fallback():
    # sem UiAutomator, mas com execute_script suportado
    driver = FakeDriver(["P1", "P2", "P3", "P4"], support_ui_automator=False, support_execute_script=True)
    page = ProductPage(driver)
    final = page.ensure_minimum_products(3, max_scrolls=4)
    assert final >= 3
    # verifica que execute_script foi chamado ao menos uma vez
    assert any(call[0] in ("mobile: swipe", "mobile: dragGesture", "mobile: scroll") for call in driver.execute_calls)

def test_ensure_minimum_products_with_swipe_legacy_and_touchaction_fallback():
    # sem UiAutomator e sem execute_script -> deve usar swipe legacy
    driver = FakeDriver(["X", "Y", "Z"], support_ui_automator=False, support_execute_script=False)
    page = ProductPage(driver)
    final = page.ensure_minimum_products(3, max_scrolls=4)
    assert final >= 3
    assert driver.swipe_called >= 1

def test_select_product_by_image_index_and_compare():
    """
    <summary>
    Verifica fluxo: selecionar produto pela imagem (UiSelector.instance)
    e então comparar títulos via compare_products usando cache/collect.
    Mockamos driver e funções auxiliares para comportamento determinístico.
    </summary>
    """
    driver = MagicMock()
    pp = ProductPage(driver)

    # Mock do elemento de imagem que será clicado
    img_elem = MagicMock()
    driver.find_element.return_value = img_elem

    # Preenche cache de títulos simulando que collect_product_titles já foi executado
    pp._last_collected_titles = ["A", "B", "C", "D"]

    # chama select_product_by_image_index para garantir invocação do find_element com UiSelector
    returned = pp.select_product_by_image_index(1)
    expected_selector = f"{pp.PRODUCT_IMAGE_UIAUTOMATOR_BASE}.instance(1)"
    driver.find_element.assert_called_with(AppiumBy.ANDROID_UIAUTOMATOR, expected_selector)
    img_elem.click.assert_called_once()
    assert returned is img_elem

    # Usa compare_products e confirma comparação consistente (0 vs 1 => "A" vs "B")
    res = pp.compare_products(0, 1)
    assert res["product_a"] == "A"
    assert res["product_b"] == "B"
    assert res["equal"] is False