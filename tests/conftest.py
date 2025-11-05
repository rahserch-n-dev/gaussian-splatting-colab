"""Pytest configuration and shared fixtures for tests."""

import shutil
import tempfile
from pathlib import Path
from typing import Generator

import pytest
from PIL import Image


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for test files."""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def sample_images_dir(temp_dir: Path) -> Path:
    """Create sample test images for COLMAP testing.

    Generates 5 simple test images with slight variations.
    """
    images_dir = temp_dir / "images"
    images_dir.mkdir(parents=True)

    # Create 5 test images with different patterns
    patterns = [
        ("gray", (128, 128, 128)),
        ("red", (255, 100, 100)),
        ("green", (100, 255, 100)),
        ("blue", (100, 100, 255)),
        ("yellow", (255, 255, 100)),
    ]

    for i, (name, color) in enumerate(patterns):
        img = Image.new("RGB", (640, 480), color)
        # Add some variation (simple gradient)
        pixels = img.load()
        for y in range(480):
            for x in range(640):
                r, g, b = pixels[x, y]
                variation = int((x + y) / 10)
                pixels[x, y] = (
                    max(0, min(255, r + variation)),
                    max(0, min(255, g + variation)),
                    max(0, min(255, b + variation)),
                )

        img.save(images_dir / f"test_{i:03d}.jpg", "JPEG", quality=95)

    return images_dir


@pytest.fixture
def sample_scene_dir(temp_dir: Path, sample_images_dir: Path) -> Path:
    """Create a complete sample scene directory structure.

    Returns a scene directory with:
    - images/ folder with test images
    """
    scene_dir = temp_dir / "test_scene"
    scene_dir.mkdir(parents=True)

    # Copy images
    images_dest = scene_dir / "images"
    shutil.copytree(sample_images_dir, images_dest)

    return scene_dir


@pytest.fixture
def mock_colmap_output(sample_scene_dir: Path) -> Path:
    """Create mock COLMAP output structure for testing.

    Creates the directory structure that COLMAP would produce:
    - sparse/0/ with dummy camera/image/point files
    """
    sparse_dir = sample_scene_dir / "sparse" / "0"
    sparse_dir.mkdir(parents=True)

    # Create dummy files (minimal valid structure)
    # In real COLMAP these would be binary files
    (sparse_dir / "cameras.bin").write_bytes(b"MOCK_CAMERAS")
    (sparse_dir / "images.bin").write_bytes(b"MOCK_IMAGES")
    (sparse_dir / "points3D.bin").write_bytes(b"MOCK_POINTS")

    # Also create text versions (more common in testing)
    (sparse_dir / "cameras.txt").write_text(
        "# Camera list with one line of data per camera:\n"
        "#   CAMERA_ID, MODEL, WIDTH, HEIGHT, PARAMS[]\n"
        "1 PINHOLE 640 480 320 240 320 240\n"
    )

    (sparse_dir / "images.txt").write_text(
        "# Image list with two lines of data per image:\n"
        "#   IMAGE_ID, QW, QX, QY, QZ, TX, TY, TZ, CAMERA_ID, NAME\n"
        "#   POINTS2D[] as (X, Y, POINT3D_ID)\n"
        "1 1 0 0 0 0 0 0 1 test_000.jpg\n\n"
    )

    (sparse_dir / "points3D.txt").write_text(
        "# 3D point list with one line of data per point:\n"
        "#   POINT3D_ID, X, Y, Z, R, G, B, ERROR, TRACK[] as (IMAGE_ID, POINT2D_IDX)\n"
    )

    return sample_scene_dir


@pytest.fixture
def project_root() -> Path:
    """Get the project root directory."""
    # Go up from tests/ to project root
    return Path(__file__).parent.parent


@pytest.fixture(autouse=True)
def setup_pythonpath(project_root: Path) -> None:
    """Ensure project root is in sys.path for all tests."""
    import sys

    root_str = str(project_root)
    if root_str not in sys.path:
        sys.path.insert(0, root_str)
