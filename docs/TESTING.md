# Testing Guide

## Overview

This project uses **pytest** for comprehensive testing with 28 tests covering:
- Unit tests for core modules
- Integration tests for COLMAP and training workflows
- CLI interface tests
- Script functionality tests

## Test Coverage

### Test Suites

1. **tests/test_env.py** (2 tests)
   - Environment detection
   - PyTorch availability checking

2. **tests/test_colmap_integration.py** (5 tests)
   - COLMAP script discovery
   - Input directory creation
   - Logs directory creation
   - GPU flag handling
   - Error handling

3. **tests/test_training_integration.py** (4 tests)
   - Training script discovery
   - Iteration configuration
   - Subprocess invocation

4. **tests/test_orchestrator.py** (5 tests)
   - Scene preparation
   - Pipeline validation
   - Directory structure checks

5. **tests/test_convert.py** (3 tests)
   - Conversion wrapper validation
   - Script path handling

6. **tests/test_main_cli.py** (4 tests)
   - CLI help output
   - Environment checks
   - Error handling

7. **tests/test_scripts.py** (5 tests)
   - All script help functions
   - Script invocation

## Running Tests

### Run All Tests

```bash
pytest tests/ -v
```

### Run Specific Test Suite

```bash
# Just integration tests
pytest tests/test_colmap_integration.py -v

# Just CLI tests
pytest tests/test_main_cli.py -v
```

### Run Single Test

```bash
pytest tests/test_env.py::test_full_env_report_contains_keys -v
```

### Run with Coverage

```bash
pip install pytest-cov
pytest tests/ --cov=src --cov-report=html
```

View coverage report: `open htmlcov/index.html`

## Test Fixtures

The test suite uses several fixtures defined in `tests/conftest.py`:

### `temp_dir`
Creates a temporary directory that's automatically cleaned up after the test.

### `sample_images_dir`
Generates 5 test images (640x480) with different colors and gradients.

### `sample_scene_dir`
Creates a complete scene directory structure with test images.

### `mock_colmap_output`
Creates mock COLMAP output files (cameras.bin, images.bin, points3D.bin) for testing.

### `project_root`
Returns the project root directory path.

## Writing New Tests

### Unit Test Template

```python
# tests/test_mymodule.py
from src import mymodule

def test_my_function():
    """Test description."""
    result = mymodule.my_function()
    assert result == expected_value
```

### Integration Test Template

```python
from pathlib import Path
from unittest.mock import patch

def test_with_files(temp_dir: Path):
    """Test that uses temporary files."""
    test_file = temp_dir / "test.txt"
    test_file.write_text("content")

    # Test your function
    result = process_file(str(test_file))
    assert result is not None
```

### Mock External Commands

```python
from unittest.mock import patch, MagicMock

def test_subprocess_call():
    """Test function that calls subprocess."""
    with patch("subprocess.check_call") as mock_call:
        my_function_that_calls_subprocess()
        assert mock_call.called
```

## Pre-Commit Hooks

Pre-commit hooks automatically run tests and linters before each commit:

```bash
# Install hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

Hooks configured:
- **black**: Code formatting
- **isort**: Import sorting
- **flake8**: Linting
- **mypy**: Type checking

## Continuous Integration

Tests run automatically on:
- Every push to remote branches
- Pull request creation
- Pull request updates

### GitHub Actions

See `.github/workflows/test.yml` (if configured) for CI pipeline.

## Test Data

### Sample Images

Test fixtures generate images programmatically:
- Size: 640x480
- Format: JPEG, quality 95
- Patterns: Gray, red, green, blue, yellow with gradients

### Mock Data Locations

- Temporary files: `$TMPDIR/pytest-*`
- Test scenes: Created in fixture temp directories
- Cleaned up automatically after tests

## Debugging Failed Tests

### Verbose Output

```bash
pytest tests/ -vv
```

### Show Print Statements

```bash
pytest tests/ -s
```

### Stop on First Failure

```bash
pytest tests/ -x
```

### Run Specific Failed Test

```bash
pytest tests/test_colmap_integration.py::test_run_colmap_error_handling -vv
```

### Debug with PDB

```bash
pytest tests/ --pdb
```

## Test Performance

Current test suite performance:
- **Total tests**: 28
- **Execution time**: ~28 seconds
- **All passing**: ✅

Breakdown by suite:
| Suite | Tests | Time |
|-------|-------|------|
| env | 2 | <1s |
| colmap | 5 | ~10s |
| training | 4 | ~8s |
| orchestrator | 5 | ~5s |
| convert | 3 | <1s |
| main_cli | 4 | ~3s |
| scripts | 5 | ~2s |

## Best Practices

### 1. Test Isolation
- Each test should be independent
- Use fixtures for setup/teardown
- Don't rely on test execution order

### 2. Clear Test Names
```python
# Good
def test_run_colmap_creates_logs_directory():
    ...

# Bad
def test_colmap_1():
    ...
```

### 3. Arrange-Act-Assert Pattern
```python
def test_example():
    # Arrange: Set up test data
    input_data = create_test_data()

    # Act: Execute the function
    result = function_under_test(input_data)

    # Assert: Verify the result
    assert result == expected_output
```

### 4. Use Meaningful Assertions
```python
# Good
assert len(results) == 5, f"Expected 5 results, got {len(results)}"

# Better
assert results == expected_results, f"Results mismatch: {results}"
```

### 5. Mock External Dependencies
- Mock file I/O when possible
- Mock network calls always
- Mock subprocess calls for unit tests

## Troubleshooting

### Import Errors

If tests can't find `src` modules:
```bash
# Ensure you're in project root
cd /path/to/gaussian-splatting-colab

# Run with python path
PYTHONPATH=. pytest tests/
```

### Fixture Not Found

Make sure `conftest.py` exists in the `tests/` directory.

### Slow Tests

Use pytest-xdist for parallel execution:
```bash
pip install pytest-xdist
pytest tests/ -n auto
```

## Contributing Tests

When adding new features:

1. **Write tests first** (TDD approach)
2. **Ensure all tests pass** before committing
3. **Add docstrings** to test functions
4. **Update this guide** if adding new patterns

### Test Checklist

- [ ] Test passes locally
- [ ] Test has clear docstring
- [ ] Test uses appropriate fixtures
- [ ] Test cleans up resources
- [ ] Related tests updated if needed

---

**Questions?** Check the main [README.md](../README.md) or [CONTRIBUTING.md](../CONTRIBUTING.md).
