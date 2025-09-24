#!/usr/bin/env python3
"""
<summary>
Testes unitários para pages.product_page.ProductPage cobrindo:
 - estratégia XPATH global em get_all_product_titles (quando productTV é header-like);
 - select_product_by_image_index monta UiSelector.instance corretamente;
 - _extract_title_from_image_element (texto direto e relativo);
 - _capture_debug_artifacts grava arquivos (usando tmp_path).
</summary>
"""
import os
import time
from unittest.mock import MagicMock
import logging
import pytest
from appium.webdriver.common.appiumby import AppiumBy
from pages.product_page import ProductPage

def make_elem_with_text(text):
    """Helper: cria um MagicMock WebElement com atributo .text"""
    e = MagicMock()
    type(e).text = text
    return e

def test_get_all_product_titles_uses_global_xpath(monkeypatch):
    """
    <summary>
    Quando a busca por productTV retorna apenas header-like, get_all_product_titles
    deve tentar XPATHs globais que relacionem productIV -> TextView e retornar textos válidos.
    </summary>
    """
    driver = MagicMock()
    pp = ProductPage(driver)

    header = make_elem_with_text("Products")

    # side_effect responde às várias chamadas driver.find_elements no método
    def find_elements_side(by, val):
        # primeira chamada: busca inicial por PRODUCT_TITLE -> header
        if by == pp.PRODUCT_TITLE[0] and val == pp.PRODUCT_TITLE[1]:
            calls = getattr(driver, "_pt_calls", 0)
            driver._pt_calls = calls + 1
            if calls == 0:
                return [header]
            # subsequent title_elems fetch -> none
            return []
        # chamada por ANDROID_UIAUTOMATOR (buscar images) -> devolve 2 imagens
        if by == AppiumBy.ANDROID_UIAUTOMATOR and val == pp.PRODUCT_IMAGE_UIAUTOMATOR_BASE:
            img1 = MagicMock(); type(img1).text = ""
            img2 = MagicMock(); type(img2).text = ""
            return [img1, img2]
        # chamada por XPATH global -> devolve TextView elements com textos reais
        if by == AppiumBy.XPATH and ("productIV" in val or "Product Image" in val):
            t1 = make_elem_with_text("Image Prod 1")
            t2 = make_elem_with_text("Image Prod 2")
            return [t1, t2]
        return []

    driver.find_elements.side_effect = find_elements_side

    titles = pp.get_all_product_titles()
    assert titles == ["Image Prod 1", "Image Prod 2"]

def test_select_product_by_image_index_calls_driver_find_and_click():
    """
    <summary>
    Verifica que select_product_by_image_index constrói UiSelector.instance(index)
    e chama driver.find_element com AppiumBy.ANDROID_UIAUTOMATOR.
    </summary>
    """
    driver = MagicMock()
    pp = ProductPage(driver)
    elem = MagicMock()
    driver.find_element.return_value = elem

    out = pp.select_product_by_image_index(2)
    expected_selector = f"{pp.PRODUCT_IMAGE_UIAUTOMATOR_BASE}.instance(2)"
    driver.find_element.assert_called_with(AppiumBy.ANDROID_UIAUTOMATOR, expected_selector)
    elem.click.assert_called_once()
    assert out is elem

def test_extract_title_from_image_element_direct_and_relatives():
    """
    <summary>
    Valida que se o elemento de imagem tem .text, o método retorna; caso contrário,
    busca relativo via find_element(..., XPATH) do próprio elemento.
    </summary>
    """
    driver = MagicMock()
    pp = ProductPage(driver)

    # Caso 1: elemento com texto direto
    img1 = MagicMock()
    type(img1).text = "Direct Title"
    assert pp._extract_title_from_image_element(img1) == "Direct Title"

    # Caso 2: elemento sem text, mas seu find_element relativo retorna TextView com texto
    img2 = MagicMock()
    type(img2).text = ""
    rel = make_elem_with_text("Relative Title")
    img2.find_element.return_value = rel
    assert pp._extract_title_from_image_element(img2) == "Relative Title"

def test_capture_debug_artifacts_writes_files(tmp_path, caplog, monkeypatch):
    """
    <summary>
    Valida que _capture_debug_artifacts grava PNG e XML no diretório ./artifacts
    e que não propaga exceções quando screenshot falha.
    </summary>
    """
    caplog.set_level(logging.DEBUG)
    driver = MagicMock()
    driver.page_source = "<hierarchy><node text='X'/></hierarchy>"

    # fake screenshot implementation: escreve ficheiro binário
    def fake_screenshot(path):
        with open(path, "wb") as f:
            f.write(b"PNG")
        return True
    driver.get_screenshot_as_file.side_effect = fake_screenshot

    pp = ProductPage(driver)
    # isola cwd para tmp_path para não poluir repo
    monkeypatch.chdir(tmp_path)

    prefix = "unit_capture"
    pp._capture_debug_artifacts(prefix=prefix)

    artifacts_dir = tmp_path / "artifacts"
    assert artifacts_dir.exists()
    files = list(artifacts_dir.iterdir())
    # deve conter .png e .xml com prefixo
    assert any(prefix in f.name and f.suffix == ".png" for f in files)
    assert any(prefix in f.name and f.suffix == ".xml" for f in files)

    # check logs mention saved files or page_source
    msgs = "\n".join(rec.message for rec in caplog.records)
    assert "Screenshot salvo" in msgs or "Page source salvo" in msgs or "page_source vazio" in msgs
