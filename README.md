# Gaussian Splatting (Local-first)

This repository started as a Colab-first pipeline for Gaussian Splatting, but this README focuses on local (Windows) development and experimentation without notebooks.

Key goals in local mode:
- Run and iterate the pipeline from the command line (PowerShell)
- Avoid Jupyter/Colab; provide simple CLI tooling
- Keep reproducible environments using virtualenv or Poetry

Project layout highlights:

- `src/` - Source code (migrate notebook logic here)
- `scripts/` - Orchestration and utilities (see `scripts/run_local.py`)
- `notebooks/` - Reference examples (not required for local runs)
- `docs/` - Guides and project conventions

Quick Windows PowerShell setup (recommended)

1) Create and activate a venv in PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2) Upgrade pip and install base deps:

```powershell
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements.txt
# install lightweight utilities used by the local runner
python -m pip install psutil
```

3) PyTorch guidance (Windows):

- If you have an NVIDIA GPU and want CUDA-enabled PyTorch, visit https://pytorch.org/ and follow the Windows installer instructions (select the correct CUDA version).
- If you do not need GPU or can't install CUDA, install the CPU-only wheel:

```powershell
python -m pip install "torch==2.9.0+cpu" --index-url https://download.pytorch.org/whl/cpu
```

Repository convenience

- A local orchestration script is provided at `scripts/run_local.py` to perform safe checks and run pipeline stages. It uses the same Python interpreter (the activated venv) to invoke internal scripts.

## Docker Setup (Recommended for GPU-Accelerated COLMAP)

**NEW:** This project now includes a Docker environment with **GPU-enabled COLMAP** for 5-10x faster feature extraction and matching.

### Quick Start with Docker

```bash
# Build the Docker image (15-40 min first time, then cached)
docker build -t gaussian-splatting-env:latest .

# Verify COLMAP has CUDA support
docker run --gpus all -it gaussian-splatting-env:latest bash /home/appuser/project/scripts/verify-colmap-cuda.sh

# Run the pipeline on your scene
docker run --gpus all --rm \
    -v ${PWD}/scenes:/home/appuser/project/scenes \
    gaussian-splatting-env:latest \
    python /home/appuser/project/scripts/run-colmap.py \
        --input_path /home/appuser/project/scenes/myscene/images \
        --output_path /home/appuser/project/scenes/myscene
```

**Why Docker?** The standard COLMAP from `apt install colmap` lacks CUDA support. Our Dockerfile builds COLMAP from source with GPU acceleration, giving you **5-10x faster SIFT extraction** and **10-50x faster matching**.

**See:** [BUILD_INSTRUCTIONS.md](BUILD_INSTRUCTIONS.md) for detailed build guide and [docs/COLMAP_CUDA_BUILD.md](docs/COLMAP_CUDA_BUILD.md) for technical details.

## Native Windows Setup (Alternative)

COLMAP is a system dependency. On Windows you have three choices:
  - **Docker** (recommended - includes GPU-enabled COLMAP, see above)
  - Use WSL2 and install COLMAP inside the Linux environment ([WSL2 Guide](docs/WSL2.md))
  - Install native COLMAP binaries for Windows (if available, but typically lacks GPU support)

Notes about COLMAP and scene layout

- The pipeline expects scenes in `scenes/{scene_name}/images/`.
- COLMAP outputs (sparse, dense) should be placed under `scenes/{scene_name}/` and the conversion step expects this layout.

How to run locally (safe, example flow)

1. Prepare images in `scenes/myscene/images/`.
2. Run the runner in check-only mode to validate environment:

```powershell
python .\scripts\run_local.py --check
```

3. If checks pass, run the full pipeline (this will call COLMAP / conversion / training scripts as available):

```powershell
python .\scripts\run_local.py --scene myscene --run
```

Developer notes

- Prefer extracting reusable logic from notebooks into `src/` as you iterate.
- Keep `requirements.txt` in sync with `pyproject.toml` if you adopt Poetry.
- Use `pre-commit` (already configured) to keep formatting and linting consistent.

## Performance Comparison

| Setup | COLMAP Time (50 images) | GPU Acceleration |
|-------|-------------------------|------------------|
| Docker (CUDA-enabled) | 5-10 min | ✓ SIFT + Matching |
| Native Windows/WSL2 (apt COLMAP) | 30-60 min | ✗ CPU only |
| Native Windows (manual CUDA build) | 5-10 min | ✓ If built correctly |

**Recommendation:** Use Docker for easiest setup with guaranteed GPU acceleration.

## Troubleshooting

### Docker Issues
- **"COLMAP built without CUDA"**: The Dockerfile has build-time verification that will fail the build if CUDA is missing. Check Docker build logs for CMake errors.
- **"nvidia-smi not found in container"**: Make sure you use `--gpus all` flag when running the container.
- **Build takes forever**: COLMAP compilation is slow (15-40 min). This is normal and only happens once (layers are cached).

### Native Setup Issues
- If `torch` is installed but `torch.cuda.is_available()` is false, you are running the CPU build of PyTorch or the machine lacks a supported CUDA driver. See the PyTorch website for Windows CUDA install instructions.
- If you need a reproducible environment for heavy experiments consider using WSL2 with GPU passthrough or Docker (recommended).

## Additional Documentation

- [BUILD_INSTRUCTIONS.md](BUILD_INSTRUCTIONS.md) - Complete Docker build guide with troubleshooting
- [docs/COLMAP_CUDA_BUILD.md](docs/COLMAP_CUDA_BUILD.md) - Technical details on COLMAP CUDA compilation
- [docs/WSL2.md](docs/WSL2.md) - WSL2 setup guide for Windows users
- [docs/LOCAL_SETUP.md](docs/LOCAL_SETUP.md) - Native local development setup