#!/usr/bin/env python
"""Wrapper CLI to run COLMAP via src.colmap.run_colmap"""
import argparse
import os
import sys

# Ensure project root is on sys.path
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from src.colmap import run_colmap


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--input_path", required=True)
    p.add_argument("--output_path", required=True)
    p.add_argument("--aabb_scale", type=int, default=16)
    args = p.parse_args()
    run_colmap(
        args.input_path,
        args.output_path,
        aabb_scale=args.aabb_scale,
        wrapper_script=None,
    )


if __name__ == "__main__":
    main()
