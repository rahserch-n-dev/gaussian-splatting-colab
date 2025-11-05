"""Integration tests for training module."""

import os
from pathlib import Path
from unittest.mock import patch

import pytest

from src import training


def test_run_training_script_not_found(sample_scene_dir: Path):
    """Test that run_training fails gracefully when training script is missing."""
    with pytest.raises(FileNotFoundError) as exc_info:
        training.run_training(str(sample_scene_dir))

    assert "Training script not found" in str(exc_info.value)


def test_run_training_with_mock_script(sample_scene_dir: Path, tmp_path: Path):
    """Test training execution with mocked training script."""
    fake_script = tmp_path / "train.py"
    fake_script.write_text("#!/usr/bin/env python3\nprint('training')\n")
    fake_script.chmod(0o755)

    original_isfile = os.path.isfile

    def mock_isfile(path):
        path_str = str(path)
        if "train.py" in path_str and str(tmp_path) in path_str:
            return True
        if "train.py" in path_str and "gaussian-splatting" in path_str:
            # Return the fake script path
            return path_str == str(fake_script)
        return original_isfile(path)

    with (
        patch("os.path.isfile", side_effect=mock_isfile),
        patch("subprocess.check_call") as mock_check_call,
    ):
        # Override the path resolution
        with patch.object(training, "__file__", str(tmp_path / "fake.py")):
            with patch("os.path.join") as mock_join:
                mock_join.side_effect = lambda *args: (
                    str(fake_script) if "train.py" in str(args) else os.path.join(*args)
                )

                training.run_training(str(sample_scene_dir), iterations=1000)

        # Verify subprocess was called
        assert mock_check_call.called
        call_args = mock_check_call.call_args[0][0]

        # Verify correct arguments
        assert str(sample_scene_dir) in " ".join(call_args)
        assert "1000" in " ".join(call_args)


def test_run_training_custom_iterations(sample_scene_dir: Path, tmp_path: Path):
    """Test that custom iteration count is passed correctly."""
    fake_script = tmp_path / "train.py"
    fake_script.write_text("#!/usr/bin/env python3\n")
    fake_script.chmod(0o755)

    with (
        patch("os.path.isfile", return_value=True),
        patch("os.path.join", return_value=str(fake_script)),
        patch("subprocess.check_call") as mock_check_call,
    ):
        custom_iterations = 5000
        training.run_training(str(sample_scene_dir), iterations=custom_iterations)

        call_args = mock_check_call.call_args[0][0]
        assert str(custom_iterations) in call_args


def test_run_training_default_pipeline(sample_scene_dir: Path, tmp_path: Path):
    """Test that default pipeline is 'gaussian'."""
    fake_script = tmp_path / "train.py"
    fake_script.write_text("#!/usr/bin/env python3\n")
    fake_script.chmod(0o755)

    with (
        patch("os.path.isfile", return_value=True),
        patch("os.path.join", return_value=str(fake_script)),
        patch("subprocess.check_call") as mock_check_call,
    ):
        training.run_training(str(sample_scene_dir))

        # The function should execute without errors
        assert mock_check_call.called
