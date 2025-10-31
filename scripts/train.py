#!/usr/bin/env python
"""Wrapper CLI to run training via src.training.run_training
"""
import argparse
import os, sys
# Ensure project root is on sys.path
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from src.training import run_training


def main():
    p = argparse.ArgumentParser()
    p.add_argument("-s", "--scene", required=True)
    p.add_argument("--pipeline", default="gaussian")
    p.add_argument("--iterations", type=int, default=30000)
    args = p.parse_args()
    run_training(args.scene, pipeline=args.pipeline, iterations=args.iterations, wrapper_script=None)


if __name__ == "__main__":
    main()
