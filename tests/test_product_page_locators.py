#!/usr/bin/env python3
"""
<summary>
Testes unitários focados no uso do locator UiSelector(resourceId=productIV).
Cobrem:
 - fallback de get_all_product_titles chamando driver.find_elements com ANDROID_UIAUTOMATOR e selector base;
 - select_product_by_image_index chamando driver.find_element com ANDROID_UIAUTOMATOR e instance(index);
 - extração de título via _extract_title_from_image_element (direto e relativo).
</summary>
"""
from unittest.mock import MagicMock
import pytest
from appium.webdriver.common.appiumby import AppiumBy
from pages.product_page import ProductPage

def make_elem_with_text(text):
    """Helper: cria um MagicMock WebElement com atributo .text"""
    e = MagicMock()
    type(e).text = text
    return e

def test_select_product_by_image_index_uses_instance_selector():
    driver = MagicMock()
    pp = ProductPage(driver)

    # Mock do elemento retornado pelo find_element
    elem = MagicMock()
    driver.find_element.return_value = elem

    # Seleciona o produto de índice 2 (0-based) -> instance(2)
    returned = pp.select_product_by_image_index(2)

    # Verifica que find_element foi chamado com AppiumBy.ANDROID_UIAUTOMATOR e selector com .instance(2)
    expected_selector = f"{pp.PRODUCT_IMAGE_UIAUTOMATOR_BASE}.instance(2)"
    driver.find_element.assert_called_with(AppiumBy.ANDROID_UIAUTOMATOR, expected_selector)

    # Verifica que o elemento foi clicado e retornado
    elem.click.assert_called_once()
    assert returned is elem

def test_get_all_product_titles_fallback_uses_android_uiautomator_and_extracts_titles():
    driver = MagicMock()
    pp = ProductPage(driver)

    # 1) Simula retorno "header-like" quando o código busca por PRODUCT_TITLE (ex.: ["Products"])
    header_elem = make_elem_with_text("Products")
    # driver.find_elements será chamado primeiro com PRODUCT_TITLE e depois com ANDROID_UIAUTOMATOR
    def find_elements_side(by, val):
        if by == pp.PRODUCT_TITLE[0] and val == pp.PRODUCT_TITLE[1]:
            return [header_elem]
        if by == AppiumBy.ANDROID_UIAUTOMATOR and val == pp.PRODUCT_IMAGE_UIAUTOMATOR_BASE:
            # Cria dois "image" elements que não têm .text mas têm find_element relativo retornando TextView com text
            img1 = MagicMock()
            type(img1).text = ""  # sem texto direto
            rel1 = make_elem_with_text("Image Prod 1")
            img1.find_element.return_value = rel1

            img2 = MagicMock()
            type(img2).text = ""  # sem texto direto
            rel2 = make_elem_with_text("Image Prod 2")
            img2.find_element.return_value = rel2

            return [img1, img2]
        return []

    driver.find_elements.side_effect = find_elements_side

    titles = pp.get_all_product_titles()

    # Verifica que a chamada de fallback usou ANDROID_UIAUTOMATOR e o selector base
    # (o side_effect garante que a chamada foi feita conforme o branch)
    assert titles == ["Image Prod 1", "Image Prod 2"]

def test__extract_title_from_image_element_prefers_direct_text_then_relatives():
    driver = MagicMock()
    pp = ProductPage(driver)

    # Caso 1: imagem com texto direto
    img_with_text = MagicMock()
    type(img_with_text).text = "Direct Title"
    assert pp._extract_title_from_image_element(img_with_text) == "Direct Title"

    # Caso 2: imagem sem text, mas find_element relativo retorna um TextView com texto
    img_no_text = MagicMock()
    type(img_no_text).text = ""
    rel_elem = make_elem_with_text("Relative Title")
    img_no_text.find_element.return_value = rel_elem
    assert pp._extract_title_from_image_element(img_no_text) == "Relative Title"

def test_get_all_product_titles_filters_header_and_uses_images():
    """
    <summary>
    Quando title_elems inclui um header-like na posição 0 e existem img_elems,
    o método deve ignorar esse header e extrair o título a partir do img_elems[0].
    </summary>
    """
    driver = MagicMock()
    pp = ProductPage(driver)

    # Simula primeira chamada por PRODUCT_TITLE retornando header-like
    header = make_elem_with_text("Products")

    # Simula dois image elements (sem text) que têm elementos relativos com texto
    img1 = MagicMock(); type(img1).text = ""
    rel1 = make_elem_with_text("Image Prod 1")
    img1.find_element.return_value = rel1

    img2 = MagicMock(); type(img2).text = ""
    rel2 = make_elem_with_text("Image Prod 2")
    img2.find_element.return_value = rel2

    # Simula title_elems contendo apenas o header (ex.: primeiro call returned header)
    def find_elements_side(by, val):
        if by == pp.PRODUCT_TITLE[0] and val == pp.PRODUCT_TITLE[1]:
            # When called first time -> header (to trigger fallback)
            calls = getattr(driver, "_calls", 0)
            if calls == 0:
                driver._calls = calls + 1
                return [header]
            # When called later to fetch title_elems -> return same header (simulate small title_elems)
            return [header]
        if by == AppiumBy.ANDROID_UIAUTOMATOR and val == pp.PRODUCT_IMAGE_UIAUTOMATOR_BASE:
            return [img1, img2]
        return []

    driver.find_elements.side_effect = find_elements_side

    titles = pp.get_all_product_titles()
    assert titles == ["Image Prod 1", "Image Prod 2"]

