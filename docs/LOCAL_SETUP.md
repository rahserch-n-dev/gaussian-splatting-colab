Local setup and best practices (Windows, local-only)

1. Environment
- Use a virtualenv for this repo. From PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements.txt
```

- If you prefer Poetry later, it's fine — but virtualenv keeps things simple on Windows.

2. GPU / PyTorch
- For GPU-enabled PyTorch on Windows, use the installer instructions at https://pytorch.org/ and pick the correct CUDA toolkit matching your NVIDIA driver.
- If you don't need GPU, the CPU wheel is acceptable: `pip install "torch==2.9.0+cpu" --index-url https://download.pytorch.org/whl/cpu`.

3. COLMAP

**Recommended: Use Docker with GPU-enabled COLMAP**

This project includes a Dockerfile that builds COLMAP from source with CUDA support for 5-10x faster processing:

```bash
# Build the image (one time, 15-40 min)
docker build -t gaussian-splatting-env:latest .

# Run pipeline in Docker
docker run --gpus all --rm \
    -v ${PWD}/scenes:/home/appuser/project/scenes \
    gaussian-splatting-env:latest \
    python /home/appuser/project/scripts/run-colmap.py \
        --input_path /home/appuser/project/scenes/myscene/images \
        --output_path /home/appuser/project/scenes/myscene
```

See [BUILD_INSTRUCTIONS.md](../BUILD_INSTRUCTIONS.md) and [COLMAP_CUDA_BUILD.md](COLMAP_CUDA_BUILD.md) for details.

**Alternative native options:**
- WSL2 (install Ubuntu, then `apt install colmap`) - but this gives CPU-only COLMAP
- Native Windows build if available - rarely has GPU support
- Build COLMAP from source on Windows - complex, use Docker instead

4. Source organization
- Extract reusable logic from notebooks into `src/` (e.g., `src/colmap/`, `src/training/`). Keep scripts in `scripts/` thin and delegating to `src/`.

5. Testing & CI
- Add simple unit tests for core logic in `tests/` (pytest). Keep tests fast and deterministic.
- Add a GitHub Actions workflow that runs `pre-commit` and `pytest` on push.

6. Quick run
- Prepare images at `scenes/<name>/images/` and run from PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
python .\scripts\run_local.py --scene myscene --check
python .\scripts\run_local.py --scene myscene --run
```

7. PyTorch install (Windows)

- Recommended: use the official PyTorch selector at https://pytorch.org/ to get the exact pip command for your CUDA version. Typical options:

  - CPU-only (works without GPU drivers):

    ```powershell
    python -m pip install "torch==2.9.0+cpu" --index-url https://download.pytorch.org/whl/cpu
    python -m pip install torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
    ```

  - CUDA-enabled (pick the correct CUDA version matching your NVIDIA driver):

    1. Check driver availability with `nvidia-smi` (PowerShell/WSL/terminal). If `nvidia-smi` is not found, you may not have the NVIDIA driver installed or visible in WSL.
    2. Go to https://pytorch.org/, set OS=Windows, Package=pip, Language=Python, CUDA=your_cuda_version, and copy the command shown.

- If you plan to use WSL2 for COLMAP/training, install CUDA inside WSL and use the Linux pip wheel recommended by the PyTorch site.

8. Poetry vs venv

- If you later decide to use Poetry, keep `pyproject.toml` as the source of truth and export a `requirements.txt` for environments where Poetry is not used:

```powershell
poetry export -f requirements.txt --without-hashes -o requirements.txt
```

This keeps `pyproject.toml` and `requirements.txt` aligned.
