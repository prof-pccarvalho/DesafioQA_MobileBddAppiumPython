#!/usr/bin/env python3
"""
<summary>
Testes unitários para o mecanismo de debug/captura de artifacts em pages.product_page.ProductPage.
Cobre:
 - gravação de screenshot e page_source em ./artifacts
 - comportamento tolerante a falhas do driver
 - emissões de logs debug (caplog)
</summary>
"""
import os
import time
from unittest.mock import MagicMock
import logging
import pytest
from pages.product_page import ProductPage

def test_capture_debug_artifacts_writes_files_and_logs(tmp_path, caplog, monkeypatch):
    """
    <summary>
    Valida que _capture_debug_artifacts grava um PNG e um XML no diretório artifacts e emite logs debug.
    </summary>
    """
    # Garante que logs debug do módulo sejam capturados
    caplog.set_level(logging.DEBUG)

    # Criamos um fake driver com page_source e get_screenshot_as_file
    driver = MagicMock()
    driver.page_source = "<hierarchy><node text='X'/></hierarchy>"

    # Implementa get_screenshot_as_file para escrever um ficheiro simples
    def fake_screenshot(path):
        with open(path, "wb") as f:
            f.write(b"PNG-DATA")
        return True
    driver.get_screenshot_as_file.side_effect = fake_screenshot

    pp = ProductPage(driver)

    # Isola o cwd para tmp_path para não poluir repo
    monkeypatch.chdir(tmp_path)

    # Chama a captura com prefixo conhecido
    prefix = "unit_test_capture"
    pp._capture_debug_artifacts(prefix=prefix)

    # Confirma existência de ficheiros no diretório artifacts
    artifacts_dir = tmp_path / "artifacts"
    assert artifacts_dir.exists() and artifacts_dir.is_dir()

    files = list(artifacts_dir.iterdir())
    # Deve ter pelo menos 2 ficheiros (png + xml)
    assert any(f.suffix == ".png" and prefix in f.name for f in files)
    assert any(f.suffix == ".xml" and prefix in f.name for f in files)

    # Verifica que logs debug com as mensagens esperadas estão presentes
    # (procuramos por fragmentos que o método registra)
    msgs = "\n".join(rec.message for rec in caplog.records)
    assert "Screenshot salvo em" in msgs or "get_screenshot_as_file" in msgs
    assert "Page source salvo em" in msgs or "page_source vazio" in msgs

def test_capture_debug_artifacts_handles_screenshot_failure(tmp_path, caplog, monkeypatch):
    """
    <summary>
    Garante que se driver.get_screenshot_as_file lançar exceção, o método não propaga e grava page_source quando possível.
    </summary>
    """
    caplog.set_level(logging.DEBUG)
    driver = MagicMock()
    driver.page_source = "<hierarchy>OK</hierarchy>"

    # screenshot lança exceção
    def fake_screenshot_fail(path):
        raise RuntimeError("simulated screenshot failure")
    driver.get_screenshot_as_file.side_effect = fake_screenshot_fail

    pp = ProductPage(driver)
    monkeypatch.chdir(tmp_path)

    # Deve não levantar
    pp._capture_debug_artifacts(prefix="failure_case")

    artifacts_dir = tmp_path / "artifacts"
    # Mesmo que screenshot falhe, page_source deve ter sido tentado salvo (ou no mínimo não propagou)
    assert artifacts_dir.exists()
    files = list(artifacts_dir.iterdir())
    # Pode ter só xml se o png falhou; garantimos que pelo menos um .xml existe
    assert any(f.suffix == ".xml" for f in files)
    # Verifica logs de exceção para screenshot
    msgs = "\n".join(rec.message for rec in caplog.records)
    assert "Falha ao salvar screenshot" in msgs or "get_screenshot_as_file" in msgs