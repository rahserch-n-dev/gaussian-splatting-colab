"""COLMAP -> Gaussian Splatting conversion wrapper.

This module wraps any conversion step required after COLMAP reconstruction and before training.
By default it calls an external conversion script if provided; keep minimal so logic can be replaced by real conversion later.
"""
from __future__ import annotations

import os
import subprocess
import sys
from typing import Optional


def run_convert(scene_path: str, wrapper_script: Optional[str] = None) -> None:
    """Run conversion from COLMAP outputs to Gaussian Splatting inputs.

    wrapper_script: path to local script (scripts/convert-colmap.py). If absent, raise FileNotFoundError to indicate manual action required.
    """
    if wrapper_script and os.path.isfile(wrapper_script):
        cmd = [sys.executable, wrapper_script, "--input_path", scene_path]
        print("Running conversion wrapper:", " ".join(cmd))
        subprocess.check_call(cmd)
    else:
        raise FileNotFoundError("No convert wrapper script found at {}".format(wrapper_script))
