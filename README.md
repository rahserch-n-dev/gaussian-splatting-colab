## Gaussian Splatting Colab (A100-Optimized)

This repo contains a ready-to-run Google Colab pipeline for 3D Gaussian Splatting using high-powered A100 GPUs.

## Features

- Headless COLMAP installation
- Gaussian Splatting pipeline
- Fast training via A100
- Support for image upload or Google Drive mount

## Quick Start

1. Open `Gaussian_Splatting_Colab.ipynb` in Google Colab.
2. Upload your image set or mount Drive.
3. Run the cells to generate splats.

## Folder Layout

- `scripts/` — Python helper scripts for COLMAP and training
- `Gaussian_Splatting_Colab.ipynb` — The main Colab notebook

## Dependencies

- Python 3.10+
- PyTorch w/ CUDA
- COLMAP
- Gaussian Splatting Repo (Inria) gaussian-splatting-colab