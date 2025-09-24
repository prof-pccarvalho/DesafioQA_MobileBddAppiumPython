#!/usr/bin/env python3
"""
<summary>
Valida fallback robusto de get_all_product_titles:
- Quando existem image elements (productIV) e existem title elements (productTV),
  o método deve preferir os textos de productTV.
</summary>
"""
from unittest.mock import MagicMock
from appium.webdriver.common.appiumby import AppiumBy
from pages.product_page import ProductPage

def make_el(text):
    e = MagicMock()
    type(e).text = text
    return e

def test_get_all_product_titles_prefers_title_elements():
    driver = MagicMock()
    pp = ProductPage(driver)

    # Simula primeira tentativa por PRODUCT_TITLE retornando header-like
    header = make_el("Products")
    # Simula imagem elements encontrados via ANDROID_UIAUTOMATOR
    img1 = MagicMock(); type(img1).text = ""
    img2 = MagicMock(); type(img2).text = ""

    # Simula title elements que existem e devem ser preferidos
    title1 = make_el("Preferred 1")
    title2 = make_el("Preferred 2")

    def find_elements_side(by, val):
        # primeira chamada para PRODUCT_TITLE (inicial) retorna header
        if by == pp.PRODUCT_TITLE[0] and val == pp.PRODUCT_TITLE[1]:
            # On first call used to detect header-like -> return header
            # But when later used to get title_elems we want to return title elements.
            # Emulate: first call -> header; subsequent calls -> title elements.
            # We'll detect by looking at a flag set on driver for call count.
            calls = getattr(driver, "_calls", 0)
            if calls == 0:
                driver._calls = calls + 1
                return [header]
            else:
                # when used to fetch title_elems after detecting images
                return [title1, title2]
        if by == AppiumBy.ANDROID_UIAUTOMATOR and val == pp.PRODUCT_IMAGE_UIAUTOMATOR_BASE:
            return [img1, img2]
        return []

    driver.find_elements.side_effect = find_elements_side

    titles = pp.get_all_product_titles()
    assert titles == ["Preferred 1", "Preferred 2"]
