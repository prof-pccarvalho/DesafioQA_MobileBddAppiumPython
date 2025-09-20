#!/usr/bin/env python3
"""
<summary>
Utilitários para checar configuração do ambiente Android (variáveis e adb).
</summary>
"""
from typing import Tuple, Dict
import os
import shutil
import subprocess

def check_android_environment() -> Tuple[bool, Dict[str, str]]:
    """
    <summary>
    Verifica ANDROID_SDK_ROOT/ANDROID_HOME e presença do adb no PATH.
    </summary>
    <returns> (ok:bool, info:dict)</returns>
    """
    info = {
        "android_sdk_root": os.environ.get("ANDROID_SDK_ROOT", ""),
        "android_home": os.environ.get("ANDROID_HOME", ""),
        "adb_path": "",
        "adb_version": "",
        "notes": "",
    }

    sdk_root = info["android_sdk_root"] or info["android_home"]
    if not sdk_root:
        info["notes"] += "Nenhuma variável ANDROID_SDK_ROOT/ANDROID_HOME definida. "
    else:
        if not os.path.isdir(sdk_root):
            info["notes"] += f"ANDROID SDK path '{sdk_root}' não existe. "
        else:
            info["notes"] += f"ANDROID SDK encontrado em {sdk_root}. "

    adb_exec = shutil.which("adb")
    if adb_exec:
        info["adb_path"] = adb_exec
        try:
            completed = subprocess.run([adb_exec, "version"], capture_output=True, text=True, timeout=5)
            info["adb_version"] = completed.stdout.strip().splitlines()[0] if completed.stdout else ""
            info["notes"] += "adb encontrado. "
        except Exception as ex:
            info["notes"] += f"Erro ao executar 'adb version': {ex}. "
    else:
        info["notes"] += "adb não encontrado no PATH. "

    ok = bool(sdk_root and os.path.isdir(sdk_root) and adb_exec)
    return ok, info
