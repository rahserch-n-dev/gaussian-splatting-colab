"""Integration tests for scripts directory."""

import subprocess
import sys


def test_run_local_check():
    """Test that scripts/run_local.py --check works."""
    result = subprocess.run(
        [sys.executable, "scripts/run_local.py", "--check"],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "Python:" in result.stdout
    assert "Checks complete" in result.stdout


def test_run_local_help():
    """Test that scripts/run_local.py --help works."""
    result = subprocess.run(
        [sys.executable, "scripts/run_local.py", "--help"],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "--check" in result.stdout
    assert "--scene" in result.stdout


def test_convert_heic_help():
    """Test that scripts/convert_heic.py --help works."""
    result = subprocess.run(
        [sys.executable, "scripts/convert_heic.py", "--help"],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "--input_dir" in result.stdout or "-i" in result.stdout


def test_run_colmap_help():
    """Test that scripts/run-colmap.py --help works."""
    result = subprocess.run(
        [sys.executable, "scripts/run-colmap.py", "--help"],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "--input_path" in result.stdout
    assert "--output_path" in result.stdout


def test_train_help():
    """Test that scripts/train.py --help works."""
    result = subprocess.run(
        [sys.executable, "scripts/train.py", "--help"],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "--scene" in result.stdout or "-s" in result.stdout
