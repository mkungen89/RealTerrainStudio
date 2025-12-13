# Error Handling Guide
## RealTerrain Studio

**Version:** 1.0.0
**Last Updated:** December 13, 2024

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Error Handling Philosophy](#error-handling-philosophy)
3. [Custom Error Types](#custom-error-types)
4. [Error Handling Utilities](#error-handling-utilities)
5. [Best Practices](#best-practices)
6. [Examples](#examples)
7. [Testing Error Handling](#testing-error-handling)

---

## 🎯 Overview

RealTerrain Studio implements comprehensive error handling to ensure:

- **User-friendly error messages** - Clear explanations, not technical jargon
- **Graceful degradation** - Continue working with partial data when possible
- **Automatic retry** - Transient network errors are retried automatically
- **Detailed logging** - Technical errors logged for debugging
- **Recovery guidance** - Users get actionable steps to fix problems

---

## 🧠 Error Handling Philosophy

### Principles

1. **Never crash** - Always catch and handle errors gracefully
2. **Inform the user** - Show clear, actionable error messages
3. **Log for debugging** - Detailed technical logs for developers
4. **Retry transient errors** - Network issues often resolve themselves
5. **Degrade gracefully** - Partial success is better than complete failure

### Error Severity Levels

**CRITICAL** - Cannot continue, user action required
- License validation failure
- GDAL not available
- Cannot create required directories

**ERROR** - Operation failed, but plugin still functional
- Network request failed after retries
- Data download failed for specific tile
- File write failed

**WARNING** - Potential issue, but operation continued
- Partial tile download failure (some succeeded)
- Cache miss (will download)
- Deprecated API usage

**INFO** - Normal operations
- License validated successfully
- Tile fetched from cache
- Export completed

---

## 🚨 Custom Error Types

### Base Error: `RTerrainError`

All custom errors inherit from this base class.

```python
class RTerrainError(Exception):
    def __init__(
        self,
        message: str,
        user_message: Optional[str] = None,
        recoverable: bool = True
    ):
        self.message = message  # Technical message (for logs)
        self.user_message = user_message  # User-friendly message (for UI)
        self.recoverable = recoverable  # Can user recover from this?
```

**Properties:**
- `message` - Technical error details (logged)
- `user_message` - User-friendly explanation (shown in UI)
- `recoverable` - Whether user can fix and try again

### Specific Error Types

#### `NetworkError`
**When to use:** Network operations fail (downloads, API calls)

**User message:** Explains network issues and suggests checking connection

```python
raise NetworkError(
    "Failed to connect to SRTM server: Connection timeout",
    user_message="Cannot connect to elevation data server. Check your internet connection."
)
```

#### `DataFetchError`
**When to use:** Data fetching/downloading fails

**User message:** Explains data source issues and suggests alternatives

```python
raise DataFetchError(
    "No SRTM tiles available for bbox",
    user_message="No elevation data available for this location. Try a different area."
)
```

#### `ValidationError`
**When to use:** Input validation fails

**User message:** Explains what's wrong with the input and how to fix it

```python
raise ValidationError(
    "Latitude must be between -90 and 90",
    field="latitude"
)
```

#### `LicenseError`
**When to use:** License validation fails

**User message:** Explains license issues and suggests solutions

```python
raise LicenseError(
    "License key expired on 2024-12-01",
    user_message="Your license has expired. Please renew at realterrainstudio.com"
)
```

#### `ExportError`
**When to use:** Export operations fail

**User message:** Explains export issues (disk space, permissions, etc.)

```python
raise ExportError(
    "Insufficient disk space: need 500MB, have 100MB",
    user_message="Not enough disk space. Free up 400MB and try again."
)
```

#### `GDALError`
**When to use:** GDAL operations fail

**User message:** Explains geospatial processing errors

```python
raise GDALError(
    "Failed to open raster file: /path/to/file.tif",
    user_message="Geospatial data file is corrupted. Try downloading again."
)
```

---

## 🛠️ Error Handling Utilities

### `@retry` Decorator

Automatically retries operations that may fail transiently.

**Parameters:**
- `max_attempts` - Maximum retry attempts (default: 3)
- `delay` - Initial delay between retries in seconds (default: 1.0)
- `backoff` - Multiplier for delay after each attempt (default: 2.0)
- `exceptions` - Tuple of exception types to catch (default: all)
- `on_retry` - Optional callback function(attempt, exception)

**Example:**

```python
@retry(
    max_attempts=3,
    delay=2.0,
    backoff=2.0,
    exceptions=(NetworkError,)
)
def download_tile(tile_id):
    """Download a tile with automatic retry on network errors."""
    response = requests.get(f"{BASE_URL}/{tile_id}")
    response.raise_for_status()
    return response.content
```

**Retry timing:**
- 1st attempt: immediate
- 2nd attempt: after 2.0s delay
- 3rd attempt: after 4.0s delay (2.0 × 2.0 backoff)

### `@handle_errors` Decorator

Catches errors and returns a default value instead of crashing.

**Parameters:**
- `default_return` - Value to return on error (default: None)
- `log_traceback` - Whether to log full traceback (default: True)
- `user_message` - Custom user message to show (default: error's message)
- `show_dialog` - Whether to show error dialog in QGIS (default: False)

**Example:**

```python
@handle_errors(default_return=[], user_message="Failed to load data")
def load_terrain_data(path):
    """Load terrain data, returning [] if it fails."""
    with open(path, 'rb') as f:
        return pickle.load(f)
```

### Validation Functions

#### `validate_bbox(bbox)`
Validates a bounding box.

```python
bbox = validate_bbox((-122.5, 37.7, -122.4, 37.8))
# Returns normalized bbox or raises ValidationError
```

**Checks:**
- Format: 4-tuple of floats
- Longitude: -180 to 180, min < max
- Latitude: -90 to 90, min < max
- Size: Not too small (<0.001°) or too large (>10°)

#### `validate_file_path(path, must_exist=False, extension=None)`
Validates a file path.

```python
path = validate_file_path("/path/to/file.tif", extension=".tif")
# Returns Path object or raises ValidationError
```

**Checks:**
- Path not empty
- Parent directory exists
- File exists (if must_exist=True)
- Extension matches (if specified)
- Write permissions (for new files)

#### `validate_resolution(resolution, allowed_resolutions=None)`
Validates resolution parameter.

```python
res = validate_resolution(30, allowed_resolutions=[10, 20, 30])
# Returns resolution or raises ValidationError
```

**Checks:**
- Is integer
- Is positive
- Is in allowed list (if specified)

### Helper Functions

#### `safe_divide(numerator, denominator, default=0.0)`
Division that never crashes on zero.

```python
result = safe_divide(10, 0, default=999)
# Returns 999 instead of crashing
```

#### `ensure_directory(path)`
Creates directory if it doesn't exist.

```python
dir_path = ensure_directory("/path/to/cache")
# Returns Path object, creates directory if needed
```

#### `handle_network_error(func, *args, **kwargs)`
Executes function and converts network errors.

```python
response = handle_network_error(
    requests.get,
    url,
    timeout=30
)
# Converts requests exceptions to NetworkError
```

#### `handle_gdal_error(func, *args, **kwargs)`
Executes function and converts GDAL errors.

```python
dataset = handle_gdal_error(
    gdal.Open,
    "/path/to/file.tif"
)
# Converts GDAL failures to GDALError
```

---

## ✅ Best Practices

### 1. Always Use Appropriate Error Types

```python
# ✅ GOOD: Specific error type
if not license_key:
    raise LicenseError("License key is empty")

# ❌ BAD: Generic exception
if not license_key:
    raise Exception("Error")
```

### 2. Provide User-Friendly Messages

```python
# ✅ GOOD: Helpful message with guidance
raise ValidationError(
    f"Bounding box too large: {area} km²",
    user_message=(
        f"Selected area is {area:.1f} km² (max: 100 km²). "
        "Try selecting a smaller area or upgrading to Pro."
    )
)

# ❌ BAD: Technical jargon
raise ValueError("bbox validation failed: area > MAX_AREA")
```

### 3. Log Technical Details

```python
# ✅ GOOD: Log details, show simple message
try:
    data = fetch_data(url)
except Exception as e:
    logger.error(f"Failed to fetch from {url}: {e}", exc_info=True)
    raise DataFetchError(
        f"Fetch failed: {e}",
        user_message="Could not download data. Check your connection."
    )

# ❌ BAD: No logging
raise DataFetchError("Failed")
```

### 4. Use Retry for Transient Errors

```python
# ✅ GOOD: Retry network operations
@retry(max_attempts=3, exceptions=(NetworkError,))
def download_file(url):
    return requests.get(url)

# ❌ BAD: Fail immediately on network blip
def download_file(url):
    return requests.get(url)
```

### 5. Degrade Gracefully

```python
# ✅ GOOD: Continue with partial success
tiles = []
for tile_id in required_tiles:
    try:
        tile = fetch_tile(tile_id)
        tiles.append(tile)
    except DataFetchError as e:
        logger.warning(f"Tile {tile_id} failed: {e}")
        continue

if not tiles:
    raise DataFetchError("All tiles failed")

# ❌ BAD: Fail completely if any tile fails
tiles = [fetch_tile(tid) for tid in required_tiles]
```

### 6. Validate Early

```python
# ✅ GOOD: Validate inputs first
def export_terrain(bbox, resolution, output_path):
    # Validate all inputs before starting work
    bbox = validate_bbox(bbox)
    resolution = validate_resolution(resolution, [10, 20, 30])
    output_path = validate_file_path(output_path, extension=".rterrain")

    # Now do the actual work
    terrain_data = fetch_terrain(bbox, resolution)
    save_terrain(terrain_data, output_path)

# ❌ BAD: Start work, discover errors mid-way
def export_terrain(bbox, resolution, output_path):
    terrain_data = fetch_terrain(bbox, resolution)  # May fail after hours
    save_terrain(terrain_data, output_path)  # Discover path invalid now
```

---

## 💡 Examples

### Example 1: Network Operation with Retry

```python
from utils.error_handling import retry, NetworkError
import requests

@retry(max_attempts=3, delay=1.0, exceptions=(NetworkError,))
def fetch_srtm_tile(tile_id):
    """Fetch SRTM tile with automatic retry."""
    url = f"https://srtm.example.com/{tile_id}.zip"

    try:
        response = requests.get(url, timeout=60)
        response.raise_for_status()
        return response.content

    except requests.RequestException as e:
        raise NetworkError(
            f"Failed to download tile {tile_id}: {e}",
            user_message="Network error downloading elevation data."
        )
```

### Example 2: Validation with User-Friendly Errors

```python
from utils.error_handling import ValidationError, validate_bbox

def export_terrain(bbox, output_path):
    """Export terrain with proper validation."""

    # Validate bounding box
    try:
        bbox = validate_bbox(bbox)
    except ValidationError as e:
        # Show error dialog to user
        show_error_dialog(e.user_message)
        return False

    # Continue with export...
    return True
```

### Example 3: Graceful Degradation

```python
from utils.error_handling import DataFetchError, handle_errors
import logging

logger = logging.getLogger(__name__)

def fetch_all_tiles(tile_ids):
    """Fetch tiles, continuing even if some fail."""
    tiles = []
    failed = []

    for tile_id in tile_ids:
        try:
            tile = fetch_single_tile(tile_id)
            tiles.append(tile)
            logger.info(f"Successfully fetched {tile_id}")

        except DataFetchError as e:
            logger.warning(f"Failed to fetch {tile_id}: {e}")
            failed.append(tile_id)
            continue

    # Check if we got enough data
    if not tiles:
        raise DataFetchError(
            f"All {len(tile_ids)} tiles failed",
            user_message="Could not download any elevation data. Check your connection."
        )

    if failed:
        logger.warning(f"Succeeded: {len(tiles)}, Failed: {len(failed)}")

    return tiles
```

### Example 4: Error Context and Reporting

```python
from utils.error_handling import create_error_report, save_error_report

def complex_operation():
    """Complex operation with error reporting."""
    try:
        # ... complex work ...
        pass

    except Exception as e:
        # Create detailed error report
        context = {
            'operation': 'complex_operation',
            'parameters': {...},
            'state': {...}
        }

        # Save error report for debugging
        report_path = "/tmp/error_report.json"
        save_error_report(e, report_path, context)

        logger.error(f"Operation failed. Error report: {report_path}")
        raise
```

---

## 🧪 Testing Error Handling

### Running Tests

```bash
cd tests
pytest test_error_handling.py -v
```

### Test Coverage

The test suite (`test_error_handling.py`) covers:

- ✅ All custom exception types
- ✅ Retry decorator with various scenarios
- ✅ Handle errors decorator
- ✅ All validation functions
- ✅ Helper utilities (safe_divide, ensure_directory, etc.)
- ✅ Realistic error scenarios
- ✅ Graceful degradation

### Writing New Error Tests

```python
def test_my_error_scenario():
    """Test specific error scenario."""

    # 1. Setup
    setup_test_data()

    # 2. Execute and expect specific error
    with pytest.raises(DataFetchError) as exc_info:
        my_function_that_should_fail()

    # 3. Verify error details
    error = exc_info.value
    assert "expected message" in error.user_message.lower()
    assert error.recoverable is True

    # 4. Verify logging
    assert "error logged" in caplog.text
```

---

## 📊 Error Handling Checklist

Before completing a feature, ensure:

- [ ] All risky operations wrapped in try-except
- [ ] Appropriate custom error types used
- [ ] User-friendly error messages provided
- [ ] Technical details logged properly
- [ ] Network operations use @retry decorator
- [ ] Inputs validated early
- [ ] Graceful degradation where possible
- [ ] Tests written for error cases
- [ ] Error dialog shown to user (if applicable)
- [ ] Recovery guidance provided in error messages

---

## 🔍 Debugging Errors

### Log Levels

```python
import logging

logger = logging.getLogger(__name__)

logger.debug("Detailed diagnostic info")  # Development only
logger.info("Normal operation")  # User-visible events
logger.warning("Potential issue")  # Degraded functionality
logger.error("Operation failed")  # Error occurred
logger.exception("Error with traceback")  # Error + stack trace
```

### Enabling Debug Logging

In QGIS Python console:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Reading Error Reports

Error reports are saved as JSON files with:
- Error type and message
- Full stack trace
- Context information
- System information
- Timestamp

```json
{
  "error_type": "NetworkError",
  "error_message": "Connection timeout",
  "user_message": "Network connection problem...",
  "traceback": "...",
  "timestamp": 1702473600.0,
  "context": {
    "url": "https://...",
    "attempt": 3
  },
  "system": {
    "platform": "win32",
    "python_version": "3.9.5"
  }
}
```

---

## 📚 Additional Resources

- **AGENT_RULES.md** - Development guidelines
- **test_error_handling.py** - Comprehensive test suite
- **utils/error_handling.py** - Error handling utilities source code

---

**Last Updated:** December 13, 2024
**Version:** 1.0.0
**For:** RealTerrain Studio
**By:** Claude Code
