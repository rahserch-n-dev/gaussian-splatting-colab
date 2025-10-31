WSL2 guide for COLMAP and GPU-enabled training

This guide helps you run COLMAP and GPU-enabled training inside WSL2 on Windows with an NVIDIA GPU (e.g., RTX 3060).

> **Note:** Docker is now the recommended approach for GPU-accelerated COLMAP. See [BUILD_INSTRUCTIONS.md](../BUILD_INSTRUCTIONS.md) for a pre-configured Docker environment with CUDA-enabled COLMAP. Use this WSL2 guide only if you prefer a native Linux environment without Docker.

1) Enable WSL2

- Install WSL2 per Microsoft docs:
  - Open PowerShell as Administrator and run:

```powershell
wsl --install
```

2) Install an Ubuntu distribution (from Microsoft Store) and open it.

3) Install NVIDIA drivers for WSL (Windows host)

- Download and install the NVIDIA driver that supports CUDA for WSL from NVIDIA's site. Your driver (581.57) appears recent enough.

4) Inside WSL (Ubuntu), install CUDA toolkit and verify GPU

```bash
sudo apt update && sudo apt install -y build-essential
# follow NVIDIA/Ubuntu instructions to install CUDA toolkits; you may only need the runtime
nvidia-smi
```

5) Install COLMAP in WSL

> **Warning:** The COLMAP from `apt install colmap` is compiled **without CUDA support** and will run on CPU only (10-20x slower). For GPU acceleration, use Docker instead (see [BUILD_INSTRUCTIONS.md](../BUILD_INSTRUCTIONS.md)).

```bash
sudo apt update
sudo apt install -y colmap
colmap --version
# Will show "without CUDA" - this is expected for apt version
```

If you want GPU-accelerated COLMAP in WSL2, you'll need to build from source (complex) or use Docker.

6) Python & PyTorch inside WSL

- Create a Python venv inside WSL and install the Linux PyTorch wheel for your CUDA version (see https://pytorch.org/ for exact commands):

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu13x
python -c "import torch; print(torch.cuda.is_available())"
```

7) Run pipeline

- Sync your project files into WSL (clone or use a shared filesystem like \"/mnt/c/...") and run:

```bash
python scripts/run_local.py --scene myscene --run
```

Notes
- For performance, run training inside WSL so GPU is directly available; COLMAP works well in WSL and avoids Windows-specific binary issues.
- If you prefer to run everything on Windows, installing CUDA-enabled PyTorch on the Windows venv (what you did earlier) also works; COLMAP may still be easier in WSL.
