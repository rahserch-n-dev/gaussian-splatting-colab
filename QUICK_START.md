# Quick Start Guide - GPU-Accelerated Gaussian Splatting

**TL;DR:** Build Docker image → Run verification → Process your scenes 6-10x faster

## Prerequisites Check

```bash
# Check Docker
docker --version
# Need: Docker 20.10+

# Check NVIDIA GPU
docker run --rm --gpus all nvidia/cuda:12.1.1-base-ubuntu22.04 nvidia-smi
# Should show your GPU (e.g., RTX 3060)

# Check disk space
df -h
# Need: 30GB free
```

If any check fails, see [BUILD_INSTRUCTIONS.md](BUILD_INSTRUCTIONS.md#requirements).

## Step 1: Build the Image (One Time, 15-40 min)

```bash
cd gaussian-splatting-colab
docker build -t gaussian-splatting-env:latest .
```

**What this does:**
- Installs CUDA toolkit and dependencies
- Builds COLMAP from source with GPU support (this takes longest)
- Installs PyTorch with CUDA
- Builds Gaussian Splatting CUDA extensions
- Verifies CUDA support automatically

**Watch for:** Build should end with "COLMAP CUDA build verification complete ✓"

**If build fails:** See troubleshooting in [BUILD_INSTRUCTIONS.md](BUILD_INSTRUCTIONS.md#common-build-issues)

## Step 2: Verify GPU Support (2 min)

```bash
# Quick check
docker run --gpus all gaussian-splatting-env:latest colmap --version
# Should show: "COLMAP 3.9.1 ... with CUDA"

# Full verification (includes runtime smoke test)
docker run --gpus all -it gaussian-splatting-env:latest \
    bash /home/appuser/project/scripts/verify-colmap-cuda.sh
```

**Expected output:**
```
==================================================
✓ COLMAP CUDA Verification PASSED
==================================================

Summary:
  - COLMAP binary built with CUDA: ✓
  - GPU flags available in help: ✓
  - GPU device detected: ✓
  - Runtime smoke test: ✓
```

**If verification fails:** Check [docs/COLMAP_CUDA_BUILD.md](docs/COLMAP_CUDA_BUILD.md#troubleshooting)

## Step 3: Prepare Your Scene

```bash
# Create scene directory
mkdir -p scenes/myscene/images

# Copy your images (JPG/PNG)
cp /path/to/your/photos/* scenes/myscene/images/

# Verify images are there
ls scenes/myscene/images/
# Should show your images
```

**Requirements:**
- 10-200+ images (more is better, up to a point)
- JPEG or PNG format
- Reasonable overlap between consecutive images
- Consistent lighting preferred

## Step 4: Run COLMAP (5-10 min for 50 images)

```bash
# Linux/Mac
docker run --gpus all --rm \
    -v $(pwd)/scenes:/home/appuser/project/scenes \
    gaussian-splatting-env:latest \
    python /home/appuser/project/scripts/run-colmap.py \
        --input_path /home/appuser/project/scenes/myscene/images \
        --output_path /home/appuser/project/scenes/myscene

# Windows PowerShell
docker run --gpus all --rm `
    -v ${PWD}\scenes:/home/appuser/project/scenes `
    gaussian-splatting-env:latest `
    python /home/appuser/project/scripts/run-colmap.py `
        --input_path /home/appuser/project/scenes/myscene/images `
        --output_path /home/appuser/project/scenes/myscene
```

**What this does:**
- Feature extraction (GPU-accelerated SIFT)
- Feature matching (GPU-accelerated)
- Sparse reconstruction
- Undistortion and conversion

**Monitor progress:**
```bash
# Check COLMAP logs (in another terminal)
tail -f scenes/myscene/logs/colmap.log
```

**When done:** You should see `scenes/myscene/sparse/0/` with cameras, images, points data.

## Step 5: Train Gaussian Splatting (Optional)

```bash
# Run training inside container
docker run --gpus all --rm \
    -v $(pwd)/scenes:/home/appuser/project/scenes \
    gaussian-splatting-env:latest \
    python /home/appuser/gaussian-splatting/train.py \
        -s /home/appuser/project/scenes/myscene \
        -m /home/appuser/project/scenes/myscene/output
```

**Training time:** 30-60 minutes typical, outputs `.ply` point cloud model.

## Common Commands

### Interactive Shell
```bash
# Drop into container shell to debug
docker run --gpus all -it --rm \
    -v $(pwd)/scenes:/home/appuser/project/scenes \
    gaussian-splatting-env:latest bash

# Inside container:
cd /home/appuser/project
python scripts/run-colmap.py --help
```

### Check GPU Usage
```bash
# In another terminal while COLMAP runs:
watch -n 1 nvidia-smi
# Should show COLMAP using GPU memory and compute
```

### View COLMAP Output
```bash
# After COLMAP completes
ls scenes/myscene/sparse/0/
# Should see: cameras.bin, images.bin, points3D.bin

# Check image count
docker run --gpus all --rm \
    -v $(pwd)/scenes:/home/appuser/project/scenes \
    gaussian-splatting-env:latest \
    colmap model_analyzer --path /home/appuser/project/scenes/myscene/sparse/0
```

## Expected Timeline

| Step | Time | One-time? |
|------|------|-----------|
| Build Docker image | 15-40 min | ✓ Yes |
| Verify GPU support | 2 min | Optional after first time |
| Prepare scene | 5 min | Per scene |
| Run COLMAP | 5-10 min | Per scene |
| Train Gaussian Splatting | 30-60 min | Per scene |

**Total first run:** ~1 hour (then 40 min per additional scene)

## Performance Expectations

### COLMAP Time by Image Count (RTX 3060)

| Images | CPU-only (WSL2) | GPU (Docker) | Speedup |
|--------|-----------------|--------------|---------|
| 10-20 | 5-10 min | 1-2 min | 5x |
| 50 | 30-45 min | 5-7 min | 6x |
| 100 | 60-90 min | 10-12 min | 7x |
| 200+ | 2-4 hours | 20-30 min | 6-8x |

**Your mileage may vary** based on:
- Image resolution (higher = slower)
- Feature density (complex scenes = more features)
- GPU model (newer = faster)
- Matching strategy (exhaustive vs vocab_tree)

## Troubleshooting

### "Cannot connect to the Docker daemon"
```bash
# Start Docker Desktop (Windows/Mac) or Docker service (Linux)
sudo systemctl start docker  # Linux
```

### "could not select device driver"
```bash
# Install NVIDIA Container Toolkit
# See: https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html
```

### "COLMAP failed" in logs
```bash
# Check the log
cat scenes/myscene/logs/colmap.log

# Common issues:
# - Not enough images (need 10+ with overlap)
# - Poor image quality
# - No overlap between images
# - Out of GPU memory (reduce image resolution)
```

### COLMAP runs but still slow
```bash
# Verify GPU is actually being used
docker run --gpus all gaussian-splatting-env:latest nvidia-smi
# Should show GPU

# Re-run verification
docker run --gpus all -it gaussian-splatting-env:latest \
    bash /home/appuser/project/scripts/verify-colmap-cuda.sh
```

### Need help?
1. Check [BUILD_INSTRUCTIONS.md](BUILD_INSTRUCTIONS.md)
2. Check [docs/COLMAP_CUDA_BUILD.md](docs/COLMAP_CUDA_BUILD.md#troubleshooting)
3. Check COLMAP logs: `scenes/*/logs/colmap.log`

## Next Steps

- **Multiple scenes?** Just run Step 4 for each (COLMAP caches are per-scene)
- **Iterate on code?** Rebuild image, cached layers make it fast
- **Production deployment?** Use same Dockerfile on cloud GPU
- **Share with team?** Push image to Docker Hub or registry

## Comparison to Other Setups

| Setup | COLMAP GPU? | Setup Time | Maintenance |
|-------|-------------|------------|-------------|
| **This Docker** | ✅ Yes | 40 min | Easy |
| WSL2 apt COLMAP | ❌ No | 45 min | Medium |
| Windows Native | ⚠️ Maybe | 2-3 hours | Hard |

**Recommendation:** Stick with Docker for best experience.

See [docs/SETUP_COMPARISON.md](docs/SETUP_COMPARISON.md) for detailed comparison.

## Cheat Sheet

```bash
# Build
docker build -t gaussian-splatting-env:latest .

# Verify
docker run --gpus all gaussian-splatting-env:latest colmap --version

# Run COLMAP
docker run --gpus all --rm -v $(pwd)/scenes:/home/appuser/project/scenes \
    gaussian-splatting-env:latest \
    python /home/appuser/project/scripts/run-colmap.py \
        --input_path /home/appuser/project/scenes/SCENENAME/images \
        --output_path /home/appuser/project/scenes/SCENENAME

# Interactive
docker run --gpus all -it --rm -v $(pwd)/scenes:/home/appuser/project/scenes \
    gaussian-splatting-env:latest bash

# Check GPU
docker run --gpus all gaussian-splatting-env:latest nvidia-smi
```

---

**Ready?** Start with Step 1 above! 🚀
