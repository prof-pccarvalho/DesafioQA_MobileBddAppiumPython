import pytest
from unittest.mock import MagicMock, call
from pages.product_page import ProductPage
from appium.webdriver.common.appiumby import AppiumBy

def make_elem_with_text(text):
    """Helper: cria um MagicMock WebElement com atributo .text"""
    e = MagicMock()
    type(e).text = text
    return e

def test_get_all_product_titles_direct():
    driver = MagicMock()
    # Simula elementos de título com textos
    elems = [make_elem_with_text("Prod A"), make_elem_with_text("Prod B")]
    driver.find_elements.return_value = elems
    pp = ProductPage(driver)
    titles = pp.get_all_product_titles()
    assert titles == ["Prod A", "Prod B"]
    # Verifica que a chamada inicial buscou pelo locator PRODUCT_TITLE
    driver.find_elements.assert_called_with(pp.PRODUCT_TITLE[0], pp.PRODUCT_TITLE[1])

def test_get_all_product_titles_fallback_to_images():
    """
    <summary>
    Quando a busca por PRODUCT_TITLE retornar apenas um header-like item,
    o método deve fazer fallback para buscar imagens usando ANDROID_UIAUTOMATOR
    com o selector PRODUCT_IMAGE_UIAUTOMATOR_BASE e extrair títulos relativos.
    </summary>
    """
    driver = MagicMock()
    pp = ProductPage(driver)

    # 1) Primeiro find_elements por PRODUCT_TITLE retorna um header-like (ex.: "Products")
    header_elem = make_elem_with_text("Products")

    # 2) Quando chamado com ANDROID_UIAUTOMATOR e o selector base retornamos "image" elements.
    # Cada "image" tem .text vazio, mas sua chamada .find_element(..., xpath_rel) retorna um TextView com texto.
    img1 = MagicMock()
    type(img1).text = ""
    rel1 = make_elem_with_text("Image Prod 1")
    img1.find_element.return_value = rel1

    img2 = MagicMock()
    type(img2).text = ""
    rel2 = make_elem_with_text("Image Prod 2")
    img2.find_element.return_value = rel2

    # implementa side_effect que responde aos dois tipos de chamada find_elements que ProductPage faz
    def find_elements_side(by, val):
        # chamada direta por PRODUCT_TITLE
        if by == pp.PRODUCT_TITLE[0] and val == pp.PRODUCT_TITLE[1]:
            return [header_elem]
        # fallback via UiSelector(resourceId=productIV)
        if by == AppiumBy.ANDROID_UIAUTOMATOR and val == pp.PRODUCT_IMAGE_UIAUTOMATOR_BASE:
            return [img1, img2]
        return []

    driver.find_elements.side_effect = find_elements_side

    titles = pp.get_all_product_titles()

    # Esperamos os títulos extraídos a partir dos elementos relativos retornados por imgX.find_element(...)
    assert titles == ["Image Prod 1", "Image Prod 2"]

def test__extract_title_from_image_element_text_and_relatives():
    driver = MagicMock()
    pp = ProductPage(driver)

    # Caso 1: imagem tem .text diretamente
    img = MagicMock()
    type(img).text = "Direct Title"
    assert pp._extract_title_from_image_element(img) == "Direct Title"

    # Caso 2: imagem sem text, mas find_element retorna relativo com text
    img2 = MagicMock()
    type(img2).text = ""
    rel_elem = MagicMock()
    type(rel_elem).text = "Relative Title"
    # configurar find_element para retornar rel_elem para qualquer XPATH pedido
    img2.find_element.return_value = rel_elem
    assert pp._extract_title_from_image_element(img2) == "Relative Title"

def test_get_product_title_by_index_and_select_product():
    driver = MagicMock()
    e1 = MagicMock()
    type(e1).text = "A"
    e2 = MagicMock()
    type(e2).text = "B"
    driver.find_elements.return_value = [e1, e2]
    pp = ProductPage(driver)
    assert pp.get_product_title_by_index(0) == "A"
    # select e click
    clicked = pp.select_product(1)
    e2.click.assert_called_once()
    assert clicked == e2
    # invalid index raises
    with pytest.raises(IndexError):
        pp.get_product_title_by_index(5)
    with pytest.raises(IndexError):
        pp.select_product(-1)

def test_select_product_by_image_index_calls_driver_find_element_and_click():
    """
    <summary>
    Valida que select_product_by_image_index monta o UiSelector com .instance(index)
    e chama driver.find_element com AppiumBy.ANDROID_UIAUTOMATOR, clicando no elemento retornado.
    </summary>
    """
    driver = MagicMock()
    pp = ProductPage(driver)

    # Mock do elemento retornado pelo find_element
    elem = MagicMock()
    driver.find_element.return_value = elem

    # Seleciona o produto de índice 2 (0-based) -> instance(2)
    returned = pp.select_product_by_image_index(2)

    # Verifica que find_element foi chamado com ANDROID_UIAUTOMATOR e selector com .instance(2)
    expected_selector = f"{pp.PRODUCT_IMAGE_UIAUTOMATOR_BASE}.instance(2)"
    driver.find_element.assert_called_with(AppiumBy.ANDROID_UIAUTOMATOR, expected_selector)

    # Verifica que o elemento foi clicado e retornado
    elem.click.assert_called_once()
    assert returned is elem
    
def test_compare_products_uses_cache_and_collect(monkeypatch):
    driver = MagicMock()
    pp = ProductPage(driver)
    # define cache suficiente
    pp._last_collected_titles = ["A", "B", "C"]
    res = pp.compare_products(0, 1)
    assert res["product_a"] == "A"
    assert res["product_b"] == "B"
    assert res["equal"] is False

    # quando cache insuficiente, ensure collect_product_titles called
    def fake_collect(min_count, max_scrolls, wait_after_scroll):
        return ["X", "X"]
    monkeypatch.setattr(pp, "collect_product_titles", fake_collect)
    # remove cache
    if hasattr(pp, "_last_collected_titles"):
        del pp._last_collected_titles
    res2 = pp.compare_products(0, 1)
    assert res2["equal"] is True

def test_collect_product_titles_accumulates_and_caches(monkeypatch):
    driver = MagicMock()
    pp = ProductPage(driver)
    # Simula sequência de telas visíveis após cada chamada a get_all_product_titles
    seq = [
        ["Products"],           # primeira chamada -> header-like (ignored)
        ["P1"],                 # após 1º scroll
        ["P1", "P2"],           # após 2º scroll (novo item)
    ]
    calls = {"i": 0}
    def fake_get_all():
        i = calls["i"]
        calls["i"] += 1
        return seq[min(i, len(seq)-1)]
    monkeypatch.setattr(pp, "get_all_product_titles", fake_get_all)
    # Faz _scroll_forward True duas vezes, depois False
    sc_seq = [True, True, False]
    sc_calls = {"i":0}
    def fake_scroll():
        i = sc_calls["i"]
        sc_calls["i"] += 1
        return sc_seq[min(i, len(sc_seq)-1)]
    monkeypatch.setattr(pp, "_scroll_forward", fake_scroll)

    titles = pp.collect_product_titles(min_count=2, max_scrolls=3, wait_after_scroll=0)
    # deve ter coletado P1, P1, P2 (não remove duplicatas), mas filtra header-like
    assert "P1" in titles
    assert "P2" in titles
    # cache deve ter sido atualizado
    assert getattr(pp, "_last_collected_titles", None) is not None
