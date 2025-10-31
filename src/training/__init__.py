"""Training wrappers for Gaussian Splatting.

Keep this module lightweight so the high-level orchestration can import and call training functions.
"""
from __future__ import annotations

import os
import subprocess
import sys
from typing import Optional


def run_training(scene_path: str, pipeline: str = "gaussian", iterations: int = 30000, wrapper_script: Optional[str] = None) -> None:
    """Run the training pipeline using the external gaussian-splatting train.py script.

    The script expects: -s <scene_path> --iterations <num>
    """
    # Use the external gaussian-splatting train.py script
    # In Docker, it's at /home/appuser/gaussian-splatting
    # Locally, it's at project_root/external/gaussian-splatting
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    
    # Try Docker location first
    train_script = "/home/appuser/gaussian-splatting/train.py"
    if not os.path.isfile(train_script):
        # Fall back to local location
        train_script = os.path.join(project_root, "external", "gaussian-splatting", "train.py")
    
    if not os.path.isfile(train_script):
        raise FileNotFoundError(f"Training script not found. Tried:\n"
                                f"  - /home/appuser/gaussian-splatting/train.py (Docker)\n"
                                f"  - {os.path.join(project_root, 'external', 'gaussian-splatting', 'train.py')} (local)")
    
    cmd = [sys.executable, train_script, "-s", scene_path, "--iterations", str(iterations)]
    print(f"Running Gaussian Splatting training ({iterations} iterations):", " ".join(cmd))
    subprocess.check_call(cmd)
