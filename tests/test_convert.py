"""Unit tests for convert module."""

from pathlib import Path
from unittest.mock import patch

import pytest

from src import convert


def test_run_convert_no_wrapper_script():
    """Test that run_convert raises error when no wrapper script provided."""
    with pytest.raises(FileNotFoundError) as exc_info:
        convert.run_convert("/fake/path", wrapper_script=None)

    assert "No convert wrapper script found" in str(exc_info.value)


def test_run_convert_missing_wrapper_script():
    """Test that run_convert raises error when wrapper script doesn't exist."""
    with pytest.raises(FileNotFoundError) as exc_info:
        convert.run_convert("/fake/path", wrapper_script="/nonexistent/script.py")

    assert "No convert wrapper script found" in str(exc_info.value)


def test_run_convert_with_valid_script(tmp_path: Path):
    """Test run_convert with a valid wrapper script."""
    # Create a fake wrapper script
    fake_script = tmp_path / "convert_wrapper.py"
    fake_script.write_text("#!/usr/bin/env python3\nprint('converting')\n")
    fake_script.chmod(0o755)

    scene_path = str(tmp_path / "scene")

    with patch("subprocess.check_call") as mock_check_call:
        convert.run_convert(scene_path, wrapper_script=str(fake_script))

        # Verify subprocess was called correctly
        assert mock_check_call.called
        call_args = mock_check_call.call_args[0][0]
        assert str(fake_script) in call_args
        assert scene_path in call_args
