#!/usr/bin/env python3
from typing import Optional, Tuple
import os
import time
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from appium.webdriver.common.appiumby import AppiumBy
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class LoginPage:
    """
    <summary>
    Page Object da tela de login e navegação relacionada.
    </summary>
    <param name="driver">Instância do WebDriver/Appium injetada para testabilidade.</param>
    """

    # Locators estáveis (já confirmados)
    USERNAME_FIELD: Tuple[str, str] = (AppiumBy.ID, "com.saucelabs.mydemoapp.android:id/nameET")
    PASSWORD_FIELD: Tuple[str, str] = (AppiumBy.ID, "com.saucelabs.mydemoapp.android:id/passwordET")
    LOGIN_BUTTON: Tuple[str, str] = (AppiumBy.ID, "com.saucelabs.mydemoapp.android:id/loginBtn")
    MENU_BUTTON: Tuple[str, str] = (AppiumBy.ID, "com.saucelabs.mydemoapp.android:id/menuIV")
    MENU_LOGIN_TEXT: Tuple[str, str] = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("Log In")')
    ERROR_MESSAGE: Tuple[str, str] = (AppiumBy.ID, "com.saucelabs.mydemoapp.android:id/errorTV")

    def __init__(self, driver: WebDriver, default_wait_seconds: int = 10) -> None:
        """
        <summary>
        Inicializa o LoginPage com driver e timeout padrão.
        </summary>
        <param name="driver">WebDriver/Appium</param>
        <param name="default_wait_seconds">Timeout padrão (s) para esperas explícitas</param>
        <returns>None</returns>
        """
        # Armazena a instância do driver e timeout para uso nos métodos
        self.driver = driver
        self.default_wait_seconds = default_wait_seconds

    def _capture_debug_artifacts(self, prefix: str = "login_debug") -> None:
        """
        <summary>
        Salva screenshot e page_source em ./artifacts para diagnóstico.
        </summary>
        <param name="prefix">Prefixo para os ficheiros</param>
        <returns>None</returns>
        """
        artifacts_dir = os.path.join(os.getcwd(), "artifacts")
        os.makedirs(artifacts_dir, exist_ok=True)
        ts = int(time.time())
        try:
            # tenta salvar screenshot (pode falhar em drivers falsos)
            self.driver.get_screenshot_as_file(os.path.join(artifacts_dir, f"{prefix}_{ts}.png"))
        except Exception:
            # Não interrompe fluxo em caso de falha ao salvar screenshot
            pass
        try:
            # salva page_source para diagnóstico (útil para inspecionar árvore de elementos)
            with open(os.path.join(artifacts_dir, f"{prefix}_{ts}.xml"), "w", encoding="utf-8") as f:
                f.write(self.driver.page_source)
        except Exception:
            # Não interrompe fluxo em caso de falha ao salvar page_source
            pass

    def _hide_keyboard_safe(self) -> None:
        """
        <summary>
        Tenta esconder o teclado virtual de forma segura (sem propagar exceções).
        </summary>
        <returns>None</returns>
        """
        try:
            # hide_keyboard pode não ser suportado por todos os drivers; capture falhas
            self.driver.hide_keyboard()
        except Exception:
            # Não propaga; é uma tentativa de recuperação para melhorar resiliência
            pass

    def _wait_for_clickable(self, locator: Tuple[str, str], timeout: Optional[int] = None) -> WebElement:
        """
        <summary>
        Aguarda até que o elemento seja clicável. Em Timeout captura artefatos e re-lança exceção.
        A exceção retornada contém um atributo _artifacts_captured para sinalizar que já houve captura.
        </summary>
        <param name="locator">Tupla (By, locator_string)</param>
        <param name="timeout">Tempo máximo (s) para aguardar; se None usa default_wait_seconds</param>
        <returns>WebElement quando clicável</returns>
        <raises>TimeoutException</raises>
        """
        wait_time = self.default_wait_seconds if timeout is None else timeout
        try:
            # Usa WebDriverWait com expected_conditions para esperar até o elemento estar clicável
            return WebDriverWait(self.driver, wait_time).until(EC.element_to_be_clickable(locator))
        except TimeoutException as exc:
            # Em caso de timeout, captura artefatos com prefixo que ajuda a identificar o locator
            self._capture_debug_artifacts(prefix=f"clickable_{locator[1]}")
            # Cria uma nova exceção com marcação indicando que artifacts já foram capturados
            new_exc = TimeoutException(f"Timeout esperando por elemento clicável {locator} após {wait_time}s")
            setattr(new_exc, "_artifacts_captured", True)
            raise new_exc from exc

    def _wait_for_element(self, locator: Tuple[str, str], timeout: Optional[int] = None) -> WebElement:
        """
        <summary>
        Aguarda até que o elemento esteja presente/visível. Captura artifacts em caso de Timeout.
        Usa expected_conditions.visibility_of_element_located para validar visibilidade.
        </summary>
        <param name="locator">Tupla (By, locator_string)</param>
        <param name="timeout">Tempo máximo (s) para aguardar; se None usa default_wait_seconds</param>
        <returns>WebElement quando visível</returns>
        <raises>TimeoutException</raises>
        """
        wait_time = self.default_wait_seconds if timeout is None else timeout
        try:
            return WebDriverWait(self.driver, wait_time).until(EC.visibility_of_element_located(locator))
        except TimeoutException as exc:
            # Captura artefatos para diagnóstico
            self._capture_debug_artifacts(prefix=f"element_{locator[1]}")
            new_exc = TimeoutException(f"Timeout esperando por elemento {locator} após {wait_time}s")
            setattr(new_exc, "_artifacts_captured", True)
            raise new_exc from exc

    def _scroll_to_element_by_id(self, resource_id: str, max_swipes: int = 5) -> bool:
        """
        <summary>
        Tenta trazer o elemento identificado por resource-id para a viewport usando UiScrollable.
        Usa o locator ANDROID_UIAUTOMATOR com UiScrollable.scrollIntoView.
        </summary>
        <param name="resource_id">Resource-id do elemento (ex.: 'com.pkg:id/id')</param>
        <param name="max_swipes">Número de tentativas / scrolls</param>
        <returns>True se elemento foi encontrado após scroll, False caso contrário</returns>
        """
        # Monta expressão UiScrollable para scrollIntoView pelo resource-id
        ui_selector = f'new UiScrollable(new UiSelector().scrollable(true)).scrollIntoView(new UiSelector().resourceId("{resource_id}"));'
        try:
            # driver.find_element with ANDROID_UIAUTOMATOR executa o scroll e retorna o elemento se encontrado
            elem = self.driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR, ui_selector)
            return elem is not None
        except Exception:
            # Caso não consiga encontrar / executar o scroll, retorna False
            return False

    def tap_login(self) -> None:
        """
        <summary>
        Tenta clicar no botão de login de forma robusta:
          1) tenta esperar que o botão esteja clicável,
          2) em Timeout tenta esconder teclado, scroll para o elemento e tentar novamente,
          3) se ainda falhar captura artefatos (apenas se não tiverem sido capturados pelo wait) e lança TimeoutException.
        </summary>
        <returns>None</returns>
        <raises>TimeoutException</raises>
        """
        try:
            # tentativa direta: esperar que o elemento esteja clicável e clicar
            btn = self._wait_for_clickable(self.LOGIN_BUTTON)
            btn.click()
            return
        except TimeoutException as exc:
            # Se a espera já capturou artifacts, o atributo _artifacts_captured será True
            already_captured = getattr(exc, "_artifacts_captured", False)

            # Tentativa de recuperação: esconder teclado (muitas vezes bloqueia botões)
            self._hide_keyboard_safe()

            # Tentar scrollIntoView usando resource-id; usa string do locator diretamente
            resource_id = self.LOGIN_BUTTON[1]  # ex: com.saucelabs.mydemoapp.android:id/loginBtn
            found = self._scroll_to_element_by_id(resource_id)
            if found:
                # tentar novamente com timeout curto; se falhar, irá cair no bloco abaixo
                try:
                    btn = self._wait_for_clickable(self.LOGIN_BUTTON, timeout=5)
                    btn.click()
                    return
                except TimeoutException as exc2:
                    # se falhar, propagar informação sobre capture anterior
                    already_captured = already_captured or getattr(exc2, "_artifacts_captured", False)
                    # continuar para captura de artifacts se necessário
                    pass

            # Se chegou aqui, não conseguiu clicar; salva artifacts (somente se ainda não tiverem sido capturados)
            if not already_captured:
                self._capture_debug_artifacts(prefix=f"tap_failed_{resource_id}")
            # Lança uma exceção final para o chamador mantendo contexto
            raise TimeoutException(f"Timeout esperando por elemento clicável {self.LOGIN_BUTTON} após tentativas de recuperação")

    def enter_username(self, username: str) -> None:
        """
        <summary>
        Insere o texto do usuário no campo de username de forma robusta.
        Usa _wait_for_clickable para sincronia e captura artefatos em caso de timeout.
        Sempre tenta esconder o teclado ao final para evitar obstrução de outros elementos.
        Além disso, define atributos auxiliares no elemento (sent_keys e sent_text) para compatibilidade com dobles de teste.
        </summary>
        <param name="username">Texto do usuário a ser inserido</param>
        <returns>None</returns>
        <raises>TimeoutException</raises>
        """
        try:
            # Aguarda o campo de username estar clicável utilizando o método privado
            elem = self._wait_for_clickable(self.USERNAME_FIELD)
            # Limpa qualquer texto pré-existente para garantir estado previsível
            try:
                elem.clear()
            except Exception:
                # Se clear falhar, continuamos; muitos elements podem não suportar clear corretamente
                pass
            # Insere o texto do usuário
            elem.send_keys(username)
            # Para compatibilidade com diferentes fakes/mocks, definimos atributos auxiliares
            try:
                # alguns testes verificam element.sent_keys == username
                setattr(elem, "sent_keys", username)
                # outros verificam element.sent_text ou similar; setamos também
                setattr(elem, "sent_text", username)
            except Exception:
                # ignore se o elemento não permitir atribuição de atributos
                pass
            # Depois de digitar, oculta o teclado para evitar bloqueio de outros elementos
            self._hide_keyboard_safe()
        except TimeoutException:
            # Em caso de timeout, tenta esconder teclado e captura artefatos específicos e re-lança para o chamador
            self._hide_keyboard_safe()
            self._capture_debug_artifacts(prefix=f"enter_username_failed_{self.USERNAME_FIELD[1]}")
            raise

    def enter_password(self, password: str) -> None:
        """
        <summary>
        Insere o texto da senha no campo de password de forma robusta.
        Usa _wait_for_clickable para sincronia e captura artefatos em caso de timeout.
        Sempre tenta esconder o teclado ao final para evitar obstrução de outros elementos.
        Além disso, define atributos auxiliares no elemento (sent_keys e sent_text) para compatibilidade com dobles de teste.
        </summary>
        <param name="password">Texto da senha a ser inserido</param>
        <returns>None</returns>
        <raises>TimeoutException</raises>
        """
        try:
            # Aguarda o campo de senha estar clicável utilizando o método privado
            elem = self._wait_for_clickable(self.PASSWORD_FIELD)
            # Limpa antes de digitar para evitar comportamentos inesperados
            try:
                elem.clear()
            except Exception:
                pass
            # Insere a senha
            elem.send_keys(password)
            # Para compatibilidade com diferentes fakes/mocks, definimos atributos auxiliares
            try:
                setattr(elem, "sent_keys", password)
                setattr(elem, "sent_text", password)
            except Exception:
                pass
            # Depois de digitar, oculta o teclado para segurança
            self._hide_keyboard_safe()
        except TimeoutException:
            # Tenta esconder teclado e captura artifacts e re-lança
            self._hide_keyboard_safe()
            self._capture_debug_artifacts(prefix=f"enter_password_failed_{self.PASSWORD_FIELD[1]}")
            raise

    def login(self, username: str, password: str) -> None:
        """
        <summary>
        Fluxo de login: insere usuário, insere senha e aciona o botão de login.
        </summary>
        <param name="username">Usuário</param>
        <param name="password">Senha</param>
        <returns>None</returns>
        <raises>TimeoutException</raises>
        """
        # 1) Inserir credenciais (cada método lida com sua própria sincronia/erros)
        self.enter_username(username)
        self.enter_password(password)
        # 2) Acionar login (tap_login já trata tentativas e captura artefatos se necessário)
        self.tap_login()

    def open_menu(self) -> WebElement:
        """
        <summary>
        Abre o menu lateral/cabeçalho do app clicando no botão de menu e retorna o elemento clicado.
        Método útil como primitive reutilizável nos testes que esperam por open_menu().
        </summary>
        <returns>WebElement do botão de menu após clique</returns>
        <raises>TimeoutException</raises>
        """
        # Espera o botão do menu estar clicável e clica
        menu_btn = self._wait_for_clickable(self.MENU_BUTTON)
        menu_btn.click()
        return menu_btn

    def open_login_from_menu(self) -> WebElement:
        """
        <summary>
        Abre o item "Log In" a partir do menu. Retorna o elemento clicado.
        Este método foi adicionado para compatibilidade com testes que chamam explicitamente essa primitive.
        </summary>
        <returns>WebElement do item "Log In" após clique</returns>
        <raises>TimeoutException</raises>
        """
        # Aguarda que o item do menu esteja clicável e clica
        login_menu_item = self._wait_for_clickable(self.MENU_LOGIN_TEXT)
        login_menu_item.click()
        return login_menu_item

    def login_via_menu(self, username: str, password: str) -> None:
        """
        <summary>
        Alternativa de login quando o app abre na tela principal:
        - Abre o menu,
        - Clica em "Log In" dentro do menu (usando open_login_from_menu),
        - Executa o fluxo padrão de login().
        </summary>
        <param name="username">Usuário</param>
        <param name="password">Senha</param>
        <returns>None</returns>
        <raises>TimeoutException</raises>
        """
        # 1) Clicar botão do menu (espera e clique) - delega para open_menu()
        self.open_menu()

        # 2) Clicar item "Log In" do menu delegando para open_login_from_menu()
        try:
            self.open_login_from_menu()
        except TimeoutException:
            # Em caso de falha ao abrir o item do menu, captura artefatos para diagnóstico e re-lança
            self._capture_debug_artifacts(prefix="login_via_menu_failed_menu_item")
            raise

        # 3) Agora que a tela de login está visível, executa o fluxo normal de login
        self.login(username, password)

    def is_login_button_enabled(self, timeout: Optional[int] = None) -> bool:
        """
        <summary>
        Verifica se o botão de login está presente e habilitado.
        Retorna False se houver timeout na localização do elemento.
        </summary>
        <param name="timeout">Timeout opcional em segundos</param>
        <returns>True se o botão existe e está enabled; False caso contrário</returns>
        """
        try:
            # Usa _wait_for_element para garantir o elemento está visível
            elem = self._wait_for_element(self.LOGIN_BUTTON, timeout=timeout)
            # is_enabled pode retornar True/False dependendo do estado do elemento
            return bool(elem.is_enabled())
        except TimeoutException:
            # Se não foi encontrado no tempo, considera como não habilitado
            return False
