#!/usr/bin/env python3
"""
<summary>
Page Object para a tela de catálogo de produtos com estratégias robustas
de extração de títulos, suporte a seleção por imagem (UiSelector.instance),
mecanismo de captura de artifacts (screenshot + page_source) e logging detalhado.
</summary>
"""
from typing import List, Tuple
import time
import os
import logging
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from appium.webdriver.common.appiumby import AppiumBy

# Logger do módulo — herdará configuração definida pela suíte de testes / behave
logger = logging.getLogger(__name__)


class ProductPage:
    """
    <summary>
    Page Object para a tela de catálogo de produtos.
    Fornece métodos para:
      - coletar títulos visíveis (get_all_product_titles) com múltiplas estratégias de fallback;
      - selecionar produtos por índice (título ou imagem);
      - rolar/collect e comparar produtos;
      - captura de artifacts para diagnóstico (_capture_debug_artifacts).
    </summary>
    <param name="driver">Instância do WebDriver/Appium</param>
    """

    # Locator para o título do produto (TextView)
    PRODUCT_TITLE: Tuple[str, str] = (AppiumBy.ID, "com.saucelabs.mydemoapp.android:id/productTV")

    # UiSelector base para localizar imagens dos produtos (productIV).
    # Para selecionar por índice: use f"{PRODUCT_IMAGE_UIAUTOMATOR_BASE}.instance(N)"
    PRODUCT_IMAGE_UIAUTOMATOR_BASE: str = 'new UiSelector().resourceId("com.saucelabs.mydemoapp.android:id/productIV")'

    def __init__(self, driver: WebDriver, default_wait_seconds: int = 5) -> None:
        """
        <summary>
        Inicializa ProductPage com driver Appium.
        </summary>
        <param name="driver">WebDriver/Appium</param>
        <param name="default_wait_seconds">Timeout padrão (segundos) usado em alguns helpers</param>
        <returns>None</returns>
        """
        # Salva instância do driver e tempo padrão
        self.driver = driver
        self.default_wait_seconds = default_wait_seconds

    def _capture_debug_artifacts(self, prefix: str = "product_debug") -> None:
        """
        <summary>
        Captura artifacts de diagnóstico no diretório ./artifacts:
          - screenshot (chama driver.get_screenshot_as_file)
          - page_source (escreve driver.page_source em XML)
        Não propaga exceções se falhar; apenas registra.
        </summary>
        <param name="prefix">Prefixo para os ficheiros gerados</param>
        <returns>None</returns>
        """
        artifacts_dir = os.path.join(os.getcwd(), "artifacts")
        try:
            os.makedirs(artifacts_dir, exist_ok=True)
        except Exception as exc:
            logger.exception("Não foi possível criar artifacts_dir '%s': %s", artifacts_dir, exc)
            return

        ts = int(time.time())
        png_path = os.path.join(artifacts_dir, f"{prefix}_{ts}.png")
        xml_path = os.path.join(artifacts_dir, f"{prefix}_{ts}.xml")

        # Tenta salvar screenshot
        try:
            ok = False
            try:
                ok = bool(self.driver.get_screenshot_as_file(png_path))
            except TypeError:
                # Alguns drivers/mocks retornam None — consideramos sucesso se não lançar
                ok = True
            if ok:
                logger.debug("_capture_debug_artifacts: Screenshot salvo em %s", png_path)
            else:
                logger.warning("_capture_debug_artifacts: driver.get_screenshot_as_file retornou False ao salvar em %s", png_path)
        except Exception as exc:
            logger.exception("_capture_debug_artifacts: Falha ao salvar screenshot em '%s': %s", png_path, exc)

        # Tenta salvar page_source
        try:
            src = ""
            try:
                src = self.driver.page_source
            except Exception as exc:
                logger.exception("_capture_debug_artifacts: Falha ao obter page_source: %s", exc)
                src = ""
            if src:
                try:
                    with open(xml_path, "w", encoding="utf-8") as f:
                        f.write(src)
                    logger.debug("_capture_debug_artifacts: Page source salvo em %s", xml_path)
                except Exception as exc:
                    logger.exception("_capture_debug_artifacts: Falha ao gravar page_source em '%s': %s", xml_path, exc)
            else:
                logger.warning("_capture_debug_artifacts: page_source vazio; não gravado em %s", xml_path)
        except Exception:
            logger.exception("_capture_debug_artifacts: Erro inesperado ao tentar salvar page_source (ignorado).")

    def _find_product_elements(self) -> List[WebElement]:
        """
        <summary>
        Recupera WebElements dos títulos de produtos atualmente visíveis.
        </summary>
        <returns>Lista de WebElement</returns>
        """
        # Usa driver.find_elements com o locator ID conhecido
        return self.driver.find_elements(self.PRODUCT_TITLE[0], self.PRODUCT_TITLE[1])

    def get_product_title_by_index(self, index: int) -> str:
        """
        <summary>
        Retorna o título do produto pelo índice 0-based usando os elementos de título.
        </summary>
        <param name="index">Índice 0-based</param>
        <returns>String com o título</returns>
        <raises>IndexError se índice fora do intervalo</raises>
        """
        elems = self._find_product_elements()
        if index < 0 or index >= len(elems):
            raise IndexError(f"Índice de produto fora do intervalo: {index} (total: {len(elems)})")
        return elems[index].text

    def select_product(self, index: int) -> WebElement:
        """
        <summary>
        Clica no produto pelo índice 0-based (baseado no elemento de título) e retorna o WebElement clicado.
        </summary>
        <param name="index">Índice 0-based</param>
        <returns>WebElement clicado</returns>
        """
        elems = self._find_product_elements()
        if index < 0 or index >= len(elems):
            raise IndexError(f"Índice de produto fora do intervalo: {index} (total: {len(elems)})")
        el = elems[index]
        el.click()
        return el

    def select_product_by_image_index(self, index: int) -> WebElement:
        """
        <summary>
        Seleciona um produto clicando na imagem correspondente usando UiSelector.instance(index).
        Usa AppiumBy.ANDROID_UIAUTOMATOR com a expressão construída.
        </summary>
        <param name="index">Índice 0-based</param>
        <returns>WebElement clicado</returns>
        """
        # Constrói selector UiSelector com instance (0-based)
        ui_selector = f"{self.PRODUCT_IMAGE_UIAUTOMATOR_BASE}.instance({index})"
        logger.debug("select_product_by_image_index: buscando imagem com UiSelector '%s'", ui_selector)
        elem = self.driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR, ui_selector)
        elem.click()
        logger.debug("select_product_by_image_index: clicado elemento para índice %d", index)
        return elem

    def _extract_title_from_image_element(self, img_elem) -> str:
        """
        <summary>
        Tenta extrair título relativo a um elemento de imagem:
          1) verifica img_elem.text;
          2) tenta buscas relativas (XPath) a partir do elemento (quando suportado);
          3) retorna string vazia se não encontrar.
        </summary>
        <param name="img_elem">WebElement da imagem</param>
        <returns>Texto do título se encontrado, senão string vazia</returns>
        """
        # 1) tenta acessar .text diretamente
        try:
            txt = getattr(img_elem, "text", None)
            if txt and str(txt).strip():
                val = str(txt).strip()
                logger.debug("_extract_title_from_image_element: texto direto encontrado '%s'", val)
                return val
        except Exception:
            logger.debug("_extract_title_from_image_element: falha ao acessar .text", exc_info=True)

        # 2) tenta buscas relativas a partir do elemento (nem todos os drivers suportam)
        relatives = [
            "./following-sibling::android.widget.TextView",
            "./../following-sibling::android.widget.TextView",
            "ancestor::android.view.ViewGroup//android.widget.TextView",
            "ancestor::android.view.ViewGroup//android.widget.TextView[@resource-id='com.saucelabs.mydemoapp.android:id/productTV']",
        ]
        for rel in relatives:
            try:
                t_elem = img_elem.find_element(AppiumBy.XPATH, rel)
                t_text = getattr(t_elem, "text", "") or ""
                s = str(t_text).strip()
                if s:
                    logger.debug("_extract_title_from_image_element: texto relativo via '%s' => '%s'", rel, s)
                    return s
            except Exception:
                logger.debug("_extract_title_from_image_element: relação '%s' não produziu resultado", rel)
                continue

        # fallback: nada encontrado
        logger.debug("_extract_title_from_image_element: não encontrou título relativo")
        return ""

    def get_all_product_titles(self) -> List[str]:
        """
        <summary>
        Retorna os títulos (strings) de todos os produtos visíveis.
        Estratégia:
          1) tenta coletar elements productTV por ID;
          2) se resultado parecer header-like/insuficiente -> ativa fallback:
             2.a) tenta localizar image elements via UiSelector(productIV);
             2.b) TENTA PRIMEIRO pesquisas GLOBAIS por XPATHs que relacionam productIV -> TextView
                 (aplicadas no driver: driver.find_elements(AppiumBy.XPATH, xpath));
             2.c) se (2.b) não retornar resultado, procede com mapping híbrido já existente:
                   - tenta title_elems por índice quando válidos;
                   - para indices sem title válido tenta extrair do img_elem (.text ou busca relativa).
        Esta função emite logs detalhados para diagnóstico.
        </summary>
        <returns>Lista de títulos visíveis (pode conter strings vazias se não extraídas)</returns>
        """
        logger.debug("get_all_product_titles: início da coleta de títulos")
        # 1) tentativa direta por ID (productTV)
        try:
            elems = self.driver.find_elements(self.PRODUCT_TITLE[0], self.PRODUCT_TITLE[1])
        except Exception as exc:
            logger.exception("get_all_product_titles: falha ao buscar productTV por ID: %s", exc)
            elems = []

        titles: List[str] = []
        for el in elems:
            try:
                titles.append(el.text or "")
            except Exception:
                titles.append("")

        logger.debug("get_all_product_titles: títulos iniciais coletados %s", titles)

        # Detecta header-like (p.ex. apenas "Products" listado)
        header_like = (len(titles) <= 1) and any(t.strip().lower() in ("products", "product", "") for t in titles)
        if not titles or header_like:
            logger.debug("get_all_product_titles: fallback ativado (header_like=%s, count_titles=%d)", header_like, len(titles))

            # a) localizar imagens productIV via ANDROID_UIAUTOMATOR
            try:
                img_elems = self.driver.find_elements(AppiumBy.ANDROID_UIAUTOMATOR, self.PRODUCT_IMAGE_UIAUTOMATOR_BASE)
                logger.debug("get_all_product_titles: %d elementos de imagem encontrados via UiSelector", len(img_elems))
            except Exception as exc:
                logger.exception("get_all_product_titles: falha ao buscar imagens via UiSelector: %s", exc)
                img_elems = []

            if not img_elems:
                logger.debug("get_all_product_titles: nenhuma imagem encontrada; retornando títulos iniciais")
                return [] if header_like else titles

            # ---------- NOVO: busca global por XPATHs relacionando productIV -> TextView ----------
            # usa resource-id e content-desc observados no inspector
            product_iv_rid = "com.saucelabs.mydemoapp.android:id/productIV"
            product_tv_rid = "com.saucelabs.mydemoapp.android:id/productTV"
            xpath_candidates = [
                # sibling direto
                f"//android.widget.ImageView[@resource-id='{product_iv_rid}']/following-sibling::android.widget.TextView",
                # sibling via content-desc (fallback quando resource-id pode variar)
                f"//android.widget.ImageView[@content-desc='Product Image']/following-sibling::android.widget.TextView",
                # primeiro TextView seguindo a image (global)
                f"(//android.widget.ImageView[@resource-id='{product_iv_rid}'])/following::android.widget.TextView[1]",
                # TextView no mesmo parent
                f"//android.widget.ImageView[@resource-id='{product_iv_rid}']/parent::*/android.widget.TextView",
                f"//android.widget.ImageView[@content-desc='Product Image']/parent::*/android.widget.TextView",
                # TextView productTV dentro do ancestor viewgroup
                f"//android.widget.ImageView[@resource-id='{product_iv_rid}']/ancestor::android.view.ViewGroup//android.widget.TextView[@resource-id='{product_tv_rid}']",
            ]

            # Executa as buscas globais no driver; é mais confiável do que buscas relativas a partir do elemento em muitos drivers
            try:
                for xp in xpath_candidates:
                    try:
                        found = self.driver.find_elements(AppiumBy.XPATH, xp)
                        # extrai textos não vazios e não header-like
                        found_texts: List[str] = []
                        for fe in found:
                            try:
                                txt = str(fe.text or "").strip()
                                if txt and txt.lower() not in ("products", "product", ""):
                                    found_texts.append(txt)
                            except Exception:
                                continue
                        logger.debug("get_all_product_titles: xpath '%s' retornou textos %s", xp, found_texts)
                        if found_texts:
                            # Retorna imediatamente os textos válidos encontrados pela XPath global
                            return found_texts
                    except Exception:
                        logger.debug("get_all_product_titles: xpath '%s' falhou (ignorado)", xp, exc_info=True)
                        continue
            except Exception:
                logger.exception("get_all_product_titles: exceção ao executar buscas XPATH globais; prossegue para mapping híbrido")

            # ---------- se a busca global não obteve resultados, executa mapping híbrido ----------
            # tenta também ler title_elems (productTV) presentes na tela para mapear por índice
            try:
                title_elems = self.driver.find_elements(self.PRODUCT_TITLE[0], self.PRODUCT_TITLE[1])
            except Exception:
                title_elems = []

            # extrai textos de title_elems
            title_texts: List[str] = []
            for te in title_elems:
                try:
                    title_texts.append(str(te.text or "").strip())
                except Exception:
                    title_texts.append("")

            def _is_header(t: str) -> bool:
                if not t:
                    return True
                s = t.strip().lower()
                return s in ("", "products", "product",)

            # se existirem textos válidos suficientes, preferimos esses
            valid_title_texts = [t for t in title_texts if not _is_header(t)]
            if len(valid_title_texts) >= len(img_elems):
                logger.debug("get_all_product_titles: usando title_elems válidos (count=%d) em vez de extração por imagem", len(valid_title_texts))
                return valid_title_texts[:len(img_elems)]

            # mapping híbrido por índice: preferir title_texts[i] quando válido, senão extrair do img_elems[i]
            titles = []
            for i in range(len(img_elems)):
                chosen = ""
                if i < len(title_texts) and not _is_header(title_texts[i]):
                    chosen = title_texts[i]
                    logger.debug("get_all_product_titles: index %d -> usando title_elems text '%s'", i, chosen)
                else:
                    img = img_elems[i]
                    try:
                        txt = getattr(img, "text", None)
                        if txt and str(txt).strip():
                            chosen = str(txt).strip()
                            logger.debug("get_all_product_titles: index %d -> texto direto do img_elem '%s'", i, chosen)
                        else:
                            # último recurso: tenta busca relativa a partir do elemento (pode falhar em alguns drivers)
                            chosen = self._extract_title_from_image_element(img) or ""
                            logger.debug("get_all_product_titles: index %d -> texto extraído por relação '%s'", i, chosen)
                    except Exception as exc:
                        logger.exception("get_all_product_titles: falha extraindo título do img_elem index %d: %s", i, exc)
                        chosen = ""
                titles.append(chosen)
            logger.debug("get_all_product_titles: fallback resultante %s", titles)
            return titles

        # sem fallback necessário: retorna títulos coletados inicialmente
        logger.debug("get_all_product_titles: retornando títulos iniciais (sem fallback)")
        return titles

    def _scroll_forward(self) -> bool:
        """
        <summary>
        Tenta rolar a tela para frente usando múltiplos fallbacks:
         - UiScrollable via ANDROID_UIAUTOMATOR,
         - mobile: swipe / dragGesture / scroll,
         - driver.swipe legacy,
         - TouchAction fallback.
        Retorna True se algum método executou com sucesso (não garante novo conteúdo).
        </summary>
        <returns>True se rolou</returns>
        """
        logger.debug("_scroll_forward: tentativa de scroll iniciada")
        ui_scroll = 'new UiScrollable(new UiSelector().scrollable(true)).scrollForward()'
        try:
            self.driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR, ui_scroll)
            logger.debug("_scroll_forward: usado UiScrollable.scrollForward() com sucesso")
            return True
        except Exception:
            logger.debug("_scroll_forward: UiScrollable.scrollForward() não disponível / falhou")

        try:
            size = self.driver.get_window_size()
            start_x = size['width'] // 2
            start_y = int(size['height'] * 0.8)
            end_x = start_x
            end_y = int(size['height'] * 0.3)
        except Exception:
            start_x = start_y = end_x = end_y = None
            logger.debug("_scroll_forward: não conseguiu obter window size")

        if start_x is not None:
            try:
                params = {"startX": start_x, "startY": start_y, "endX": end_x, "endY": end_y, "duration": 500}
                self.driver.execute_script("mobile: swipe", params)
                logger.debug("_scroll_forward: executed mobile: swipe")
                return True
            except Exception:
                logger.debug("_scroll_forward: mobile: swipe falhou; tentando dragGesture/scroll")
            try:
                drag_params = {"startX": start_x, "startY": start_y, "endX": end_x, "endY": end_y, "speed": 1000}
                self.driver.execute_script("mobile: dragGesture", drag_params)
                logger.debug("_scroll_forward: executed mobile: dragGesture")
                return True
            except Exception:
                logger.debug("_scroll_forward: mobile: dragGesture falhou")
            try:
                scroll_params = {"direction": "down"}
                self.driver.execute_script("mobile: scroll", scroll_params)
                logger.debug("_scroll_forward: executed mobile: scroll")
                return True
            except Exception:
                logger.debug("_scroll_forward: mobile: scroll falhou")

        try:
            if start_x is not None and hasattr(self.driver, "swipe"):
                self.driver.swipe(start_x, start_y, end_x, end_y, 500)
                logger.debug("_scroll_forward: usado driver.swipe (legacy)")
                return True
        except Exception:
            logger.debug("_scroll_forward: driver.swipe falhou")

        try:
            from appium.webdriver.common.touch_action import TouchAction  # type: ignore
            try:
                TouchAction(self.driver).press(x=start_x, y=start_y).wait(ms=200).move_to(x=end_x, y=end_y).release().perform()
                logger.debug("_scroll_forward: usado TouchAction fallback")
                return True
            except Exception:
                logger.debug("_scroll_forward: TouchAction falhou")
        except Exception:
            logger.debug("_scroll_forward: TouchAction não disponível")

        logger.debug("_scroll_forward: nenhum método de scroll funcionou")
        return False

    def compare_products(self, index_a: int, index_b: int) -> dict:
        """
        <summary>
        Compara dois produtos usando a lista acumulada de títulos.
        Se cache interno (_last_collected_titles) satisfazer os índices, será usado.
        Caso contrário, coleta mais títulos via collect_product_titles.
        </summary>
        <param name="index_a">Índice 0-based A</param>
        <param name="index_b">Índice 0-based B</param>
        <returns>Dicionário com keys: product_a, product_b, equal (bool)</returns>
        <raises>IndexError se índices não disponíveis</raises>
        """
        required = max(index_a, index_b) + 1
        cached = getattr(self, "_last_collected_titles", None)
        if isinstance(cached, list) and len(cached) >= required:
            logger.debug("compare_products: usando cache com %d títulos", len(cached))
            accumulated_titles = cached
        else:
            logger.debug("compare_products: coletando ao menos %d títulos", required)
            accumulated_titles = self.collect_product_titles(min_count=required, max_scrolls=8, wait_after_scroll=self.default_wait_seconds * 0.1)

        logger.debug("compare_products: accumulated_titles=%s", accumulated_titles)
        if len(accumulated_titles) < required:
            logger.error("compare_products: insuficiente títulos (required=%d, found=%d)", required, len(accumulated_titles))
            raise IndexError(f"Índice de produto fora do intervalo: requer {required}, mas encontrou {len(accumulated_titles)}")

        title_a = accumulated_titles[index_a]
        title_b = accumulated_titles[index_b]
        return {"product_a": title_a, "product_b": title_b, "equal": (title_a == title_b)}

    def ensure_minimum_products(self, min_count: int, max_scrolls: int = 8, wait_after_scroll: float = 0.6) -> int:
        """
        <summary>
        Garante que pelo menos min_count títulos sejam encontrados (com scrolls).
        Retorna o total final de títulos encontrados.
        </summary>
        <returns>Quantidade final</returns>
        """
        logger.debug("ensure_minimum_products: solicitando mínimo %d produtos", min_count)
        titles = self.collect_product_titles(min_count=min_count, max_scrolls=max_scrolls, wait_after_scroll=wait_after_scroll)
        logger.debug("ensure_minimum_products: encontrou %d títulos", len(titles))
        return len(titles)

    def collect_product_titles(self, min_count: int, max_scrolls: int = 6, wait_after_scroll: float = 0.6) -> List[str]:
        """
        <summary>
        Coleta e acumula títulos navegando pelo catálogo até atingir min_count ou max_scrolls.
        Retorna a lista acumulada (cacheada em self._last_collected_titles).
        </summary>
        <returns>Lista de títulos coletados</returns>
        """
        logger.debug("collect_product_titles: início com min_count=%d max_scrolls=%d", min_count, max_scrolls)
        accumulated: List[str] = []
        consecutive_no_new = 0

        def _is_header_like(t: str) -> bool:
            if not t:
                return True
            s = t.strip().lower()
            return s in ("", "products", "product", "title", "catalog")

        # coleta inicial
        visible = self.get_all_product_titles()
        logger.debug("collect_product_titles: títulos visíveis iniciais: %s", visible)
        for t in visible:
            if not _is_header_like(t):
                accumulated.append(t)

        if len(accumulated) >= min_count:
            self._last_collected_titles = list(accumulated)
            logger.debug("collect_product_titles: satisfez min_count com viewport inicial")
            return accumulated

        # itera com scrolls
        for attempt in range(max_scrolls):
            logger.debug("collect_product_titles: tentativa de scroll #%d", attempt + 1)
            scrolled = self._scroll_forward()
            if not scrolled:
                logger.debug("collect_product_titles: _scroll_forward retornou False; abortando")
                break

            time.sleep(wait_after_scroll)
            visible = self.get_all_product_titles()
            logger.debug("collect_product_titles: visíveis após scroll #%d -> %s", attempt + 1, visible)
            before = len(accumulated)
            for t in visible:
                if not _is_header_like(t):
                    accumulated.append(t)
            added = len(accumulated) - before
            logger.debug("collect_product_titles: adicionados nesta iteração: %d (total agora %d)", added, len(accumulated))

            if added > 0:
                consecutive_no_new = 0
            else:
                consecutive_no_new += 1

            if len(accumulated) >= min_count:
                self._last_collected_titles = list(accumulated)
                logger.debug("collect_product_titles: atingiu min_count=%d", min_count)
                return accumulated

            if consecutive_no_new >= 2:
                logger.debug("collect_product_titles: sem novos itens por %d iterações, abortando", consecutive_no_new)
                break

        self._last_collected_titles = list(accumulated)
        logger.debug("collect_product_titles: finalizando com total %d", len(accumulated))
        return accumulated
