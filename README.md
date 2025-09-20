
-----

# DesafioQA\_MobileBddAppiumPython

## Resumo do Projeto

Este repositório contém uma suíte de testes automatizados para o aplicativo móvel **"Sauce Labs Demo App"** (disponível em `resources/mda-2.2.0-25.apk`).

O projeto utiliza uma abordagem de automação abrangente, combinando:

  * **Page Objects** (usando Appium e Selenium)
  * **Testes Unitários** (com Pytest)
  * **Testes BDD** (com Behave)

O foco principal é a **robustez**, a **captura de artefatos** para diagnóstico de falhas e a **compatibilidade** entre a execução local e em ambientes de Integração Contínua (CI).

-----

## Status do Projeto

  * **Testes Unitários:** 
  * **Testes BDD:** 
  * **Artefatos Gerados:** Salvos na pasta `./artifacts/` (inclui screenshots e `page_source` em caso de falhas).

-----

## Pré-requisitos

Certifique-se de que os seguintes componentes estão instalados e configurados em seu sistema operacional:

  * **Python:** Versão `3.10` ou superior (testado com `3.12`).
  * **Node.js & Appium Server:** Necessário para o servidor Appium.
  * **Android SDK:** Com o **ADB** configurado no `PATH`.
  * **Emulador** ou **dispositivo Android real** para a execução dos testes.
  * **Gerenciador de pacotes Python:** Recomenda-se o uso de `pipenv`.

-----

## Instalação (Passo a Passo)

### 1\. Instalar dependências de sistema

1.  **Instale Python:** Verifique a instalação com `python --version`.
2.  **Instale Node.js:** Siga as instruções do [site oficial](https://nodejs.org/).
3.  **Instale Appium globalmente:**
    ```bash
    npm install -g appium
    ```
    Confirme a instalação: `appium --version`.
4.  **Configure o Android SDK:**
      * Instale o Android SDK.
      * Defina as variáveis de ambiente `ANDROID_HOME` e inclua o diretório `platform-tools` no seu `PATH`.
      * Confirme a configuração com `adb devices`.

### 2\. Instalar dependências Python

Escolha um dos métodos abaixo:

#### Método recomendado (Pipenv)

```bash
# 1. Instale pipenv globalmente
pip install pipenv

# 2. Instale as dependências e ative o ambiente virtual
pipenv install --dev
pipenv shell
```

#### Método alternativo (Pip e Requirements)

Crie um arquivo `requirements.txt` com as dependências do seu projeto e, em seguida, instale-as:

```bash
pip install -r requirements.txt
```

-----

## Executando os Testes

Antes de rodar qualquer teste, prepare o ambiente:

1.  **Inicie o Appium Server:**
    ```bash
    appium
    ```
2.  **Inicie o emulador ou conecte seu dispositivo:**
    ```bash
    adb devices
    ```

### Testes Unitários (Pytest)

A partir da raiz do projeto:

```bash
pytest -q
```

  * Para rodar um arquivo específico: `pytest -q tests/test_login_page_methods.py`.

### Testes BDD (Behave)

A partir da raiz do projeto:

```bash
behave -f pretty
```

  * **Observação:** O *step* `Given que o app está aberto na tela de login` inicializa o driver e instala o APK. O dispositivo/emulador deve estar pronto e visível para o ADB.

-----

## Estrutura do Projeto

```
.
├── artifacts/                  # Screenshots e page_source de falhas
├── features/
│   ├── login.feature           # Cenários BDD
│   └── steps/
│       └── login_steps.py      # Implementação dos steps
├── pages/
│   └── login_page.py           # Page Objects
├── resources/
│   └── mda-2.2.0-25.apk        # APK da aplicação
├── tests/
│   ├── conftest.py             # Fixtures e configurações do pytest
│   ├── test_*.py               # Testes unitários (pytest)
│   └── __init__.py
├── .github/
│   └── workflows/
│       └── python-tests.yml    # Workflow de CI com GitHub Actions
├── Pipfile / requirements.txt  # Gerenciamento de dependências
├── README.md                   # Este arquivo
└── ...
```

-----

## Boas Práticas e Recomendações

  * **Page Objects:** Prefira métodos atômicos (`enter_username`, `tap_login`) e use *docstrings* e comentários para documentar cada funcionalidade.
  * **Testes Unitários:** Use `monkeypatch` para simular dependências (como `WebDriverWait` ou o `driver`) e isolar o código sob teste.
  * **Observabilidade:** O workflow de CI já faz *upload* da pasta `artifacts/` em caso de falha.
  * **Variáveis de Ambiente:** Utilize-as para configurar o ambiente de execução (`APPIUM_SERVER`, `DEVICE_NAME`, etc.), facilitando a portabilidade.

-----

## Troubleshooting

  * **`ModuleNotFoundError`:** Certifique-se de que está executando os testes a partir da raiz do projeto e que a estrutura de pacotes está correta (`__init__.py` nas pastas de código).
  * **`Timeout` ao esperar por um elemento:**
      * Verifique os `page_source` gerados nos artefatos.
      * Confirme se os locators ainda são válidos para a build do APK que você está usando.
      * Aumente o `timeout` usando as variáveis de ambiente.

-----

## Contribuindo

1.  Faça um `fork` do projeto.
2.  Crie uma nova *branch* para sua funcionalidade (`feature/sua-funcionalidade`).
3.  Faça suas alterações e crie um **Pull Request (PR)** para a *branch* principal.
4.  Certifique-se de incluir novos testes unitários e de manter a documentação (comentários e *docstrings*) atualizada.

-----

## Licença

Este projeto é distribuído sob a licença [MIT](https://www.google.com/search?q=LICENSE).

-----