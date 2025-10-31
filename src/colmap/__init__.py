"""Lightweight COLMAP integration helpers.

These wrappers prefer calling local scripts (e.g., `scripts/run-colmap.py`) if present.
They keep the pipeline callable from Python so notebook code can be migrated into `src/`.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
from typing import Optional


def run_colmap(input_path: str, output_path: str, aabb_scale: int = 16, wrapper_script: Optional[str] = None, use_gpu: bool = True) -> None:
    """Run COLMAP reconstruction following the gaussian-splatting workflow.

    Uses the external/gaussian-splatting/convert.py script for proper COLMAP processing.
    This function raises CalledProcessError if the invoked process fails.
    
    Args:
        input_path: Path to folder containing input images
        output_path: Scene root path (will contain input/, sparse/, etc.)
        aabb_scale: Axis-aligned bounding box scale (not used by convert.py)
        wrapper_script: Deprecated, kept for compatibility
        use_gpu: Whether to use GPU for COLMAP operations (default: True)
    """
    # Use the external gaussian-splatting convert.py script
    # In Docker, it's at /home/appuser/gaussian-splatting
    # Locally, it's at project_root/external/gaussian-splatting
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    
    # Try Docker location first
    convert_script = "/home/appuser/gaussian-splatting/convert.py"
    if not os.path.isfile(convert_script):
        # Fall back to local location
        convert_script = os.path.join(project_root, "external", "gaussian-splatting", "convert.py")
    
    if not os.path.isfile(convert_script):
        raise FileNotFoundError(f"COLMAP convert script not found. Tried:\n"
                                f"  - /home/appuser/gaussian-splatting/convert.py (Docker)\n"
                                f"  - {os.path.join(project_root, 'external', 'gaussian-splatting', 'convert.py')} (local)")
    
    # The convert.py script expects images in source_path/input/
    # We need to prepare the directory structure
    input_dir = os.path.join(output_path, "input")
    
    # If input_path has images but input_dir doesn't, copy or symlink
    if os.path.exists(input_path) and input_path != input_dir:
        if not os.path.exists(input_dir):
            print(f"Creating symlink: {input_dir} -> {input_path}")
            try:
                # Try symbolic link first (requires admin on Windows or dev mode)
                os.symlink(input_path, input_dir, target_is_directory=True)
            except (OSError, NotImplementedError):
                # Fall back to copying files
                print(f"Symlink failed, copying images instead...")
                shutil.copytree(input_path, input_dir)
        else:
            # input/ already exists, assume it's set up correctly
            pass
    
    # Run the COLMAP convert script with GPU optimization
    cmd = [sys.executable, convert_script, "--source_path", output_path]
    if not use_gpu:
        cmd.append("--no_gpu")
    
    gpu_status = "enabled" if use_gpu else "disabled"
    print(f"Running COLMAP reconstruction (GPU {gpu_status}):", " ".join(cmd))

    # Ensure logs directory exists under the scene output path
    logs_dir = os.path.join(output_path, "logs")
    os.makedirs(logs_dir, exist_ok=True)
    colmap_log = os.path.join(logs_dir, "colmap.log")

    # Helper to run and capture output to a log file. Returns (rc, output_text)
    def _run_and_log(command, logfile_path):
        with open(logfile_path, "ab") as lf:
            lf.write(("\n--- Running: " + " ".join(command) + "\n").encode())
            proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=os.environ)
            out_chunks = []
            for chunk in proc.stdout:
                lf.write(chunk)
                out_chunks.append(chunk)
            proc.wait()
            return proc.returncode, b"".join(out_chunks).decode(errors='replace')

    # First attempt: as requested (GPU if enabled)
    rc, out = _run_and_log(cmd, colmap_log)

    # Detect OpenGL context failure patterns and retry with CPU-only mode once
    opengl_errors = ["could not create OpenGL context", "Check failed: context_.create()", "could not connect to display", "QXcbConnection"]
    need_retry = False
    lowered = out.lower()
    for pat in opengl_errors:
        if pat.lower() in lowered:
            need_retry = True
            break

    if rc != 0 and need_retry and use_gpu:
        print("Detected OpenGL / GPU context issue in COLMAP. Retrying feature extraction with CPU-only mode (--no_gpu). See logs at:", colmap_log)
        # append --no_gpu and run again
        cmd_cpu = [sys.executable, convert_script, "--source_path", output_path, "--no_gpu"]
        rc2, out2 = _run_and_log(cmd_cpu, colmap_log)
        if rc2 != 0:
            print("COLMAP CPU retry also failed. Check log:", colmap_log)
            raise subprocess.CalledProcessError(rc2, cmd_cpu)
        else:
            print("COLMAP completed with CPU-only mode. Proceeding.")
            return

    if rc != 0:
        print("COLMAP failed. See log:", colmap_log)
        raise subprocess.CalledProcessError(rc, cmd)
    else:
        print("COLMAP completed successfully. Log:", colmap_log)
