# RealTerrain Studio - Developer Guide

**Version:** 1.0.0
**Last Updated:** December 13, 2024

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Getting Started](#getting-started)
3. [Project Structure](#project-structure)
4. [Development Setup](#development-setup)
5. [Coding Standards](#coding-standards)
6. [Testing](#testing)
7. [Contributing](#contributing)
8. [Architecture](#architecture)
9. [Adding New Features](#adding-new-features)
10. [Release Process](#release-process)

---

## 🎯 Overview

Welcome to the RealTerrain Studio developer documentation! This guide will help you contribute to the project.

### Project Goals

- **Accessibility:** Make real-world terrain creation easy for everyone
- **Quality:** Provide high-quality, accurate geographic data
- **Performance:** Fast exports even for large areas
- **Reliability:** Robust error handling and recovery
- **Extensibility:** Easy to add new data sources and features

### Tech Stack

**QGIS Plugin:**
- **Language:** Python 3.9+
- **Framework:** QGIS 3.28+ API
- **Key Libraries:**
  - `numpy` - Array processing
  - `GDAL` - Geospatial data
  - `Pillow` - Image processing
  - `requests` - HTTP requests
  - `PyQt5` - UI (via QGIS)

**UE5 Plugin:**
- **Language:** C++20
- **Engine:** Unreal Engine 5.3+
- **Key APIs:**
  - Landscape API
  - Spline Components
  - Procedural Mesh Component

**Backend Services:**
- **Language:** Python 3.11 (FastAPI)
- **Database:** PostgreSQL + PostGIS
- **Cache:** Redis
- **Storage:** S3-compatible

---

## 🚀 Getting Started

### Fork & Clone

```bash
# Fork the repository on GitHub
# Then clone your fork

git clone https://github.com/YOUR_USERNAME/realterrain-studio.git
cd realterrain-studio
```

### Repository Structure

```
realterrain-studio/
├── qgis-plugin/          # QGIS plugin source
│   ├── src/
│   │   ├── realterrain/  # Main plugin code
│   │   ├── data_sources/ # Data fetchers
│   │   ├── utils/        # Utilities
│   │   └── ui/           # UI components
│   ├── tests/            # Unit tests
│   └── metadata.txt      # QGIS plugin metadata
│
├── ue5-plugin/           # UE5 plugin source
│   ├── Source/
│   │   └── RealTerrainStudio/
│   │       ├── Public/
│   │       └── Private/
│   └── Resources/
│
├── backend/              # Backend services
│   ├── api/              # FastAPI application
│   ├── models/           # Database models
│   └── services/         # Business logic
│
├── docs/                 # Documentation
├── tests/                # Integration tests
└── scripts/              # Build scripts
```

---

## 🛠️ Development Setup

### Prerequisites

1. **QGIS 3.28+** installed
2. **Python 3.9+** (comes with QGIS)
3. **Git** for version control
4. **IDE:** VS Code, PyCharm, or similar

### Setting Up Development Environment

#### 1. Create Development Profile in QGIS

```bash
# Windows
C:\Users\YourName\AppData\Roaming\QGIS\QGIS3\profiles\dev\

# macOS
~/Library/Application Support/QGIS/QGIS3/profiles/dev/

# Linux
~/.local/share/QGIS/QGIS3/profiles/dev/
```

Launch QGIS with dev profile:
```bash
qgis --profiles-path /path/to/profiles --profile dev
```

#### 2. Link Plugin for Development

**Option A: Symlink (Recommended)**

Windows (run as Admin):
```cmd
mklink /D "C:\Users\YourName\AppData\Roaming\QGIS\QGIS3\profiles\dev\python\plugins\realterrain_studio" "C:\dev\realterrain-studio\qgis-plugin\src"
```

macOS/Linux:
```bash
ln -s ~/dev/realterrain-studio/qgis-plugin/src ~/Library/Application\ Support/QGIS/QGIS3/profiles/dev/python/plugins/realterrain_studio
```

**Option B: Plugin Reloader**

1. Install Plugin Reloader in QGIS
2. `Plugins` → `Plugin Reloader` → `Configure`
3. Select `RealTerrain Studio`
4. Use F5 to reload plugin during development

#### 3. Install Development Dependencies

```bash
cd qgis-plugin

# Install dev dependencies
pip install -r requirements-dev.txt

# Includes:
# - pytest (testing)
# - pytest-cov (coverage)
# - pytest-qt (Qt testing)
# - black (code formatting)
# - flake8 (linting)
# - mypy (type checking)
```

#### 4. Setup Pre-commit Hooks

```bash
# Install pre-commit
pip install pre-commit

# Setup hooks
pre-commit install

# Test hooks
pre-commit run --all-files
```

---

## 📝 Coding Standards

### Python Style Guide

We follow **PEP 8** with some modifications:

**Line Length:**
- Maximum 100 characters (not 79)

**Imports:**
```python
# Standard library
import os
import sys
from pathlib import Path

# Third-party
import numpy as np
import requests
from qgis.core import QgsProject

# Local
from realterrain.utils import validate_bbox
from realterrain.data_sources.srtm import SRTMFetcher
```

**Docstrings:**

Use Google-style docstrings:

```python
def fetch_elevation(
    bbox: Tuple[float, float, float, float],
    resolution: int = 30
) -> np.ndarray:
    """
    Fetch elevation data for bounding box.

    Args:
        bbox: Bounding box (min_lon, min_lat, max_lon, max_lat)
        resolution: Resolution in meters (10, 20, 30, or 90)

    Returns:
        numpy.ndarray: Elevation data (height, width) in meters

    Raises:
        ValidationError: If bbox invalid
        DataFetchError: If data cannot be fetched

    Example:
        >>> elevation = fetch_elevation((-122.5, 37.7, -122.4, 37.8), 30)
        >>> print(elevation.shape)
        (128, 128)

    Notes:
        - Data is cached automatically
        - Uses SRTM tiles
        - Gaps are filled using interpolation
    """
```

**Type Hints:**

Always use type hints:

```python
from typing import Tuple, Dict, List, Optional

def process_data(
    data: np.ndarray,
    bbox: Tuple[float, float, float, float],
    options: Optional[Dict[str, Any]] = None
) -> List[str]:
    """Process data and return results."""
    if options is None:
        options = {}

    # ...
    return results
```

### Code Formatting

**Use Black:**

```bash
# Format all code
black qgis-plugin/src/

# Check formatting
black --check qgis-plugin/src/
```

**Configuration (.black):**
```toml
[tool.black]
line-length = 100
target-version = ['py39']
```

### Linting

**Use Flake8:**

```bash
# Lint code
flake8 qgis-plugin/src/

# With detailed output
flake8 --show-source --statistics qgis-plugin/src/
```

**Configuration (.flake8):**
```ini
[flake8]
max-line-length = 100
exclude = __pycache__,.git,build,dist
ignore = E203,W503
```

### Type Checking

**Use MyPy:**

```bash
# Type check
mypy qgis-plugin/src/

# Strict mode
mypy --strict qgis-plugin/src/
```

---

## 🧪 Testing

### Running Tests

```bash
cd tests

# Run all tests
pytest

# Run with coverage
pytest --cov=realterrain_studio

# Run specific test file
pytest test_srtm.py

# Run specific test
pytest test_srtm.py::TestSRTMFetcher::test_fetch_elevation

# Verbose output
pytest -v

# Show print statements
pytest -s
```

### Writing Tests

**Test Structure:**

```python
import pytest
from realterrain_studio.data_sources.srtm import SRTMFetcher


class TestSRTMFetcher:
    """Tests for SRTM elevation fetcher."""

    @pytest.fixture
    def fetcher(self):
        """Create fetcher instance."""
        return SRTMFetcher()

    @pytest.fixture
    def valid_bbox(self):
        """Valid bounding box for testing."""
        return (-122.5, 37.7, -122.4, 37.8)

    def test_fetch_elevation_success(self, fetcher, valid_bbox):
        """Test successful elevation fetch."""
        elevation = fetcher.fetch_elevation(valid_bbox, resolution=30)

        assert elevation is not None
        assert elevation.shape[0] > 0
        assert elevation.shape[1] > 0
        assert elevation.min() >= -500  # Death Valley
        assert elevation.max() <= 9000  # Mount Everest

    def test_fetch_elevation_invalid_bbox(self, fetcher):
        """Test fetch with invalid bbox raises error."""
        invalid_bbox = (200, 0, 210, 10)  # Invalid longitude

        with pytest.raises(ValidationError, match="longitude"):
            fetcher.fetch_elevation(invalid_bbox)

    def test_fetch_elevation_caching(self, fetcher, valid_bbox):
        """Test elevation data is cached."""
        # First fetch
        elevation1 = fetcher.fetch_elevation(valid_bbox)

        # Second fetch (should use cache)
        import time
        start = time.time()
        elevation2 = fetcher.fetch_elevation(valid_bbox)
        duration = time.time() - start

        # Should be much faster (< 1 second)
        assert duration < 1.0
        assert np.array_equal(elevation1, elevation2)
```

**Mocking External Services:**

```python
import pytest
from unittest.mock import Mock, patch

@patch('requests.get')
def test_download_tile_network_error(mock_get, fetcher):
    """Test network error handling."""
    # Mock network failure
    mock_get.side_effect = requests.ConnectionError("Connection refused")

    with pytest.raises(NetworkError):
        fetcher._download_tile("N37W123")
```

**Testing UI Components (Qt):**

```python
import pytest
from pytestqt.qtbot import QtBot
from realterrain.ui.main_panel import RealTerrainPanel


def test_panel_creation(qtbot):
    """Test panel can be created."""
    panel = RealTerrainPanel()
    qtbot.addWidget(panel)

    assert panel is not None
    assert panel.isVisible()

def test_draw_bbox_button(qtbot):
    """Test draw bounding box button."""
    panel = RealTerrainPanel()
    qtbot.addWidget(panel)

    # Click button
    qtbot.mouseClick(panel.draw_bbox_button, Qt.LeftButton)

    # Check tool is activated
    assert panel.bbox_tool.isActive()
```

### Test Coverage

**Goal:** >80% code coverage

```bash
# Generate coverage report
pytest --cov=realterrain_studio --cov-report=html

# Open report
# Windows
start htmlcov/index.html

# macOS
open htmlcov/index.html

# Linux
xdg-open htmlcov/index.html
```

---

## 🤝 Contributing

### Contribution Workflow

1. **Create Issue**
   - Describe the feature or bug
   - Get feedback from maintainers

2. **Create Branch**
   ```bash
   git checkout -b feature/my-new-feature
   # or
   git checkout -b fix/issue-123
   ```

3. **Make Changes**
   - Write code
   - Write tests
   - Update documentation

4. **Run Tests**
   ```bash
   pytest
   black --check .
   flake8 .
   mypy .
   ```

5. **Commit Changes**
   ```bash
   git add .
   git commit -m "Add feature: description

   - Detailed change 1
   - Detailed change 2

   Closes #123"
   ```

6. **Push & Create PR**
   ```bash
   git push origin feature/my-new-feature
   ```
   - Create pull request on GitHub
   - Fill out PR template
   - Link related issues

7. **Code Review**
   - Address reviewer comments
   - Update PR as needed

8. **Merge**
   - Once approved, maintainer will merge
   - Delete branch after merge

### Commit Message Guidelines

**Format:**
```
<type>: <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Code style (formatting, no logic change)
- `refactor`: Code refactoring
- `test`: Adding/updating tests
- `chore`: Maintenance tasks

**Examples:**

```
feat: Add support for ASTER elevation data

- Implement ASTERFetcher class
- Add tests for ASTER fetcher
- Update documentation

Closes #45
```

```
fix: Handle network timeout in OSM fetcher

- Increase timeout to 180 seconds
- Add retry logic
- Improve error messages

Fixes #67
```

### Pull Request Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests pass
- [ ] Added new tests
- [ ] Manually tested in QGIS

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex code
- [ ] Documentation updated
- [ ] No new warnings
- [ ] Tests added/updated
- [ ] All tests pass

## Screenshots (if applicable)
Add screenshots here

## Related Issues
Closes #123
```

---

## 🏗️ Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────┐
│           QGIS Plugin (UI)              │
│  ┌──────────────────────────────────┐   │
│  │   Main Panel (Qt Widget)         │   │
│  │  - Draw bbox                     │   │
│  │  - Configure sources             │   │
│  │  - Start export                  │   │
│  └──────────────────────────────────┘   │
└─────────────────┬───────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│      RealTerrainExporter (Core)         │
│  ┌──────────────────────────────────┐   │
│  │  Orchestrates data fetching      │   │
│  │  and export process              │   │
│  └──────────────────────────────────┘   │
└─────────────────┬───────────────────────┘
                  │
        ┌─────────┼─────────┐
        │         │         │
        ▼         ▼         ▼
    ┌─────┐   ┌─────┐   ┌─────┐
    │SRTM │   │Sent │   │ OSM │
    │     │   │-2   │   │     │
    └─────┘   └─────┘   └─────┘
        │         │         │
        └─────────┼─────────┘
                  │
                  ▼
        ┌─────────────────┐
        │ Export Formats  │
        │  - .rterrain    │
        │  - Separate     │
        │  - FBX          │
        └─────────────────┘
```

### Module Responsibilities

**realterrain/core/**
- `exporter.py` - Main export orchestration
- `config.py` - Configuration management
- `license.py` - License validation

**realterrain/data_sources/**
- `srtm.py` - SRTM elevation fetching
- `sentinel2_fetcher.py` - Satellite imagery
- `osm_fetcher.py` - OSM data fetching
- `base.py` - Base classes for data sources

**realterrain/processing/**
- `elevation.py` - Elevation processing
- `imagery.py` - Image processing
- `materials.py` - Material classification
- `roads.py` - Road spline generation

**realterrain/export/**
- `formats.py` - Export format handlers
- `rterrain.py` - .rterrain format
- `separate_files.py` - Separate files export
- `fbx.py` - FBX export

**realterrain/utils/**
- `error_handling.py` - Error handling utilities
- `geometry.py` - Geometric calculations
- `cache.py` - Caching system
- `logging.py` - Logging configuration

**realterrain/ui/**
- `main_panel.py` - Main UI panel
- `bbox_tool.py` - Bounding box drawing tool
- `settings_dialog.py` - Settings dialog
- `progress_dialog.py` - Progress dialog

### Data Flow

```
1. User Input (UI)
   └─> Bounding box + Configuration

2. Validation
   └─> validate_bbox(), validate_config()

3. Preview (optional)
   └─> Calculate download size, duration

4. Data Fetching (parallel)
   ├─> SRTM elevation (if enabled)
   ├─> Sentinel-2 imagery (if enabled)
   └─> OSM data (if enabled)

5. Processing
   ├─> Merge elevation tiles
   ├─> Mosaic satellite images
   ├─> Parse OSM features
   └─> Classify materials (if enabled)

6. Export
   ├─> Generate heightmap
   ├─> Save textures
   ├─> Export vector data
   └─> Write metadata

7. Result
   └─> Return file paths + stats
```

---

## 🆕 Adding New Features

### Adding a New Data Source

**Example: Adding ASTER elevation data**

1. **Create Data Source Class**

File: `qgis-plugin/src/data_sources/aster.py`

```python
from typing import Tuple, Optional, Callable
import numpy as np
from .base import ElevationDataSource

class ASTERFetcher(ElevationDataSource):
    """Fetch ASTER GDEM elevation data."""

    BASE_URL = "https://aster.example.com/api/v1"

    def __init__(self, cache_dir: Optional[str] = None):
        super().__init__(cache_dir)

    def fetch_elevation(
        self,
        bbox: Tuple[float, float, float, float],
        resolution: int = 30,
        progress_callback: Optional[Callable] = None
    ) -> np.ndarray:
        """Fetch ASTER elevation data."""
        # Implementation here
        pass

    def get_required_tiles(self, bbox):
        """Get required ASTER tiles."""
        pass
```

2. **Write Tests**

File: `tests/test_aster.py`

```python
import pytest
from realterrain_studio.data_sources.aster import ASTERFetcher

class TestASTERFetcher:
    def test_fetch_elevation(self):
        fetcher = ASTERFetcher()
        bbox = (-122.5, 37.7, -122.4, 37.8)
        elevation = fetcher.fetch_elevation(bbox, resolution=30)

        assert elevation is not None
        assert elevation.shape[0] > 0
```

3. **Add to Configuration**

File: `qgis-plugin/src/realterrain/config.py`

```python
ELEVATION_SOURCES = {
    'srtm': SRTMFetcher,
    'aster': ASTERFetcher,  # Add new source
}
```

4. **Update UI**

File: `qgis-plugin/src/ui/main_panel.py`

```python
self.elevation_source_combo.addItems(['SRTM', 'ASTER'])
```

5. **Document**

Update:
- `docs/USER_GUIDE.md` - User-facing documentation
- `docs/API_DOCUMENTATION.md` - API documentation
- `CHANGELOG.md` - Add to changelog

### Adding a New Export Format

**Example: Adding GeoTIFF export**

1. **Create Format Handler**

File: `qgis-plugin/src/realterrain/export/geotiff.py`

```python
from osgeo import gdal
import numpy as np

class GeoTIFFFormat:
    """Export as GeoTIFF."""

    @staticmethod
    def export(
        elevation: np.ndarray,
        bbox: Tuple[float, float, float, float],
        output_path: str
    ) -> str:
        """Export elevation as GeoTIFF."""
        # Implementation
        driver = gdal.GetDriverByName('GTiff')
        # ...
        return output_path
```

2. **Register Format**

File: `qgis-plugin/src/realterrain/export/formats.py`

```python
EXPORT_FORMATS = {
    'rterrain': RTerrainFormat,
    'separate': SeparateFilesFormat,
    'geotiff': GeoTIFFFormat,  # Add new format
}
```

3. **Add Tests**

File: `tests/test_export_geotiff.py`

```python
def test_geotiff_export():
    elevation = np.random.rand(512, 512).astype(np.float32)
    bbox = (-122.5, 37.7, -122.4, 37.8)

    path = GeoTIFFFormat.export(elevation, bbox, '/tmp/test.tif')

    assert Path(path).exists()
```

---

## 🚀 Release Process

### Version Numbering

We use **Semantic Versioning**:

- **Major:** Breaking changes (e.g., 1.0.0 → 2.0.0)
- **Minor:** New features, backwards compatible (e.g., 1.0.0 → 1.1.0)
- **Patch:** Bug fixes (e.g., 1.0.0 → 1.0.1)

### Release Checklist

**1. Pre-Release:**

- [ ] All tests pass: `pytest`
- [ ] Code linted: `flake8 .`
- [ ] Code formatted: `black --check .`
- [ ] Type checked: `mypy .`
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
- [ ] Version bumped in:
  - `qgis-plugin/metadata.txt`
  - `qgis-plugin/src/__init__.py`
  - `ue5-plugin/RealTerrainStudio.uplugin`

**2. Build:**

```bash
# Build QGIS plugin
cd scripts
python build_plugin.py --version 1.0.1

# Build UE5 plugin
cd ue5-plugin
ue5 -run=BuildPlugin -plugin=RealTerrainStudio.uplugin
```

**3. Test Release:**

- [ ] Install on clean QGIS
- [ ] Test basic export workflow
- [ ] Test UE5 import
- [ ] Verify license activation
- [ ] Check error handling

**4. Tag Release:**

```bash
git tag -a v1.0.1 -m "Release version 1.0.1"
git push origin v1.0.1
```

**5. Create GitHub Release:**

- Go to GitHub → Releases → New Release
- Tag: v1.0.1
- Title: "RealTerrain Studio v1.0.1"
- Description: Copy from CHANGELOG.md
- Attach build artifacts:
  - `realterrain_studio_v1.0.1.zip` (QGIS plugin)
  - `RealTerrainStudio_UE5_v1.0.1.zip` (UE5 plugin)

**6. Publish:**

- [ ] Upload to QGIS Plugin Repository
- [ ] Update website
- [ ] Announce on Discord/Twitter
- [ ] Send email to subscribers (Pro users)

**7. Post-Release:**

- [ ] Monitor for bug reports
- [ ] Update documentation website
- [ ] Bump version to next dev version (e.g., 1.0.2-dev)

---

## 📚 Additional Resources

### Documentation

- [AGENT_RULES.md](../AGENT_RULES.md) - Agent development rules
- [ERROR_HANDLING.md](ERROR_HANDLING.md) - Error handling guide
- [API_DOCUMENTATION.md](API_DOCUMENTATION.md) - API reference

### External Resources

- [QGIS Plugin Development](https://docs.qgis.org/latest/en/docs/pyqgis_developer_cookbook/)
- [GDAL Python API](https://gdal.org/python/)
- [Unreal Engine C++ API](https://docs.unrealengine.com/5.3/en-US/API/)
- [Python Type Hints](https://docs.python.org/3/library/typing.html)

### Community

- **Discord:** https://discord.gg/realterrainstudio
- **Forum:** https://forum.realterrainstudio.com
- **GitHub:** https://github.com/realterrainstudio

---

## 🤝 Code of Conduct

We are committed to providing a welcoming and inclusive environment.

**Our Standards:**

- ✅ Be respectful and considerate
- ✅ Welcome newcomers
- ✅ Focus on what is best for the community
- ✅ Show empathy towards others

**Unacceptable Behavior:**

- ❌ Harassment or discrimination
- ❌ Trolling or insulting comments
- ❌ Public or private harassment
- ❌ Publishing others' private information

**Reporting:**

If you experience or witness unacceptable behavior, report to:
- conduct@realterrainstudio.com

All reports will be reviewed and investigated.

---

## 💡 Tips for Contributors

### Quick Wins

Looking for easy first contributions?

- Fix typos in documentation
- Add more examples to docs
- Write tests for uncovered code
- Improve error messages
- Add type hints to functions

### Performance Tips

- Profile code: `python -m cProfile script.py`
- Use `np.ndarray` for large data (not lists)
- Cache expensive operations
- Use generators for large iterations
- Parallelize independent operations

### Debugging Tips

**QGIS Python Console:**

```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Reload plugin during development
from importlib import reload
import realterrain_studio
reload(realterrain_studio)
```

**VS Code Launch Configuration:**

`.vscode/launch.json`:
```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "QGIS Plugin",
      "type": "python",
      "request": "attach",
      "port": 5678,
      "host": "localhost"
    }
  ]
}
```

In plugin code:
```python
import debugpy
debugpy.listen(5678)
print("Waiting for debugger...")
debugpy.wait_for_client()
```

---

**Thank you for contributing to RealTerrain Studio!** 🎉

Your contributions make this project better for everyone.

---

**Last Updated:** December 13, 2024
**Version:** 1.0.0
**For:** RealTerrain Studio
**By:** RealTerrain Studio Team
