"""High-level orchestration helpers to run the full pipeline.

This module centralizes steps used in notebooks: prepare scene, run COLMAP, convert outputs, and train.
Functions are intentionally thin and delegate to the src.* modules so they stay testable.
"""
from __future__ import annotations

import os
import shutil
from typing import Optional

from src import colmap as colmap_mod
from src import training as training_mod


def prepare_scene_from_dir(src_images_dir: str, scene_name: str) -> str:
    """Prepare a scene directory by copying images from src_images_dir into scenes/<scene_name>/images.

    Returns the absolute scene path.
    """
    scene_base = os.path.abspath(os.path.join("scenes", scene_name))
    images_dir = os.path.join(scene_base, "images")
    os.makedirs(images_dir, exist_ok=True)
    # copy files (not recursive) to images folder
    for fname in os.listdir(src_images_dir):
        src = os.path.join(src_images_dir, fname)
        if os.path.isfile(src):
            dst = os.path.join(images_dir, fname)
            shutil.copy2(src, dst)
    return scene_base


def run_full_pipeline(scene_name: str, src_images_dir: Optional[str] = None, aabb_scale: int = 16, iterations: int = 30000) -> None:
    """Run the full pipeline for a scene.

    If src_images_dir is provided, images are copied into `scenes/<scene_name>/images` first.
    This function delegates to the colmap/convert/training modules and raises on failures.
    """
    if src_images_dir:
        prepare_scene_from_dir(src_images_dir, scene_name)

    scene_base = os.path.abspath(os.path.join("scenes", scene_name))
    images_dir = os.path.join(scene_base, "images")
    if not os.path.isdir(images_dir):
        raise FileNotFoundError(f"Images folder missing: {images_dir}")

    # 1) COLMAP (includes conversion to Gaussian Splatting format)
    colmap_mod.run_colmap(images_dir, scene_base, aabb_scale=aabb_scale, wrapper_script=os.path.join("scripts", "run-colmap.py"))

    # Note: The COLMAP convert.py script handles conversion, so no separate step needed

    # 2) Train
    training_mod.run_training(scene_base, pipeline="gaussian", iterations=iterations, wrapper_script=os.path.join("scripts", "train.py"))
