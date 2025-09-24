A sua solicitação é bastante detalhada e, para garantir que o novo `README.md` atenda a todas as suas necessidades, compilei uma versão completa que incorpora todas as melhorias que você pediu, incluindo a nova estrutura, as boas práticas, os exemplos de código e a seção de *troubleshooting* com o Appium Inspector.

Aqui está o `README.md` finalizado.

-----

# DesafioQA\_MobileBddAppiumPython

## 📋 Resumo do Projeto

Este repositório apresenta uma suíte de testes automatizados para o aplicativo **"Sauce Labs Demo App"** (`resources/mda-2.2.0-25.apk`). O projeto foi desenhado para ser robusto e eficiente, utilizando uma combinação de **Page Objects**, **Testes Unitários (Pytest)** e **Testes BDD (Behave)**.

Ele prioriza a **captura de artefatos** para facilitar o diagnóstico de falhas e a **portabilidade**, permitindo a execução tanto em ambiente local quanto em **Integração Contínua (CI)**.

## 🚀 Status do Projeto

  * **Testes Unitários:** \* **Testes BDD:** \* **Artefatos Gerados:** Salvos na pasta `./artifacts/` (inclui screenshots e `page_source` em caso de falhas).

-----

## 🛠️ Pré-requisitos

Certifique-se de que os seguintes componentes estão instalados e configurados:

  * **Python:** Versão `3.10` ou superior (testado com `3.12`).
  * **Node.js & Appium Server:** O servidor Appium é essencial para a automação.
  * **Android SDK:** Com o **ADB** configurado no `PATH`.
  * **Emulador** ou **dispositivo Android real**.
  * **Gerenciador de pacotes Python:** Recomenda-se o uso de `pipenv`.

-----

## ⚙️ Instalação (Passo a Passo)

### 1\. Instalar dependências de sistema

1.  **Instale Python e Node.js:** Verifique as versões com `python --version` e `node --version`.
2.  **Instale o Appium:**
    ```bash
    npm install -g appium
    ```
    Confirme a instalação com `appium --version`.
3.  **Configure o Android SDK:**
      * Instale o Android SDK e configure as variáveis de ambiente `ANDROID_HOME` e `platform-tools` no seu `PATH`. Isso garante que o `adb` e outras ferramentas estejam acessíveis via terminal.
      * Confirme a configuração rodando `adb devices`.

#### Exemplo de Configuração de Variáveis (Windows)

**PowerShell**

```powershell
$env:ANDROID_SDK_ROOT = "C:\Users\pcbar\AppData\Local\Android\Sdk"
$env:Path += ";$env:ANDROID_SDK_ROOT\platform-tools"
```

### 2\. Instalar dependências Python

**Método recomendado (Pipenv)**

```bash
# Instale pipenv globalmente
pip install pipenv

# Instale as dependências do projeto
pipenv install --dev

# Ative o ambiente virtual
pipenv shell
```

**Método alternativo (Pip e Requirements)**

```bash
pip install -r requirements.txt
```

-----

## ▶️ Executando os Testes

Antes de rodar qualquer teste, prepare o ambiente:

1.  **Inicie o Appium Server:**
    ```bash
    appium
    ```
    *Dica: O Appium usa a porta padrão `4723`. Verifique os logs do terminal se encontrar problemas de conexão.*
2.  **Inicie o emulador ou conecte seu dispositivo:**
    ```bash
    adb devices
    ```
    *Se a lista estiver vazia, verifique se o emulador está rodando e se a depuração USB está ativada no seu dispositivo real.*

### Testes Unitários (Pytest)

A partir da raiz do projeto:

```bash
pytest -q
pytest -s
```

  * Para rodar um arquivo específico: `pytest -q tests/test_login_page_methods.py`.

### Testes BDD (Behave)

A partir da raiz do projeto:

```bash
behave -f pretty
behave -f pretty features/login.feature
behave -f pretty features/compare_products.feature
```

-----

## 📂 Estrutura do Projeto

```
.
├── artifacts/                  # Screenshots e page_source de falhas
├── APK-Info/                   # Ferramentas para info do APK
├── features/                   # Cenários BDD com Behave
│   ├── compare_products.feature
│   ├── login.feature
│   └── steps/
│       ├── login_steps.py      # Implementação dos steps de login
│       └── product_steps.py    # Implementação dos steps de produtos
├── pages/
│   ├── login_page.py           # Page Objects da tela de login
│   └── product_page.py         # Page Objects da tela de produtos
├── resources/
│   └── mda-2.2.0-25.apk        # APK da aplicação
├── scripts/
│   └── setup_env.ps1           # Script para configurar o ambiente (ex: PowerShell)
├── tests/
│   ├── conftest.py             # Fixtures e configurações do Pytest
│   ├── test_*.py               # Testes unitários com Pytest
│   └── utils/                  # Utilitários para os testes
├── .github/
│   └── workflows/
│       └── python-tests.yml    # Workflow de CI com GitHub Actions
├── Pipfile                     # Gerenciamento de dependências com Pipenv
├── Pipfile.lock                # Arquivo de lock do Pipfile
└── README.md                   # Este arquivo
```

-----

## 💡 Boas Práticas e Recomendações

  * **Page Objects:** Crie métodos atômicos e bem nomeados (ex.: `enter_username`, `tap_login`). Use `docstrings` para documentar a funcionalidade de cada um.
  * **Isolamento de Testes Unitários:** Para testar a lógica dos Page Objects, utilize `monkeypatch` para simular dependências como `WebDriverWait` ou o próprio driver, garantindo que o teste seja rápido e isolado.
  * **Variáveis de Ambiente:** Configure variáveis como `APPIUM_SERVER` e `DEVICE_NAME` para facilitar a portabilidade entre a máquina local e o ambiente de CI.
  * **Observabilidade:** O framework já salva screenshots e o `page_source` em caso de falhas, facilitando o *debug*. Para o CI, o workflow do GitHub Actions já está configurado para anexar a pasta `artifacts/` em caso de falha.
  * **Credenciais no CI:** Recomenda-se configurar credenciais e variáveis sensíveis usando **GitHub Secrets**, evitando expor informações diretamente no código.

-----

## 🔍 Dicas e Troubleshooting

  * **Appium não inicia:** Verifique se não há outro serviço rodando na porta `4723`.
  * **`adb devices` retorna vazio:** Confirme se o emulador ou dispositivo está rodando e com a depuração USB ativa.
  * **`Timeout` ao esperar por um elemento:**
      * Verifique o `page_source` gerado nos artefatos para confirmar a validade dos locators.
      * Considere aumentar o `timeout` via variáveis de ambiente.
  * **Erro de permissão para instalar APK:** Certifique-se de que a depuração USB está ativa e o dispositivo desbloqueado.
  * **Caminhos do APK com espaços:** Evite espaços no caminho do arquivo ou escape-os nas *Desired Capabilities*.
  * **Como debugar localmente:**
      * Use o **Appium Inspector** para inspecionar a hierarquia de elementos e gerar locators.

### Exemplo de Appium Inspector Desired Capabilities

Este é um exemplo de configuração que pode ser usada no Appium Inspector. Ajuste os caminhos e o `deviceName` conforme sua configuração.

```json
{
  "platformName": "Android",
  "automationName": "UiAutomator2",
  "deviceName": "emulator-5554",
  "app": "C:\\Users\\pcbar\\IdeaProjects\\DesafioQA_MobileBddAppiumPython\\resources\\mda-2.2.0-25.apk",
  "appWaitActivity": "*",
  "autoGrantPermissions": true,
  "noReset": false
}
```

**Observações:**

  * No Windows, use barras invertidas duplas `\\` ou barras normais `/` no JSON.
  * `appWaitActivity: "*"` é útil quando você não tem o nome exato da *activity* de lançamento.
  * `noReset: false` força a reinstalação e um estado "limpo" do aplicativo, o que é ideal para cenários de teste que precisam começar do zero.

-----

## 🤝 Contribuindo

1.  Faça um `fork` do projeto.
2.  Crie uma nova *branch* para sua funcionalidade (`feature/sua-funcionalidade`).
3.  Faça suas alterações, adicione testes para cobrir o novo código e atualize a documentação (comentários e `docstrings`).
4.  Abra um **Pull Request (PR)** para a *branch* principal, descrevendo claramente as mudanças e o motivo delas.

-----

## 📄 Licença

Este projeto é distribuído sob a **Licença MIT**.