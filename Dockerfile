# Start from an NVIDIA CUDA base image with the development toolkit
# This image includes Ubuntu, nvcc (the CUDA compiler), and necessary libraries
# We choose 12.1.1 as it's compatible with your driver and a common target for ML projects
FROM nvidia/cuda:12.1.1-devel-ubuntu22.04

# Set environment variables to avoid interactive prompts during installation
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Etc/UTC

# Install system dependencies: git, python, venv, and build tools
# NOTE: We build COLMAP from source with CUDA support later (apt version lacks CUDA)
RUN apt-get update && apt-get install -y \
    git \
    python3.10 \
    python3.10-venv \
    python3-dev \
    python3-distutils \
    build-essential \
    cmake \
    ninja-build \
    pkg-config \
    g++ \
    gcc \
    libgl1-mesa-glx \
    libgl1-mesa-dri \
    libegl1-mesa \
    libgles2-mesa \
    mesa-utils \
    libglew-dev \
    libglfw3-dev \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Install COLMAP build dependencies
# These are required to compile COLMAP with CUDA, OpenGL, and all features
RUN apt-get update && apt-get install -y \
    libboost-program-options-dev \
    libboost-filesystem-dev \
    libboost-graph-dev \
    libboost-system-dev \
    libeigen3-dev \
    libflann-dev \
    libfreeimage-dev \
    libmetis-dev \
    libgoogle-glog-dev \
    libgtest-dev \
    libsqlite3-dev \
    libglew-dev \
    qtbase5-dev \
    libqt5opengl5-dev \
    libcgal-dev \
    libceres-dev \
    && rm -rf /var/lib/apt/lists/*

# Build COLMAP from source with CUDA support
# This is the only way to get GPU-accelerated SIFT feature extraction and matching
# We do this early in the Dockerfile so it's cached and doesn't rebuild on code changes
WORKDIR /tmp/colmap-build
RUN git clone https://github.com/colmap/colmap.git --branch 3.9.1 --depth 1 && \
    cd colmap && \
    mkdir build && \
    cd build && \
    cmake .. -GNinja \
        -DCMAKE_BUILD_TYPE=Release \
        -DCMAKE_INSTALL_PREFIX=/usr/local \
        -DWITH_CUDA=ON \
        -DCMAKE_CUDA_ARCHITECTURES="75;80;86;89;90" \
        -DGUI_ENABLED=ON \
        -DWITH_OPENGL=ON \
        -DCGAL_ENABLED=ON && \
    ninja && \
    ninja install && \
    cd / && \
    rm -rf /tmp/colmap-build

# Verify COLMAP installation and CUDA support at build time
# This robust check ensures CUDA is actually compiled in
RUN set -e && \
    echo "=== Checking COLMAP version ===" && \
    colmap --version && \
    if colmap --version 2>&1 | grep -i "without CUDA"; then \
        echo "ERROR: COLMAP was built without CUDA support" && exit 1; \
    fi && \
    echo "=== Version check passed (no 'without CUDA' found) ===" && \
    echo "=== Verifying CUDA flags are available ===" && \
    colmap feature_extractor --help | grep -i "SiftExtraction.use_gpu" && \
    colmap exhaustive_matcher --help | grep -i "SiftMatching.use_gpu" && \
    echo "=== COLMAP CUDA build verification complete ==="

# Set up a non-root user and minimal workspace
RUN useradd -m -s /bin/bash appuser
USER appuser
WORKDIR /home/appuser

# Create and activate a virtual environment (will be used for building)
RUN python3.10 -m venv .venv
ENV PATH="/home/appuser/.venv/bin:$PATH"

# Ensure pip and build helpers are available
RUN pip install --no-cache-dir --upgrade pip setuptools wheel cython pybind11 ninja

# Install PyTorch early so submodule build steps that import torch can succeed
RUN pip install --no-cache-dir torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cu121

# Clone the external gaussian-splatting repository and build its submodules first
RUN git clone https://github.com/graphdeco-inria/gaussian-splatting.git /home/appuser/gaussian-splatting
WORKDIR /home/appuser/gaussian-splatting
RUN git submodule update --init --recursive

# Set CUDA architectures to compile for (avoids GPU auto-detection during build)
# 7.5=RTX 2000, 8.0=A100, 8.6=RTX 3000, 8.9=RTX 4000, 9.0=H100
ENV TORCH_CUDA_ARCH_LIST="7.5;8.0;8.6;8.9;9.0"
ENV FORCE_CUDA="1"
ENV QT_QPA_PLATFORM="offscreen"
ENV NVIDIA_DRIVER_CAPABILITIES="compute,utility,graphics"
ENV MESA_GL_VERSION_OVERRIDE="3.3"

RUN pip install --no-build-isolation --no-cache-dir submodules/diff-gaussian-rasterization
RUN pip install --no-build-isolation --no-cache-dir submodules/simple-knn
RUN pip install --no-cache-dir plyfile tqdm opencv-python joblib pillow pillow-heif

# Now copy the project after the heavy external build (reduces build context size)
WORKDIR /home/appuser/project
COPY --chown=appuser:appuser requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cu121

# Copy the rest of the project files
COPY --chown=appuser:appuser . .

# Set a default command to show that the container is ready
CMD ["bash"]
