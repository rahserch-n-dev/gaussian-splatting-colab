"""Integration tests for the orchestrator module."""

import os
from pathlib import Path

import pytest

from src import orchestrator


def test_prepare_scene_from_dir(temp_dir: Path, sample_images_dir: Path):
    """Test scene preparation copies images correctly."""
    scene_name = "test_scene"

    # Create the scene
    scene_path = orchestrator.prepare_scene_from_dir(str(sample_images_dir), scene_name)

    # Verify structure
    assert os.path.isdir(scene_path)
    images_dir = os.path.join(scene_path, "images")
    assert os.path.isdir(images_dir)

    # Verify images were copied
    image_files = [f for f in os.listdir(images_dir) if f.endswith(".jpg")]
    assert len(image_files) == 5  # We created 5 test images

    # Verify image names
    expected_names = [f"test_{i:03d}.jpg" for i in range(5)]
    for name in expected_names:
        assert name in image_files


def test_prepare_scene_idempotent(temp_dir: Path, sample_images_dir: Path):
    """Test that preparing a scene twice doesn't cause errors."""
    scene_name = "test_scene"

    # Prepare twice
    scene_path1 = orchestrator.prepare_scene_from_dir(
        str(sample_images_dir), scene_name
    )
    scene_path2 = orchestrator.prepare_scene_from_dir(
        str(sample_images_dir), scene_name
    )

    # Should return same path
    assert scene_path1 == scene_path2

    # Images should still be there
    images_dir = os.path.join(scene_path1, "images")
    image_files = [f for f in os.listdir(images_dir) if f.endswith(".jpg")]
    assert len(image_files) == 5


def test_prepare_scene_with_existing_files(temp_dir: Path, sample_images_dir: Path):
    """Test scene preparation when target already has some files."""
    scene_name = "test_scene"

    # Create scene directory manually with one file
    scene_dir = Path("scenes") / scene_name / "images"
    scene_dir.mkdir(parents=True, exist_ok=True)
    (scene_dir / "existing.txt").write_text("existing file")

    # Prepare scene
    scene_path = orchestrator.prepare_scene_from_dir(str(sample_images_dir), scene_name)

    images_dir = os.path.join(scene_path, "images")

    # New images should be there
    image_files = [f for f in os.listdir(images_dir) if f.endswith(".jpg")]
    assert len(image_files) == 5

    # Existing file should still be there
    assert os.path.exists(os.path.join(images_dir, "existing.txt"))


def test_run_full_pipeline_missing_images(temp_dir: Path):
    """Test that pipeline fails gracefully with missing images."""
    scene_name = "nonexistent_scene"

    with pytest.raises(FileNotFoundError) as exc_info:
        orchestrator.run_full_pipeline(scene_name)

    assert "Images folder missing" in str(exc_info.value)


def test_run_full_pipeline_directory_structure(
    temp_dir: Path, sample_images_dir: Path, monkeypatch
):
    """Test that pipeline validates directory structure."""
    # Change to temp directory for this test
    monkeypatch.chdir(temp_dir)

    scene_name = "test_scene"

    # Create scenes directory
    scenes_dir = temp_dir / "scenes"
    scenes_dir.mkdir()

    # Prepare scene should work
    scene_path = orchestrator.prepare_scene_from_dir(str(sample_images_dir), scene_name)

    # Verify the structure was created correctly
    assert os.path.isdir(scene_path)
    assert os.path.isdir(os.path.join(scene_path, "images"))
