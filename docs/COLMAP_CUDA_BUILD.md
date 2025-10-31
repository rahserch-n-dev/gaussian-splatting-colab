# Building COLMAP with CUDA Support

## Problem
The standard COLMAP package from Ubuntu's apt repository (`apt install colmap`) is compiled **without CUDA support**. This means:
- GPU flags like `SiftExtraction.use_gpu` are ignored
- Feature extraction runs on CPU only (~10-20x slower)
- Matching runs on CPU only (even slower for large image sets)

## Solution
We build COLMAP from source with CUDA enabled in the Dockerfile.

### Key Implementation Details
This implementation uses **canonical CMake flags and robust verification**:
- **`-DWITH_CUDA=ON`** instead of `-DCUDA_ENABLED=ON` (canonical flag used by COLMAP)
- **`-DCMAKE_INSTALL_PREFIX=/usr/local`** to ensure predictable installation paths
- **Build-time verification** that fails fast if CUDA support is missing
- **Runtime smoke test** script that actually runs COLMAP with GPU flags on test images

## What Changed
The Dockerfile now:
1. Installs COLMAP build dependencies (Boost, Eigen, Ceres, FLANN, FreeImage, etc.)
2. Clones COLMAP 3.9.1 from the official repository
3. Builds with CMake flags:
   - `-DWITH_CUDA=ON` - Enables GPU-accelerated SIFT (canonical flag name)
   - `-DCMAKE_CUDA_ARCHITECTURES="75;80;86;89;90"` - Supports RTX 2000-4000, A100, H100
   - `-DCMAKE_INSTALL_PREFIX=/usr/local` - Ensures correct installation path
   - `-DWITH_OPENGL=ON` - Enables OpenGL rendering
   - `-DGUI_ENABLED=ON` - Includes Qt GUI (for debugging)
   - `-DCGAL_ENABLED=ON` - Computational geometry support
4. Installs COLMAP system-wide in `/usr/local`
5. Verifies CUDA support during build with robust checks:
   - Checks version string doesn't contain "without CUDA"
   - Verifies GPU flags (`SiftExtraction.use_gpu`, `SiftMatching.use_gpu`) are available

## Build Time
- **First build:** 15-40 minutes (depending on CPU)
- **Subsequent builds:** Seconds (if only project code changed, COLMAP layers are cached)

## How to Rebuild the Docker Image

### 1. Build the image
```bash
docker build -t gaussian-splatting-env:latest .
```

This will:
- Install all dependencies
- Build COLMAP with CUDA (takes longest, but cached)
- Build gaussian-splatting CUDA extensions
- Install your project code

### 2. Verify COLMAP CUDA support
```bash
# Start container with GPU access (IMPORTANT: use --gpus all)
docker run --gpus all -it gaussian-splatting-env:latest bash

# Inside container, run robust verification script
bash /home/appuser/project/scripts/verify-colmap-cuda.sh
```

Expected output:
```
==================================================
COLMAP CUDA Verification Script
==================================================

=== Step 1: Check COLMAP Version ===
COLMAP 3.9.1 (Commit ... with CUDA)

✓ COLMAP version shows 'with CUDA' - good!

=== Step 2: Check for GPU Flags in Help Text ===
✓ Found SiftExtraction.use_gpu flag in feature_extractor
✓ Found SiftMatching.use_gpu flag in exhaustive_matcher

=== Step 3: Check GPU Device Availability ===
✓ nvidia-smi is available
0, NVIDIA GeForce RTX 3060, 536.67, 12288 MiB

=== Step 4: Runtime Smoke Test ===
Creating test images and running COLMAP with GPU flags...
Running: colmap feature_extractor with --SiftExtraction.use_gpu 1
✓ Feature extraction with GPU flag succeeded
✓ Log contains CUDA/GPU references - GPU was likely used

==================================================
✓ COLMAP CUDA Verification PASSED
==================================================

Summary:
  - COLMAP binary built with CUDA: ✓
  - GPU flags available in help: ✓
  - GPU device detected: ✓
  - Runtime smoke test: ✓

Your COLMAP installation is ready for GPU-accelerated
feature extraction and matching!
```

If you see "✗ FATAL: COLMAP was built WITHOUT CUDA support", the build failed and you need to check the CMake logs.

## Supported GPU Architectures
The build targets these NVIDIA GPU compute capabilities:
- **7.5:** RTX 2060, 2070, 2080, Quadro RTX
- **8.0:** A100, A30
- **8.6:** RTX 3050, 3060, 3070, 3080, 3090
- **8.9:** RTX 4060, 4070, 4080, 4090, L4, L40
- **9.0:** H100

Your RTX 3060 uses compute capability **8.6**, so it's fully supported.

## Performance Impact
With GPU-enabled COLMAP:
- **Feature extraction:** 5-10x faster (SIFT on GPU)
- **Feature matching:** 10-50x faster (GPU exhaustive or vocab tree matching)
- **Total COLMAP time:** Typically 5-15 minutes instead of 1-3 hours for ~50-100 images

## Troubleshooting

### Build fails with CUDA errors
Check that:
- Base image has CUDA toolkit (we use `nvidia/cuda:12.1.1-devel-ubuntu22.04`)
- CMake finds nvcc: Inside build, `which nvcc` should show `/usr/local/cuda/bin/nvcc`
- CUDA version matches your driver (12.1.1 requires driver >= 530)

### COLMAP built but still shows "without CUDA"
The verification step in the Dockerfile (lines 76-88) will catch this and **fail the build automatically**. If you see this during build:
1. Check Docker build logs for CMake configuration warnings about CUDA
2. Ensure `-DWITH_CUDA=ON` is set in the cmake command (line 66)
3. Verify nvcc is in PATH during build: `docker run <image-id> which nvcc`
4. Check CMake detected CUDA: Look for "Found CUDA: ON" in build output

### Verification script reports "without CUDA" after container starts
This should never happen if the Docker build succeeded (build-time verification prevents this).
If it does:
1. You may have an older cached layer - rebuild with `--no-cache`:
   ```bash
   docker build --no-cache -t gaussian-splatting-env:latest .
   ```
2. Check if you're running the right image: `docker images` and verify the timestamp

### GPU not detected at runtime
This is different from CUDA support in the binary. Runtime GPU detection requires:
```bash
docker run --gpus all ...  # Must pass GPU to container
```

Inside container:
```bash
nvidia-smi  # Should show your GPU
```

### OpenGL context errors
Even with CUDA-enabled COLMAP, you might see OpenGL errors in headless environments. This is normal and handled by the code - it will retry with `--no_gpu` flag for visualization, but SIFT/matching will still use CUDA.

## Alternative: Prebuilt CUDA-enabled COLMAP
If the source build is too slow, you can try:
1. Official COLMAP Docker images (if they ship with CUDA)
2. Pre-built binaries from COLMAP releases (check if CUDA-enabled builds exist)

However, building from source guarantees compatibility with your specific CUDA version (12.1.1) and GPU architecture.

## References
- [COLMAP Installation Guide](https://colmap.github.io/install.html)
- [COLMAP GPU Acceleration](https://colmap.github.io/faq.html#gpu-acceleration)
- [NVIDIA CUDA Compute Capabilities](https://developer.nvidia.com/cuda-gpus)
