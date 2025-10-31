#!/usr/bin/env python
"""Wrapper CLI to run conversion step via src.convert.run_convert
"""
import argparse
import os, sys
# Ensure project root is on sys.path
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from src.convert import run_convert


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--input_path", required=True)
    args = p.parse_args()
    run_convert(args.input_path, wrapper_script=None)


if __name__ == "__main__":
    main()
