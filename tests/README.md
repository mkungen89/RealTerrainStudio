# 🧪 Tests - RealTerrain Studio

Automated testing for RealTerrain Studio to ensure reliability and quality.

---

## 📁 Test Structure

```
tests/
├── qgis/                    ← QGIS Plugin tests
│   ├── test_srtm.py
│   ├── test_exporters.py
│   ├── test_licensing.py
│   └── conftest.py
│
├── ue5/                     ← UE5 Plugin tests
│   ├── TerrainImporterTest.cpp
│   ├── MaterialApplicatorTest.cpp
│   └── TestHelpers.h
│
├── integration/             ← End-to-end tests
│   ├── test_full_workflow.py
│   ├── test_qgis_to_ue5.py
│   └── fixtures/
│
└── README.md               ← This file
```

---

## 🎯 Testing Strategy

### Test Pyramid

```
        /\
       /  \        E2E Tests (Few, Slow, High-level)
      /----\
     /      \      Integration Tests (Some, Medium, Cross-component)
    /--------\
   /          \    Unit Tests (Many, Fast, Low-level)
  /____________\
```

### Unit Tests (70%)
- Test individual functions
- Fast execution
- Mock external dependencies
- High code coverage goal: 80%+

### Integration Tests (20%)
- Test component interactions
- Test with real data sources
- Verify file formats
- Database operations

### End-to-End Tests (10%)
- Test complete workflows
- QGIS export → UE5 import
- License validation flow
- Payment flow

---

## 🐍 QGIS Plugin Tests (Python)

### Setup

```bash
cd qgis-plugin

# Install test dependencies
pip install pytest pytest-cov pytest-mock

# Run tests
pytest tests/

# Run with coverage
pytest --cov=src/realterrain tests/

# Run specific test file
pytest tests/test_srtm.py

# Run specific test
pytest tests/test_srtm.py::test_fetch_elevation_basic
```

### Writing Tests

```python
# tests/test_srtm.py
import pytest
from src.data_sources.srtm import SRTMFetcher

def test_fetch_elevation_basic():
    """Test basic SRTM elevation data fetching"""
    fetcher = SRTMFetcher()
    bbox = (-122.5, 37.7, -122.4, 37.8)  # San Francisco

    data = fetcher.fetch(bbox, resolution=30)

    assert data is not None
    assert data.shape[0] > 0
    assert data.shape[1] > 0
    assert data.dtype == 'int16'  # SRTM is 16-bit signed integer

def test_fetch_elevation_invalid_bbox():
    """Test error handling for invalid bbox"""
    fetcher = SRTMFetcher()
    bbox = (200, 200, 300, 300)  # Invalid coordinates

    with pytest.raises(ValueError):
        fetcher.fetch(bbox, resolution=30)

@pytest.fixture
def mock_srtm_response(mocker):
    """Mock HTTP response for SRTM data"""
    mock = mocker.patch('requests.get')
    mock.return_value.status_code = 200
    mock.return_value.content = b'fake_srtm_data'
    return mock

def test_fetch_with_mock(mock_srtm_response):
    """Test SRTM fetching with mocked HTTP response"""
    fetcher = SRTMFetcher()
    bbox = (-122.5, 37.7, -122.4, 37.8)

    data = fetcher.fetch(bbox, resolution=30)

    # Verify HTTP request was made
    assert mock_srtm_response.called
```

### Test Coverage Goals

- **Core functionality:** 90%+
- **Data fetchers:** 85%+
- **Exporters:** 85%+
- **Utils:** 80%+
- **UI:** 60%+ (harder to test)

---

## 🎮 UE5 Plugin Tests (C++)

### Setup

UE5 uses its own testing framework: Automation Testing

### Writing Tests

```cpp
// Tests/TerrainImporterTest.cpp

#include "Misc/AutomationTest.h"
#include "TerrainImporter.h"

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
    FTerrainImporterBasicTest,
    "RealTerrain.TerrainImporter.Basic",
    EAutomationTestFlags::ApplicationContextMask | EAutomationTestFlags::ProductFilter
)

bool FTerrainImporterBasicTest::RunTest(const FString& Parameters)
{
    // Create importer
    URealTerrainImporter* Importer = NewObject<URealTerrainImporter>();
    TestNotNull(TEXT("Importer created"), Importer);

    // Test basic import
    FString TestFile = TEXT("TestData/sample.rterrain");
    bool bSuccess = Importer->ImportFromFile(TestFile);
    TestTrue(TEXT("Import succeeded"), bSuccess);

    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
    FTerrainImporterInvalidFileTest,
    "RealTerrain.TerrainImporter.InvalidFile",
    EAutomationTestFlags::ApplicationContextMask | EAutomationTestFlags::ProductFilter
)

bool FTerrainImporterInvalidFileTest::RunTest(const FString& Parameters)
{
    URealTerrainImporter* Importer = NewObject<URealTerrainImporter>();

    // Test with invalid file
    FString TestFile = TEXT("NonExistent/file.rterrain");
    bool bSuccess = Importer->ImportFromFile(TestFile);
    TestFalse(TEXT("Import failed as expected"), bSuccess);

    return true;
}
```

### Running UE5 Tests

1. Open UE5 Editor
2. Go to: **Window** → **Test Automation**
3. Select tests to run
4. Click **Start Tests**

Or via command line:
```bash
UnrealEditor.exe YourProject.uproject -ExecCmds="Automation RunTests RealTerrain" -unattended -nopause -testexit="Automation Test Queue Empty"
```

---

## 🔗 Integration Tests

### Full Workflow Test

```python
# tests/integration/test_full_workflow.py
import pytest
import subprocess
from pathlib import Path

def test_qgis_export_to_ue5_import():
    """
    Test complete workflow:
    1. Export from QGIS
    2. Import to UE5
    3. Verify result
    """
    # Step 1: Export from QGIS
    output_file = Path("test_output/test_terrain.rterrain")
    bbox = (-122.5, 37.7, -122.4, 37.8)  # Small area for fast test

    # Run QGIS export (headless)
    result = subprocess.run([
        "qgis_process",
        "run",
        "realterrain:export",
        f"--bbox={bbox}",
        f"--output={output_file}"
    ], capture_output=True)

    assert result.returncode == 0
    assert output_file.exists()
    assert output_file.stat().st_size > 0

    # Step 2: Verify package structure
    import zipfile
    with zipfile.ZipFile(output_file, 'r') as z:
        files = z.namelist()
        assert 'heightmap.png' in files
        assert 'metadata.json' in files
        assert 'satellite.jpg' in files

    # Step 3: Import to UE5 (via commandlet)
    # This would require UE5 commandlet setup
    # Skipped in basic CI, run in full integration suite
```

---

## 🤖 Continuous Integration (CI)

### GitHub Actions

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test-qgis:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      - run: pip install -r qgis-plugin/requirements.txt
      - run: pytest qgis-plugin/tests/

  test-ue5:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v3
      - name: Build UE5 Plugin
        run: |
          # UE5 build commands
      - name: Run Tests
        run: |
          # UE5 test commands

  test-integration:
    runs-on: ubuntu-latest
    needs: [test-qgis, test-ue5]
    steps:
      - uses: actions/checkout@v3
      - run: pytest tests/integration/
```

---

## 📊 Test Reports

### Coverage Reports

```bash
# Generate HTML coverage report
pytest --cov=src --cov-report=html

# Open report
open htmlcov/index.html
```

### Performance Tests

```python
import pytest
import time

@pytest.mark.performance
def test_export_performance():
    """Ensure export completes within time limit"""
    start = time.time()

    # Run export
    result = export_terrain(bbox, resolution=30)

    duration = time.time() - start

    # Should complete in under 60 seconds
    assert duration < 60
```

---

## 🎯 Testing Best Practices

### DO ✅
- Write tests before fixing bugs
- Test edge cases
- Use meaningful test names
- Keep tests independent
- Mock external dependencies
- Test error cases
- Run tests before committing

### DON'T ❌
- Skip tests
- Test implementation details
- Share state between tests
- Ignore failing tests
- Test third-party code
- Write tests without assertions
- Commit broken tests

---

## 🆘 Troubleshooting Tests

### Tests fail locally but pass in CI
- Check Python/Node version matches CI
- Check dependencies are installed
- Check environment variables

### Tests are slow
- Use mocks for external calls
- Use smaller test data
- Run tests in parallel
- Skip slow tests in dev: `pytest -m "not slow"`

### Tests are flaky
- Check for race conditions
- Check for shared state
- Add waits for async operations
- Use deterministic test data

---

## 📬 Contact

Questions about testing?
- **Email:** dev@realterrainstudio.com
- **Discord:** #testing channel

---

**Test everything. Trust nothing. Ship with confidence.**
