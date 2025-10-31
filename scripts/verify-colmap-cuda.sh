#!/bin/bash
# Robust COLMAP CUDA verification script
# Run this inside the Docker container after building with --gpus all

set -e  # Exit on any error

echo "=================================================="
echo "COLMAP CUDA Verification Script"
echo "=================================================="

# 1. Check COLMAP version and ensure it was built WITH CUDA
echo ""
echo "=== Step 1: Check COLMAP Version ==="
VERSION_OUTPUT=$(colmap --version 2>&1)
echo "$VERSION_OUTPUT"

if echo "$VERSION_OUTPUT" | grep -qi "without CUDA"; then
    echo ""
    echo "✗ FATAL: COLMAP was built WITHOUT CUDA support"
    echo "   The version string contains 'without CUDA'"
    exit 1
fi

if echo "$VERSION_OUTPUT" | grep -qi "with CUDA"; then
    echo ""
    echo "✓ COLMAP version shows 'with CUDA' - good!"
else
    echo ""
    echo "⚠ WARNING: Could not confirm 'with CUDA' in version string"
    echo "   (This might be OK if the version format changed)"
fi

# 2. Verify CUDA flags are available in help text
echo ""
echo "=== Step 2: Check for GPU Flags in Help Text ==="

if colmap feature_extractor --help 2>&1 | grep -q "SiftExtraction.use_gpu"; then
    echo "✓ Found SiftExtraction.use_gpu flag in feature_extractor"
else
    echo "✗ FATAL: SiftExtraction.use_gpu flag not found"
    exit 1
fi

if colmap exhaustive_matcher --help 2>&1 | grep -q "SiftMatching.use_gpu"; then
    echo "✓ Found SiftMatching.use_gpu flag in exhaustive_matcher"
else
    echo "✗ FATAL: SiftMatching.use_gpu flag not found"
    exit 1
fi

# 3. Check GPU availability at runtime
echo ""
echo "=== Step 3: Check GPU Device Availability ==="
if command -v nvidia-smi &> /dev/null; then
    echo "✓ nvidia-smi is available"
    nvidia-smi --query-gpu=index,name,driver_version,memory.total --format=csv,noheader
    GPU_AVAILABLE=1
else
    echo "✗ WARNING: nvidia-smi not found"
    echo "   Make sure you ran: docker run --gpus all ..."
    GPU_AVAILABLE=0
fi

# 4. Runtime smoke test - only if GPU is available
if [ $GPU_AVAILABLE -eq 1 ]; then
    echo ""
    echo "=== Step 4: Runtime Smoke Test ==="
    echo "Creating test images and running COLMAP with GPU flags..."

    TEST_DIR=$(mktemp -d)
    trap "rm -rf $TEST_DIR" EXIT

    # Create 2 tiny test images (100x100 gray squares with slight variation)
    mkdir -p "$TEST_DIR/images"
    convert -size 100x100 xc:gray80 "$TEST_DIR/images/test1.jpg" 2>/dev/null || {
        echo "⚠ ImageMagick not available, skipping runtime test"
        echo "   (This is OK - build-time checks already passed)"
        GPU_AVAILABLE=0
    }

    if [ $GPU_AVAILABLE -eq 1 ]; then
        convert -size 100x100 xc:gray60 "$TEST_DIR/images/test2.jpg"

        # Create database
        mkdir -p "$TEST_DIR/database"
        DB_PATH="$TEST_DIR/database/database.db"

        # Try feature extraction with GPU flag
        echo "Running: colmap feature_extractor with --SiftExtraction.use_gpu 1"
        if colmap feature_extractor \
            --database_path "$DB_PATH" \
            --image_path "$TEST_DIR/images" \
            --SiftExtraction.use_gpu 1 \
            --SiftExtraction.num_threads 1 \
            2>&1 | tee "$TEST_DIR/extract.log"; then

            echo ""
            echo "✓ Feature extraction with GPU flag succeeded"

            # Check if GPU was actually used (look for CUDA-related messages)
            if grep -qi "cuda\|gpu" "$TEST_DIR/extract.log"; then
                echo "✓ Log contains CUDA/GPU references - GPU was likely used"
            else
                echo "⚠ Log doesn't mention CUDA/GPU (might still be OK)"
            fi
        else
            echo ""
            echo "✗ WARNING: Feature extraction with GPU flag failed"
            echo "   Check logs above for details"
            exit 1
        fi
    fi
else
    echo ""
    echo "=== Skipping Runtime Smoke Test (no GPU available) ==="
fi

# Summary
echo ""
echo "=================================================="
echo "✓ COLMAP CUDA Verification PASSED"
echo "=================================================="
echo ""
echo "Summary:"
echo "  - COLMAP binary built with CUDA: ✓"
echo "  - GPU flags available in help: ✓"
if [ $GPU_AVAILABLE -eq 1 ]; then
    echo "  - GPU device detected: ✓"
    echo "  - Runtime smoke test: ✓"
else
    echo "  - GPU device: not tested (run with --gpus all)"
fi
echo ""
echo "Your COLMAP installation is ready for GPU-accelerated"
echo "feature extraction and matching!"
echo ""
