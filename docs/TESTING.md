# Testing Guide - RealTerrain Studio

Complete guide for running and writing tests for RealTerrain Studio.

---

## 🎯 Testing Strategy

### Test Coverage Goals

- **Backend**: 85%+ coverage
- **UE5 Plugin**: 70%+ coverage (C++ automation tests)
- **Integration**: All critical workflows tested

### Test Pyramid

```
        /\
       /  \        E2E (10%)
      /----\       - Complete workflows
     /      \      Integration (20%)
    /--------\     - Cross-component tests
   /          \    Unit (70%)
  /____________\   - Individual functions
```

---

## 🐍 Python Tests (Backend)

### Quick Start

```bash
# Install test dependencies
cd C:\RealTerrainStudio
pip install -r tests/requirements.txt

# Run all tests
cd tests
pytest

# Run with coverage
pytest --cov=../backend --cov-report=html

# Run specific test file
pytest backend/test_exporters.py

# Run specific test
pytest backend/test_exporters.py::TestHeightmapExporter::test_export_16bit_png
```

### Running Different Test Categories

```bash
# Unit tests only
pytest backend/ -m "not integration"

# Integration tests only
pytest integration/ -m integration

# Performance tests only
pytest -m performance

# Smoke tests (quick verification)
pytest -m smoke

# Skip slow tests during development
pytest -m "not slow"
```

### Parallel Test Execution

```bash
# Run tests in parallel (faster)
pytest -n 4  # Use 4 worker processes
pytest -n auto  # Auto-detect number of CPUs
```

### Using the Test Runner Script

```bash
# Run all tests
python tests/run_tests.py

# Run only unit tests
python tests/run_tests.py --unit

# Run with coverage report
python tests/run_tests.py --coverage

# Run performance tests
python tests/run_tests.py --performance

# Parallel execution
python tests/run_tests.py --parallel 4 --verbose
```

---

## 🎮 UE5 Plugin Tests (C++)

### Running UE5 Automation Tests

#### Method 1: Via UE5 Editor

1. Open Unreal Engine 5 Editor
2. Go to **Window** → **Test Automation**
3. Navigate to **RealTerrainStudio** category
4. Select tests to run
5. Click **Start Tests**

#### Method 2: Via Command Line

```bash
# Navigate to UE5 installation
cd "C:\Program Files\Epic Games\UE_5.7\Engine\Binaries\Win64"

# Run all RealTerrain tests
UnrealEditor-Cmd.exe "C:\Users\Mikael\Documents\Unreal Projects\ProjectX\ProjectX.uproject" ^
  -ExecCmds="Automation RunTests RealTerrainStudio" ^
  -unattended -nopause -NullRHI ^
  -testexit="Automation Test Queue Empty"

# Run specific test category
UnrealEditor-Cmd.exe ProjectX.uproject ^
  -ExecCmds="Automation RunTests RealTerrainStudio.HeightmapImporter" ^
  -unattended -nopause -NullRHI ^
  -testexit="Automation Test Queue Empty"
```

### UE5 Test Categories

- **RealTerrainStudio.HeightmapImporter.*** - Heightmap import tests
- **RealTerrainStudio.SatelliteImporter.*** - Satellite texture tests
- **RealTerrainStudio.OSMSplineImporter.*** - OSM spline tests

### UE5 Test Filters

```cpp
// Product tests (run by default in shipping builds)
EAutomationTestFlags::ProductFilter

// Performance/stress tests
EAutomationTestFlags::PerfFilter

// Application context (requires game instance)
EAutomationTestFlags::ApplicationContextMask
```

---

## 🔗 Integration Tests

### Full Workflow Test

Tests the complete pipeline from data export to UE5 import:

```bash
cd tests
pytest integration/test_full_workflow.py -v
```

### What Integration Tests Cover

1. **Data Export**:
   - Heightmap PNG creation
   - Metadata JSON generation
   - Satellite texture export
   - OSM splines export

2. **Data Validation**:
   - File format correctness
   - Coordinate system consistency
   - Elevation range validity

3. **Error Recovery**:
   - Missing optional files
   - Corrupted data handling
   - Partial exports

---

## 📊 Test Coverage

### Generate Coverage Report

```bash
# HTML report
pytest --cov=backend --cov=qgis-plugin/src --cov-report=html

# Terminal report
pytest --cov=backend --cov-report=term-missing

# XML report (for CI/CD)
pytest --cov=backend --cov-report=xml
```

### View Coverage Report

```bash
# Open HTML report in browser
start htmlcov/index.html  # Windows
open htmlcov/index.html   # macOS
xdg-open htmlcov/index.html  # Linux
```

### Coverage Goals by Module

| Module | Target Coverage | Current Status |
|--------|----------------|----------------|
| Heightmap Exporter | 90% | ✅ Framework Ready |
| Satellite Exporter | 85% | ✅ Framework Ready |
| OSM Exporter | 85% | ✅ Framework Ready |
| Database | 80% | ✅ Framework Ready |
| UE5 Importer | 70% | ✅ Framework Ready |

---

## 🚀 Continuous Integration

### GitHub Actions Workflow

Tests run automatically on:
- Every push to `main` or `develop`
- Every pull request
- Nightly builds (performance tests)

### CI Stages

1. **Backend Tests**:
   - Unit tests with coverage
   - Upload to Codecov

2. **Integration Tests**:
   - Cross-component tests
   - Data format validation

3. **Code Quality**:
   - Black (formatting)
   - isort (import sorting)
   - flake8 (linting)

4. **Performance Tests** (main branch only):
   - Benchmark critical operations
   - Ensure performance targets met

### Viewing CI Results

- Check the **Actions** tab in GitHub
- Coverage reports on Codecov
- Performance trends tracked over time

---

## ✍️ Writing Tests

### Python Unit Test Example

```python
# tests/backend/test_my_feature.py
import pytest

class TestMyFeature:
    """Test my new feature."""

    def test_basic_functionality(self):
        """Test basic case."""
        result = my_function(input_data)
        assert result is not None
        assert result.status == 'success'

    def test_error_handling(self):
        """Test error case."""
        with pytest.raises(ValueError):
            my_function(invalid_data)

    @pytest.mark.performance
    def test_performance(self):
        """Test performance."""
        import time
        start = time.time()
        result = my_function(large_data)
        duration = time.time() - start
        assert duration < 1.0  # Should complete in < 1 second
```

### UE5 Automation Test Example

```cpp
// Tests/MyFeatureTest.cpp
#include "Misc/AutomationTest.h"
#include "MyFeature.h"

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
    FMyFeatureBasicTest,
    "RealTerrainStudio.MyFeature.Basic",
    EAutomationTestFlags::ApplicationContextMask | EAutomationTestFlags::ProductFilter
)

bool FMyFeatureBasicTest::RunTest(const FString& Parameters)
{
    // Arrange
    UMyFeature* Feature = NewObject<UMyFeature>();

    // Act
    bool bResult = Feature->DoSomething();

    // Assert
    TestTrue(TEXT("Feature should succeed"), bResult);
    TestNotNull(TEXT("Feature should be valid"), Feature);

    return true;
}
```

### Using Fixtures

```python
# tests/conftest.py
import pytest

@pytest.fixture
def sample_data():
    """Provide sample data for tests."""
    return {
        'width': 1024,
        'height': 1024,
        'data': np.zeros((1024, 1024), dtype=np.uint16)
    }

# tests/test_feature.py
def test_with_fixture(sample_data):
    """Test using fixture."""
    assert sample_data['width'] == 1024
```

### Mocking External Dependencies

```python
from unittest.mock import Mock, patch

def test_with_mock():
    """Test with mocked HTTP request."""
    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {'data': 'test'}

        result = fetch_data_from_api()
        assert result['data'] == 'test'
        mock_get.assert_called_once()
```

---

## 🐛 Debugging Tests

### Run Single Test with Debugging

```bash
# Python
pytest -v -s tests/backend/test_file.py::TestClass::test_method

# -v: Verbose output
# -s: Show print statements
```

### Add Debugging Breakpoints

```python
def test_something():
    # Add breakpoint
    import pdb; pdb.set_trace()

    result = my_function()
    assert result is not None
```

### View Test Output

```bash
# Capture all output
pytest -v -s --tb=long

# Show only failures
pytest --tb=short

# Show only first failure
pytest -x
```

---

## 🎯 Performance Testing

### Benchmark Tests

```python
@pytest.mark.performance
def test_export_performance(benchmark):
    """Benchmark export operation."""
    result = benchmark(export_terrain, bbox, resolution=30)
    assert result is not None
```

### Performance Targets

| Operation | Target Time | Current |
|-----------|-------------|---------|
| Heightmap Export (1024×1024) | < 2s | ✅ TBD |
| Satellite Export (2048×2048) | < 3s | ✅ TBD |
| OSM Splines Parse (1000 features) | < 1s | ✅ TBD |
| Complete Package (10km²) | < 30s | ✅ TBD |

---

## 📝 Test Markers

### Available Markers

- `@pytest.mark.unit` - Fast unit tests
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.performance` - Performance tests
- `@pytest.mark.smoke` - Quick smoke tests
- `@pytest.mark.slow` - Tests that take > 5 seconds

### Using Markers

```python
@pytest.mark.performance
@pytest.mark.slow
def test_large_terrain_export():
    """Test large terrain export (slow)."""
    pass
```

---

## 🛠️ Troubleshooting

### Tests Fail Locally But Pass in CI

- Check Python version matches CI (3.11)
- Check dependencies are up to date
- Check environment variables

### Tests Are Slow

- Use smaller test data
- Mock external dependencies
- Run in parallel: `pytest -n auto`
- Skip slow tests: `pytest -m "not slow"`

### Coverage Not Working

- Ensure source paths are correct in pytest.ini
- Run from tests directory
- Check .coveragerc configuration

---

## 📬 Contact

Questions about testing?
- Check existing tests for examples
- Review this documentation
- Contact: dev@realterrainstudio.com

---

**Test thoroughly. Ship confidently. 🚀**
