"""Local orchestration for Gaussian Splatting (replace Colab notebook steps).

Use from PowerShell or any terminal after activating the project's venv.

Examples:
    python .\scripts\run_local.py --check
    python .\scripts\run_local.py --scene myscene --run
"""
import argparse
import importlib
import os
import subprocess
import sys

# Ensure project root is on sys.path so `src` imports work when running scripts directly.
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
        sys.path.insert(0, REPO_ROOT)

from src.core import env
from src import colmap as colmap_mod
from src import training as training_mod


def check_python():
    info = env.get_python_info()
    print(f"Python: {info['executable']} ({info['version'].splitlines()[0]})")


def check_torch():
    info = env.get_torch_info()
    if not info.get("installed"):
        print("torch not installed")
        return
    print("torch version:", info.get("version"))
    if info.get("cuda_error"):
        print("cuda check error:", info.get("cuda_error"))
    else:
        print("cuda available:", info.get("cuda_available"))
        print("cuda device count:", info.get("cuda_device_count"))


def verify_scene(scene_name: str):
    base = os.path.abspath(os.path.join("scenes", scene_name))
    images = os.path.join(base, "images")
    ok = True
    if not os.path.isdir(base):
        print(f"Scene folder missing: {base}")
        ok = False
    if not os.path.isdir(images):
        print(f"Images folder missing: {images}")
        ok = False
    if ok:
        print(f"Found scene: {base}")
    return ok


def run_colmap_if_present(scene_name: str):
    local_script = os.path.join("scripts", "run-colmap.py")
    try:
        colmap_mod.run_colmap(os.path.join("scenes", scene_name, "images"), os.path.join("scenes", scene_name), wrapper_script=local_script)
    except FileNotFoundError:
        print("No wrapper script found and system COLMAP not available. Install COLMAP or provide scripts/run-colmap.py")
    except subprocess.CalledProcessError as e:
        # Provide guidance and point to colmap log if available
        logs_path = os.path.join("scenes", scene_name, "logs", "colmap.log")
        if os.path.exists(logs_path):
            print(f"COLMAP failed. See logs: {logs_path}")
        raise


def run_train_if_present(scene_name: str):
    local_script = os.path.join("scripts", "train.py")
    try:
        training_mod.run_training(os.path.join("scenes", scene_name), wrapper_script=local_script)
    except FileNotFoundError:
        print("No training wrapper script found at scripts/train.py — please add one or call training manually.")
    except subprocess.CalledProcessError as e:
        raise


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--check", action="store_true", help="Run environment checks only")
    p.add_argument("--scene", type=str, default="myscene", help="Scene name under scenes/<name>/images")
    p.add_argument("--run", action="store_true", help="Run the standard pipeline (colmap conversion + train) if scripts are present")
    args = p.parse_args()

    check_python()
    check_torch()

    if args.check:
        print("Checks complete")
        return

    scene_ok = verify_scene(args.scene)
    if not scene_ok:
        print("Scene verification failed — fix folder layout before running pipeline")
        sys.exit(1)

    if args.run:
        # Use the orchestrator for the full pipeline. This delegates to src.* modules and the thin scripts.
        try:
            from src.orchestrator import run_full_pipeline

            run_full_pipeline(args.scene)
        except FileNotFoundError as e:
            print("Pipeline precondition failed:", e)
            sys.exit(5)
        except subprocess.CalledProcessError as e:
            print("Subprocess failed during pipeline:", e)
            sys.exit(6)


if __name__ == "__main__":
    main()
