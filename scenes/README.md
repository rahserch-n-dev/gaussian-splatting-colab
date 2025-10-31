# Scenes Directory

Place your input images and scene data here for processing with Gaussian Splatting.

## Directory Structure

Each scene should have its own subdirectory with the following structure:

```
scenes/
└── your-scene-name/
    └── images/          # Place your input photos here (.jpg, .png)
```

## Example

```
scenes/
└── my-first-scene/
    └── images/
        ├── IMG_0001.jpg
        ├── IMG_0002.jpg
        ├── IMG_0003.jpg
        └── ...
```

## Processing Pipeline

After placing images in `scenes/your-scene-name/images/`, the pipeline will create:

- `scenes/your-scene-name/sparse/` - COLMAP 3D reconstruction
- `scenes/your-scene-name/output/` - Trained Gaussian Splatting model

## Quick Start

1. Create a scene folder: `scenes/my-scene/images/`
2. Add 20+ photos of your subject from different angles
3. Run the pipeline:
   ```powershell
   docker run --rm --gpus all -v "${PWD}/scenes:/home/appuser/project/scenes" gaussian-splatting-env python scripts/run_local.py --scene my-scene --run
   ```

## Tips

- Use 20-50 images for best results
- Take photos from various angles around the subject
- Maintain consistent lighting
- Avoid motion blur
- Include sufficient overlap between images (60-80%)
