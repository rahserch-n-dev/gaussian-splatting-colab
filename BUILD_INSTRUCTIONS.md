# Docker Build Instructions - COLMAP with CUDA

## Quick Start

```bash
# Build the Docker image (15-40 min first time, then cached)
docker build -t gaussian-splatting-env:latest .

# Verify COLMAP has CUDA support
docker run --gpus all -it gaussian-splatting-env:latest bash -c "colmap --version"
# Should show: "COLMAP 3.9.1 ... with CUDA"

# Run full verification
docker run --gpus all -it gaussian-splatting-env:latest bash /home/appuser/project/scripts/verify-colmap-cuda.sh
```

## What This Build Does

### 1. System Dependencies (Dockerfile lines 12-53)
- Python 3.10, build tools, OpenGL/Mesa libraries
- COLMAP build dependencies: Boost, Eigen3, Ceres, FLANN, FreeImage, Qt5, CGAL

### 2. COLMAP Build from Source (lines 55-74)
**Why:** Ubuntu's apt package lacks CUDA support
**How:** Clone COLMAP 3.9.1 and build with:
```cmake
-DWITH_CUDA=ON                              # GPU-accelerated SIFT
-DCMAKE_CUDA_ARCHITECTURES="75;80;86;89;90" # Modern NVIDIA GPUs
-DCMAKE_INSTALL_PREFIX=/usr/local           # Standard install location
-DWITH_OPENGL=ON                            # OpenGL rendering
-DGUI_ENABLED=ON                            # Qt GUI for debugging
```

**Build time:** 15-40 minutes (cached for future builds)

### 3. Build-Time Verification (lines 76-88)
Automatically fails the build if:
- `colmap --version` contains "without CUDA"
- `SiftExtraction.use_gpu` flag is missing
- `SiftMatching.use_gpu` flag is missing

### 4. Python Environment & Gaussian Splatting (lines 90-120)
- Creates Python virtual environment
- Installs PyTorch with CUDA 12.1
- Builds gaussian-splatting CUDA extensions
- Installs your project code

## Build Timeline

| Step | Time | Cacheable |
|------|------|-----------|
| System deps | 2-5 min | ✓ Yes |
| COLMAP build | 15-40 min | ✓ Yes (until deps change) |
| PyTorch install | 3-5 min | ✓ Yes |
| Gaussian-splatting | 5-10 min | ✓ Yes |
| Project code | 10 sec | ✗ No (changes frequently) |

**Total first build:** 25-60 minutes
**Rebuild after code change:** 10-30 seconds (only project layer rebuilds)

## Requirements

### Host System
- Docker with NVIDIA Container Toolkit
- NVIDIA GPU with driver >= 530 (for CUDA 12.1)
- At least 30GB free disk space (final image ~24GB)

### Verify Prerequisites
```bash
# Check Docker
docker --version

# Check NVIDIA runtime
docker run --rm --gpus all nvidia/cuda:12.1.1-base-ubuntu22.04 nvidia-smi

# Should show your GPU
```

## Common Build Issues

### "CUDA not found" during CMake
**Symptom:** CMake can't find CUDA toolkit
**Fix:** Base image should have `nvidia/cuda:12.1.1-devel-ubuntu22.04` (has nvcc)
```bash
# Verify in Dockerfile line 4:
FROM nvidia/cuda:12.1.1-devel-ubuntu22.04
```

### "ERROR: COLMAP built without CUDA support"
**Symptom:** Build-time verification fails
**Cause:** CMake didn't enable CUDA (missing dependencies or nvcc not found)
**Debug:**
```bash
# Look for this in build logs:
-- Found CUDA: /usr/local/cuda (found version "12.1")

# If not found, check:
docker run nvidia/cuda:12.1.1-devel-ubuntu22.04 which nvcc
# Should output: /usr/local/cuda/bin/nvcc
```

### Build hangs at COLMAP compilation
**Symptom:** Ninja build appears stuck
**Cause:** COLMAP is a large C++ project, compilation is genuinely slow
**Fix:** Be patient. On a 4-core CPU, expect 20-30 min. Monitor with:
```bash
# In another terminal:
docker ps  # Get container ID
docker stats <container-id>  # Should show CPU usage
```

### "out of space" error
**Symptom:** Build fails with disk space error
**Cause:** Docker image + build layers + caches need ~30GB
**Fix:**
```bash
# Clean up old images/containers
docker system prune -a

# Check available space
df -h
```

## Verification After Build

### Quick Check
```bash
docker run --gpus all gaussian-splatting-env:latest colmap --version
# Expected: "COLMAP 3.9.1 (Commit <hash> on <date> with CUDA)"
```

### Full Verification
```bash
docker run --gpus all -it gaussian-splatting-env:latest bash

# Inside container:
bash /home/appuser/project/scripts/verify-colmap-cuda.sh
```

This runs:
1. ✓ Version string check (no "without CUDA")
2. ✓ GPU flags available in help text
3. ✓ nvidia-smi detects your GPU
4. ✓ Runtime smoke test (extract features from test images with GPU flag)

Expected result: All checks pass, summary shows ✓

## Using the Built Image

### Interactive Session
```bash
docker run --gpus all -it --rm \
    -v $(pwd)/scenes:/home/appuser/project/scenes \
    gaussian-splatting-env:latest bash
```

### Run Pipeline
```bash
docker run --gpus all --rm \
    -v $(pwd)/scenes:/home/appuser/project/scenes \
    gaussian-splatting-env:latest \
    python /home/appuser/project/scripts/run-colmap.py \
        --input_path /home/appuser/project/scenes/myscene/images \
        --output_path /home/appuser/project/scenes/myscene
```

## Rebuilding

### Full Rebuild (clean)
```bash
docker build --no-cache -t gaussian-splatting-env:latest .
```

### Incremental (after code changes)
```bash
# Just re-run normal build - uses cached layers
docker build -t gaussian-splatting-env:latest .
```

### Rebuild Only COLMAP (after dependency changes)
```bash
# Build up to COLMAP layer, then continue
docker build --target <layer> -t temp .  # Not needed - just rebuild normally
```

## Performance Expectations

With CUDA-enabled COLMAP on RTX 3060 (12GB):

| Dataset Size | CPU-only COLMAP | GPU COLMAP | Speedup |
|--------------|-----------------|------------|---------|
| 10-20 images | 5-10 min | 1-2 min | 5x |
| 50-100 images | 30-60 min | 5-10 min | 6-10x |
| 200+ images | 2-4 hours | 15-30 min | 8-12x |

**Note:** Actual speedup depends on image resolution, feature density, and matching strategy.

## Next Steps

After successful build:
1. Run verification script (see above)
2. Test with a small scene (10-20 images)
3. Check COLMAP logs for GPU usage confirmation
4. Run full pipeline on your target dataset

## References

- [COLMAP Installation](https://colmap.github.io/install.html)
- [COLMAP CUDA Support](https://colmap.github.io/faq.html#gpu-acceleration)
- [Detailed CUDA Build Guide](docs/COLMAP_CUDA_BUILD.md)
- [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html)
