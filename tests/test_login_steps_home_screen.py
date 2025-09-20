#!/usr/bin/env python3
"""
<summary>
Unit tests para o helper wait_for_any_locator e para step_verify_home_screen.
Não usam Appium real: monkeypatcham WebDriverWait no módulo de steps para simular comportamento.
</summary>
"""
import os
import types
import pytest
from selenium.common.exceptions import TimeoutException

# Importamos o módulo de steps para monkeypatchar WebDriverWait nele
import features.steps.login_steps as ls_mod


class DummyWait:
    """
    <summary>
    Dummy WebDriverWait substituto. Cada instância registra seu índice de criação e,
    dependendo da configuração, o método until() retornará com sucesso apenas na
    chamada configurada (success_call_index) ou sempre levantará TimeoutException.
    </summary>
    """
    calls = []            # lista para contar instâncias criadas
    success_call_index = None  # índice (1-based) da instância que deverá ter sucesso

    def __init__(self, driver, timeout):
        # registra a criação da instância e armazena seu índice (1-based)
        DummyWait.calls.append(1)
        self._index = len(DummyWait.calls)

    def until(self, condition):
        # Se success_call_index coincide com este índice, simula sucesso
        if DummyWait.success_call_index is not None and DummyWait.success_call_index == self._index:
            return True  # simula elemento encontrado
        # caso contrário, simula timeout
        raise TimeoutException("simulated timeout")


@pytest.fixture(autouse=True)
def reset_dummy():
    # reseta estado do DummyWait antes de cada teste
    DummyWait.calls.clear()
    DummyWait.success_call_index = None
    yield
    DummyWait.calls.clear()
    DummyWait.success_call_index = None


def test_verify_home_screen_succeeds_with_first_locator(monkeypatch):
    """
    <summary>
    Garante que quando a primeira tentativa for bem-sucedida o passo não lança.
    </summary>
    """
    # Forçamos que a primeira instância de WebDriverWait (primeiro locator) tenha sucesso
    DummyWait.success_call_index = 1
    # Monkeypatcha WebDriverWait no módulo de steps para usar DummyWait
    monkeypatch.setattr(ls_mod, "WebDriverWait", DummyWait)

    # Cria um contexto simples com driver (não usado pela DummyWait)
    ctx = types.SimpleNamespace()
    ctx.driver = object()
    # Executa; não deve lançar
    ls_mod.step_verify_home_screen(ctx)


def test_verify_home_screen_succeeds_with_second_locator(monkeypatch):
    """
    <summary>
    Garante que quando a primeira falha e a segunda tiver sucesso o passo não lança.
    </summary>
    """
    # força sucesso na segunda instância (segunda tentativa -> segundo locator)
    DummyWait.success_call_index = 2
    monkeypatch.setattr(ls_mod, "WebDriverWait", DummyWait)

    ctx = types.SimpleNamespace()
    ctx.driver = object()
    # Executa; não deve lançar
    ls_mod.step_verify_home_screen(ctx)


def test_verify_home_screen_failure_captures_artifacts(monkeypatch, tmp_path):
    """
    <summary>
    Garante que quando nenhum locator for encontrado o passo captura artifacts
    (via context.login_page._capture_debug_artifacts se disponível) e levanta TimeoutException.
    </summary>
    """
    # Simula que nenhuma tentativa terá sucesso (success_call_index = None)
    DummyWait.success_call_index = None
    monkeypatch.setattr(ls_mod, "WebDriverWait", DummyWait)

    # Context com driver e um login_page fake para capturar artifacts
    captured = {"flag": False}

    class FakeLoginPage:
        def _capture_debug_artifacts(self, prefix=None):
            captured["flag"] = True

    ctx = types.SimpleNamespace()
    ctx.driver = object()
    ctx.login_page = FakeLoginPage()

    # Ao executar esperamos TimeoutException
    with pytest.raises(TimeoutException):
        ls_mod.step_verify_home_screen(ctx)

    # E verificamos que o capture foi executado
    assert captured["flag"] is True
