# Copilot Instructions for Gaussian Splatting Colab

## Project Architecture

This is a **Gaussian Splatting pipeline** designed for Google Colab A100 environments. The project follows a modular Python structure optimized for both local development and cloud notebook execution.

### Key Components
- **`notebooks/`**: Colab-ready notebooks with complete pipeline demonstrations
- **`scripts/`**: Automation scripts for COLMAP, training, and data processing (currently scaffolded)
- **`src/`**: Core reusable modules (to be populated as notebooks mature)
- **`main.py`**: Entry point that imports from `src/` for local execution

## Critical Workflow Patterns

### Colab-First Development
The primary workflow revolves around `notebooks/Gaussian_Splatting_Colab.ipynb`:
1. GPU detection (`!nvidia-smi`)
2. COLMAP installation and scene reconstruction
3. Image upload via `google.colab.files.upload()`
4. Pipeline execution: `run_colmap.py` → `convert_colmap.py` → `train.py`

**Convention**: All notebooks should be self-contained but extract reusable logic to `src/` as patterns emerge.

### Dependency Strategy
- **Poetry** for dev dependencies (`pyproject.toml`)
- **requirements.txt** for Colab compatibility (export via `poetry export`)
- **Colab installs**: Use `!pip install` with specific CUDA indices for PyTorch

### Directory-Specific Patterns

#### `scripts/` Directory
Scripts are **pipeline orchestrators**, not core logic holders:
```python
# Expected pattern for scripts/train.py
from src.training import GaussianTrainer
# CLI interface that delegates to src/ modules
```

#### `src/` Module Structure
Follow domain-driven organization as code moves from notebooks:
- `src/colmap/` - COLMAP integration and scene reconstruction
- `src/training/` - Gaussian Splatting training logic  
- `src/rendering/` - Output generation and visualization
- `src/core/` - Shared utilities and configurations

#### Environment Management
- Use `.env.example` for documenting required variables (API keys, paths)
- **Never commit** actual API keys or Colab-specific paths
- Support both local venv and Colab environments in the same codebase

## Code Quality Standards

### Pre-commit Pipeline
All code must pass:
```yaml
black + isort (formatting)
flake8 (linting)  
mypy (type checking)
```

Run locally: `pre-commit install && pre-commit run --all-files`

### Notebook → Code Migration
When extracting from notebooks to `src/`:
1. **Keep notebook cells small** and focused on single operations
2. **Extract classes/functions** that appear in multiple notebooks
3. **Preserve Colab compatibility** - test imports work in both environments
4. **Maintain GPU optimization** patterns from notebook context

## External Integration Points

### COLMAP Dependencies
- System-level installation required (`apt install colmap`)
- Expects specific directory structure: `scenes/{scene_name}/images/`
- Outputs to `scenes/{scene_name}/sparse/` for downstream processing

### PyTorch/CUDA Setup
- Use `--extra-index-url https://download.pytorch.org/whl/cu121` for Colab
- Verify GPU availability before heavy compute operations
- Handle both CUDA and CPU fallback in `src/` modules

## Key Files for Understanding

- **`NEXT_STEPS.md`**: Roadmap for moving notebook code into `src/`
- **`docs/01-Project_Overview_and_Best_Practices.md`**: Architectural philosophy
- **`.pre-commit-config.yaml`**: Code quality gates
- **`notebooks/Gaussian_Splatting_Colab.ipynb`**: Reference implementation workflow

## AI Assistant Guidelines

When working on this codebase:
1. **Prioritize Colab compatibility** - test notebook changes in isolated cells
2. **Extract reusable patterns** to `src/` when you see duplication across notebooks
3. **Maintain GPU awareness** - always check CUDA availability in compute-heavy operations
4. **Follow the domain structure** when creating new `src/` modules
5. **Update requirements.txt** when adding dependencies to `pyproject.toml`

The goal is evolving from notebook prototypes to production-ready modules while keeping the Colab research workflow intact.