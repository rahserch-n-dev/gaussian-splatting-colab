# Setup Options Comparison

This guide helps you choose the best environment setup for your Gaussian Splatting pipeline.

## Quick Recommendation

**For most users: Use Docker** - It's the fastest way to get GPU-accelerated COLMAP with guaranteed compatibility.

## Comparison Table

| Factor | Docker (Recommended) | WSL2 Native | Windows Native |
|--------|---------------------|-------------|----------------|
| **Setup Time** | 15-40 min (one-time build) | 30-60 min | 1-3 hours |
| **COLMAP GPU Support** | ✅ Built-in (CUDA-enabled) | ❌ CPU only (apt version) | ⚠️ Depends on build |
| **COLMAP Performance** | 5-10 min (50 images) | 30-60 min (50 images) | Varies widely |
| **PyTorch GPU** | ✅ Yes | ✅ Yes | ✅ Yes |
| **Complexity** | Low (pre-configured) | Medium | High |
| **Maintenance** | Easy (rebuild image) | Medium (manual updates) | High (manual deps) |
| **Portability** | ✅ Runs anywhere | Linux-only | Windows-only |
| **Reproducibility** | ✅ Dockerfile versioned | ⚠️ Manual setup | ⚠️ Manual setup |

## Detailed Breakdown

### Option 1: Docker (Recommended)

**Best for:** Everyone, especially if you want GPU-accelerated COLMAP without hassle

**Pros:**
- ✅ COLMAP built with CUDA support (5-10x faster SIFT, 10-50x faster matching)
- ✅ Pre-configured environment with all dependencies
- ✅ Reproducible builds via Dockerfile
- ✅ Build-time verification ensures CUDA works
- ✅ Easy to share with team members
- ✅ No conflicts with host system

**Cons:**
- ⏱ First build takes 15-40 minutes
- 💾 Large image size (~24GB)
- 🔧 Requires Docker + NVIDIA Container Toolkit

**Setup:**
```bash
# One-time setup
docker build -t gaussian-splatting-env:latest .

# Run pipeline
docker run --gpus all --rm \
    -v ${PWD}/scenes:/home/appuser/project/scenes \
    gaussian-splatting-env:latest \
    python /home/appuser/project/scripts/run-colmap.py \
        --input_path /home/appuser/project/scenes/myscene/images \
        --output_path /home/appuser/project/scenes/myscene
```

**See:** [BUILD_INSTRUCTIONS.md](../BUILD_INSTRUCTIONS.md)

---

### Option 2: WSL2 Native

**Best for:** Users who prefer native Linux environment and don't need GPU COLMAP

**Pros:**
- ✅ Native Linux environment
- ✅ Good integration with Windows filesystem
- ✅ PyTorch GPU support works well
- ✅ Familiar Linux tools

**Cons:**
- ❌ apt COLMAP lacks CUDA support (CPU-only, 10-20x slower)
- 🔧 Manual dependency installation
- ⚠️ Less reproducible (manual steps)
- 🐛 Potential driver/CUDA version mismatches

**Setup:**
```bash
# Inside WSL2
sudo apt update
sudo apt install -y colmap  # Note: CPU-only version
python3 -m venv .venv
source .venv/bin/activate
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
```

**Warning:** This gives you CPU-only COLMAP. To get GPU COLMAP in WSL2, you'd need to build from source (complex) or use Docker inside WSL2.

**See:** [docs/WSL2.md](WSL2.md)

---

### Option 3: Windows Native

**Best for:** Users who must avoid Docker/WSL2 and are comfortable with manual builds

**Pros:**
- ✅ Native Windows performance
- ✅ Direct GPU access
- ✅ No virtualization overhead

**Cons:**
- ❌ COLMAP Windows binaries rarely have GPU support
- 🔧 Very complex manual dependency setup
- ⏱ Longest setup time
- 🐛 High chance of version conflicts
- 📝 Poor reproducibility

**Setup:**
Complex and varies by system. Generally involves:
1. Installing Visual Studio build tools
2. Installing CUDA toolkit
3. Building COLMAP from source (if GPU support needed)
4. Installing PyTorch with CUDA
5. Managing all dependencies manually

**Not recommended unless you have specific constraints.**

**See:** [docs/LOCAL_SETUP.md](LOCAL_SETUP.md)

---

## Performance Comparison (Real-World)

Based on RTX 3060 12GB, 50-image dataset:

| Setup | COLMAP Time | Notes |
|-------|-------------|-------|
| Docker (CUDA COLMAP) | **5-10 min** | GPU SIFT + GPU matching |
| WSL2 (apt COLMAP) | 30-60 min | CPU-only, all cores |
| Windows (manual CUDA build) | 5-10 min | If built correctly |
| Windows (CPU COLMAP) | 45-90 min | Slower CPU, fewer cores |

**Speedup from GPU COLMAP:** 6-10x faster overall pipeline time

---

## Migration Between Setups

### From WSL2 to Docker
```bash
# Your scenes/ data is portable
# Just mount it in Docker:
docker run --gpus all --rm \
    -v /mnt/c/Python-Dad/gaussian-splatting-colab/scenes:/home/appuser/project/scenes \
    gaussian-splatting-env:latest bash
```

### From Windows Native to Docker
```powershell
# Same - just mount your scenes directory
docker run --gpus all --rm `
    -v ${PWD}\scenes:/home/appuser/project/scenes `
    gaussian-splatting-env:latest bash
```

---

## Requirements by Setup

### All Setups Require:
- NVIDIA GPU (RTX 2000 series or newer recommended)
- NVIDIA driver >= 530 (for CUDA 12.1)
- At least 12GB disk space for scenes + outputs

### Docker-Specific:
- Docker Desktop (Windows/Mac) or Docker Engine (Linux)
- NVIDIA Container Toolkit
- 30GB free disk space (for Docker image + build cache)

### WSL2-Specific:
- Windows 10/11 with WSL2 enabled
- Ubuntu 22.04 distribution (or similar)
- CUDA toolkit installed in WSL2

### Windows Native-Specific:
- Visual Studio Build Tools 2019+
- CMake, Ninja, Git
- CUDA Toolkit 12.1 (matching your driver)
- Patience for dependency hell 😅

---

## Decision Tree

```
Do you need GPU-accelerated COLMAP?
├─ Yes
│  └─ Use Docker (builds COLMAP with CUDA)
│
└─ No (CPU COLMAP is OK, or you only need training GPU)
   ├─ Comfortable with Linux?
   │  └─ Yes → WSL2 is fine
   │  └─ No → Still use Docker (easier)
   │
   └─ Must avoid Docker/WSL2?
      └─ Windows Native (not recommended)
```

---

## Troubleshooting by Setup

### Docker
- **Build fails:** Check CMake logs for CUDA detection
- **GPU not found at runtime:** Use `--gpus all` flag
- **Slow build:** First build is slow (15-40 min), then cached

### WSL2
- **COLMAP slow:** Expected - apt version is CPU-only
- **PyTorch doesn't see GPU:** Check CUDA toolkit in WSL2
- **nvidia-smi fails:** Check Windows NVIDIA driver

### Windows Native
- **Everything broken:** Expected - use Docker instead 😉

---

## Recommended Workflow

**For development:**
1. Use Docker for COLMAP (GPU-accelerated)
2. Mount your scenes/ directory
3. Edit code on Windows, run in container

**For production:**
1. Build Docker image in CI
2. Deploy to cloud GPU (AWS, GCP, etc.)
3. Same Dockerfile works everywhere

**For experimentation:**
1. Use Docker for consistent environment
2. Iterate quickly with cached layers
3. Share Dockerfile with collaborators

---

## Cost Comparison (Time = Money)

Assuming 100 images, RTX 3060:

| Setup | COLMAP Time | Your Time Cost (1hr setup) | Total "Cost" |
|-------|-------------|---------------------------|--------------|
| Docker | 10 min | 40 min (one-time build) | 50 min |
| WSL2 | 60 min | 45 min (setup) | 105 min |
| Windows Native | 10 min (if GPU) | 3 hours (setup hell) | 3hr 10min |

**Winner:** Docker saves you 2+ hours on first run, then crushes on every subsequent run.

---

## Conclusion

**Use Docker unless you have a very specific reason not to.**

The Dockerfile in this repo gives you:
- ✅ GPU-accelerated COLMAP (6-10x faster)
- ✅ Pre-configured environment
- ✅ Reproducible builds
- ✅ Easy sharing
- ✅ Build-time verification

See [BUILD_INSTRUCTIONS.md](../BUILD_INSTRUCTIONS.md) to get started.
