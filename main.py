#!/usr/bin/env python
"""Main entry point for Gaussian Splatting pipeline.

This provides a unified CLI interface for running the Gaussian Splatting workflow
locally without notebooks.

Usage:
    python main.py --check                    # Environment check
    python main.py --scene myscene --run      # Run full pipeline
    python main.py --scene myscene --colmap   # Run COLMAP only
    python main.py --scene myscene --train    # Run training only
"""
import argparse
import sys
from pathlib import Path

# Ensure project root is on sys.path
PROJECT_ROOT = Path(__file__).parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.colmap import run_colmap
from src.core import env
from src.orchestrator import run_full_pipeline
from src.training import run_training


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Gaussian Splatting Pipeline - Local Execution",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    parser.add_argument(
        "--check", action="store_true", help="Run environment checks and exit"
    )
    parser.add_argument(
        "--scene", type=str, default="myscene", help="Scene name (folder under scenes/)"
    )
    parser.add_argument(
        "--run", action="store_true", help="Run the full pipeline (COLMAP + training)"
    )
    parser.add_argument(
        "--colmap", action="store_true", help="Run COLMAP reconstruction only"
    )
    parser.add_argument(
        "--train",
        action="store_true",
        help="Run training only (requires existing COLMAP output)",
    )
    parser.add_argument(
        "--iterations",
        type=int,
        default=30000,
        help="Training iterations (default: 30000)",
    )
    parser.add_argument(
        "--aabb_scale", type=int, default=16, help="AABB scale for COLMAP (default: 16)"
    )

    args = parser.parse_args()

    # Environment check
    if args.check:
        print("=== Environment Check ===")
        report = env.full_env_report()

        print(f"\nPython: {report['python']['version'].split()[0]}")
        print(f"Executable: {report['python']['executable']}")

        print(f"\nSystem: {report['system']['platform']}")

        if report["torch"]["installed"]:
            print(f"\nPyTorch: {report['torch']['version']}")
            if report["torch"].get("cuda_available"):
                print(
                    f"CUDA: Available ({report['torch']['cuda_device_count']} devices)"
                )
            else:
                print("CUDA: Not available (CPU only)")
        else:
            print("\nPyTorch: Not installed")
            print("Install with: pip install -r requirements.txt")

        print("\n Environment check complete")
        return 0

    # Scene path validation
    scene_path = PROJECT_ROOT / "scenes" / args.scene
    images_path = scene_path / "images"

    if not scene_path.exists():
        print(f"ERROR: Scene directory not found: {scene_path}")
        print(f"Create it with: mkdir -p {scene_path}/images")
        return 1

    if not images_path.exists() and (args.run or args.colmap):
        print(f"ERROR: Images directory not found: {images_path}")
        print(f"Create it and add images: mkdir -p {images_path}")
        return 1

    # Execute requested operation
    try:
        if args.run:
            print(f"\n=== Running Full Pipeline: {args.scene} ===")
            run_full_pipeline(
                args.scene, aabb_scale=args.aabb_scale, iterations=args.iterations
            )
            print("\n Pipeline complete!")

        elif args.colmap:
            print(f"\n=== Running COLMAP: {args.scene} ===")
            run_colmap(str(images_path), str(scene_path), aabb_scale=args.aabb_scale)
            print("\n COLMAP complete!")

        elif args.train:
            print(f"\n=== Running Training: {args.scene} ===")
            # Check if COLMAP output exists
            sparse_path = scene_path / "sparse"
            if not sparse_path.exists():
                print(f"ERROR: COLMAP output not found at {sparse_path}")
                print(
                    "Run COLMAP first with: python main.py --scene {} --colmap".format(
                        args.scene
                    )
                )
                return 1

            run_training(str(scene_path), iterations=args.iterations)
            print("\n Training complete!")
        else:
            parser.print_help()
            return 0

    except FileNotFoundError as e:
        print(f"\nERROR: {e}")
        return 1
    except Exception as e:
        print(f"\nERROR: {type(e).__name__}: {e}")
        import traceback

        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
