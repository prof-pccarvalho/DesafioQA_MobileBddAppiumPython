#!/usr/bin/env python3
"""
<summary>
Valida que get_all_product_titles utiliza XPATH global (baseado em resource-id / content-desc)
quando productTV não está presente inicialmente.
</summary>
"""
from unittest.mock import MagicMock
from appium.webdriver.common.appiumby import AppiumBy
from pages.product_page import ProductPage

def make_elem_with_text(text):
    e = MagicMock()
    type(e).text = text
    return e

def test_xpath_global_using_inspector_attributes():
    driver = MagicMock()
    pp = ProductPage(driver)

    # 1) initial call by PRODUCT_TITLE returns only header-like -> triggers fallback
    header = make_elem_with_text("Products")
    # We'll track calls for PRODUCT_TITLE initial vs later; simple flag on driver
    def find_elems(by, val):
        # initial PRODUCT_TITLE call
        if by == pp.PRODUCT_TITLE[0] and val == pp.PRODUCT_TITLE[1]:
            calls = getattr(driver, "_pt_calls", 0)
            driver._pt_calls = calls + 1
            if calls == 0:
                return [header]
            # subsequent title_elems fetch -> none for this test
            return []
        # call for images via UIAUTOMATOR -> return two image placeholders
        if by == AppiumBy.ANDROID_UIAUTOMATOR and val == pp.PRODUCT_IMAGE_UIAUTOMATOR_BASE:
            img1 = MagicMock(); type(img1).text = ""
            img2 = MagicMock(); type(img2).text = ""
            return [img1, img2]
        # simulate the global XPATH search: if xpath contains productIV or 'Product Image', return two text nodes
        if by == AppiumBy.XPATH and ("productIV" in val or "Product Image" in val):
            t1 = make_elem_with_text("Image Prod 1")
            t2 = make_elem_with_text("Image Prod 2")
            return [t1, t2]
        return []
    driver.find_elements.side_effect = find_elems

    titles = pp.get_all_product_titles()
    assert titles == ["Image Prod 1", "Image Prod 2"]
