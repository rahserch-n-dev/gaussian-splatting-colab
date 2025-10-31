"""Environment detection utilities for local runs.

Keep this lightweight so tests can import it without heavy dependencies.
"""
from __future__ import annotations

import importlib
import platform
import sys
from typing import Dict, Any


def get_python_info() -> Dict[str, Any]:
    return {"executable": sys.executable, "version": sys.version}


def get_system_info() -> Dict[str, Any]:
    return {"platform": platform.platform(), "processor": platform.processor()}


def get_torch_info() -> Dict[str, Any]:
    info: Dict[str, Any] = {}
    try:
        torch = importlib.import_module("torch")
        info["installed"] = True
        info["version"] = getattr(torch, "__version__", None)
        try:
            info["cuda_available"] = torch.cuda.is_available()
            info["cuda_device_count"] = torch.cuda.device_count()
        except Exception as e:
            info["cuda_error"] = str(e)
    except Exception:
        info["installed"] = False
    return info


def full_env_report() -> Dict[str, Any]:
    return {"python": get_python_info(), "system": get_system_info(), "torch": get_torch_info()}
