"""Integration tests for main.py CLI."""

import subprocess
import sys


def test_main_help():
    """Test that main.py --help works."""
    result = subprocess.run(
        [sys.executable, "main.py", "--help"],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "Gaussian Splatting Pipeline" in result.stdout
    assert "--check" in result.stdout
    assert "--run" in result.stdout
    assert "--colmap" in result.stdout
    assert "--train" in result.stdout


def test_main_check():
    """Test that main.py --check works."""
    result = subprocess.run(
        [sys.executable, "main.py", "--check"],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "Environment Check" in result.stdout
    assert "Python:" in result.stdout
    assert "PyTorch:" in result.stdout


def test_main_missing_scene():
    """Test that main.py fails gracefully with missing scene."""
    result = subprocess.run(
        [sys.executable, "main.py", "--scene", "nonexistent_scene_xyz", "--colmap"],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 1
    assert "ERROR" in result.stdout or "not found" in result.stdout.lower()


def test_main_no_args():
    """Test that main.py with no args shows help."""
    result = subprocess.run(
        [sys.executable, "main.py"],
        capture_output=True,
        text=True,
    )

    # main.py without args shows help (exit 0) or errors on missing scene
    # Both are acceptable behaviors
    assert result.returncode in [0, 1]
    # Should contain usage info or error message
    assert (
        "usage:" in result.stdout
        or "ERROR" in result.stdout
        or "help" in result.stdout.lower()
    )
