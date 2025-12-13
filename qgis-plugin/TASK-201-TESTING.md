## TASK-201: SRTM Data Fetcher - Testing Guide

## ✅ Task Status: READY FOR TESTING

The SRTM data fetcher has been implemented with full caching, progress callbacks, and error handling.

---

## 📋 What Was Created

### Core Files:

1. **`src/data_sources/srtm.py`** - Complete SRTM data fetcher
   - `SRTMFetcher` class with full functionality
   - `fetch_srtm_elevation()` convenience function
   - Automatic tile identification and downloading
   - Intelligent caching system
   - Progress callback support
   - Multi-tile merging
   - No-data value handling
   - GDAL-based processing

2. **`test_srtm.py`** - Test suite
   - Multiple test locations (San Francisco, Everest, Grand Canyon)
   - Cache functionality test
   - Progress reporting
   - Error handling verification

---

## 🌍 SRTM Data Details

**What is SRTM?**
- Shuttle Radar Topography Mission
- Global elevation data
- Free and publicly available
- 30m resolution (SRTM 1 Arc-Second)
- 90m resolution (SRTM 3 Arc-Second)

**Coverage:**
- Latitude: 60°N to 56°S
- Covers ~80% of Earth's land surface
- Tiles are 5° x 5°

**Data Source:**
- CGIAR-CSI SRTM server
- Tiles downloaded as ZIP files containing GeoTIFF

---

## 🧪 Testing Instructions

### Prerequisites

**GDAL Required:**
GDAL is included with QGIS, so these tests should work in the QGIS Python environment.

**Check GDAL availability:**
```python
# In QGIS Python Console
from osgeo import gdal
print(f"GDAL version: {gdal.__version__}")
```

### Method 1: Run Test Suite (Recommended)

**In QGIS Python Console:**

1. Open QGIS
2. Go to **Plugins → Python Console**
3. Run:

```python
import sys
sys.path.insert(0, r'C:\RealTerrainStudio\qgis-plugin\src')

# Import test module
exec(open(r'C:\RealTerrainStudio\qgis-plugin\test_srtm.py').read())
```

**Expected Output:**
```
============================================================
SRTM Data Fetcher Test Suite
============================================================

✅ GDAL version: 3.x.x

============================================================
Test: San Francisco Bay Area
============================================================

Bounding Box: (-122.5, 37.7, -122.4, 37.8)
  [  0%] Identifying required tiles...
  [ 10%] Need to fetch 1 tile(s)
  [ 10%] Downloading tile 1/1: srtm_11_04
  [ 80%] Merging tiles...
  [100%] Processing complete

Results:
  Shape: (xxx, xxx)
  Min elevation: 0.0 m
  Max elevation: 300.0 m
  Mean elevation: 50.0 m

✅ Test passed!

...

Test Summary:
  San Francisco        ✅ PASSED
  Cache                ✅ PASSED
  Mount Everest        ✅ PASSED
  Grand Canyon         ✅ PASSED

Total: 4/4 tests passed

🎉 All tests passed!
```

### Method 2: Manual Testing

**Test 1: Basic Fetch**

```python
import sys
sys.path.insert(0, r'C:\RealTerrainStudio\qgis-plugin\src')

from data_sources.srtm import fetch_srtm_elevation
import numpy as np

# San Francisco area
bbox = (-122.5, 37.7, -122.4, 37.8)

def progress(msg, pct):
    print(f"[{pct:3d}%] {msg}")

elevation = fetch_srtm_elevation(bbox, resolution=30, progress_callback=progress)

print(f"Shape: {elevation.shape}")
print(f"Min: {np.nanmin(elevation):.1f}m")
print(f"Max: {np.nanmax(elevation):.1f}m")
```

**Test 2: Cache Verification**

```python
from data_sources.srtm import SRTMFetcher

fetcher = SRTMFetcher()

# First fetch (downloads)
bbox = (-122.5, 37.7, -122.4, 37.8)
elev1 = fetcher.fetch_elevation(bbox)

# Check cache size
cache_size = fetcher.get_cache_size()
print(f"Cache size: {cache_size / 1024 / 1024:.2f} MB")

# Second fetch (from cache, should be instant)
elev2 = fetcher.fetch_elevation(bbox)

print(f"Data matches: {np.array_equal(elev1, elev2, equal_nan=True)}")
```

**Test 3: Different Locations**

```python
# Mount Everest (should have very high elevation)
everest_bbox = (86.9, 27.9, 87.0, 28.0)
everest_elev = fetch_srtm_elevation(everest_bbox)
print(f"Everest max: {np.nanmax(everest_elev):.1f}m (should be >8000m)")

# Death Valley (should have very low elevation)
death_valley_bbox = (-117.0, 36.2, -116.8, 36.4)
death_valley_elev = fetch_srtm_elevation(death_valley_bbox)
print(f"Death Valley min: {np.nanmin(death_valley_elev):.1f}m (should be <0m)")

# Alps (high elevation)
alps_bbox = (7.6, 45.8, 7.8, 46.0)
alps_elev = fetch_srtm_elevation(alps_bbox)
print(f"Alps max: {np.nanmax(alps_elev):.1f}m (should be >4000m)")
```

**Test 4: Error Handling**

```python
# Invalid bounding box
try:
    bad_bbox = (200, 37, 210, 38)  # Invalid longitude
    fetch_srtm_elevation(bad_bbox)
except ValueError as e:
    print(f"✅ Correctly caught error: {e}")

# Invalid resolution
try:
    bbox = (-122.5, 37.7, -122.4, 37.8)
    fetch_srtm_elevation(bbox, resolution=15)  # Not supported
except ValueError as e:
    print(f"✅ Correctly caught error: {e}")
```

---

## ✅ Acceptance Criteria Verification

- [ ] **Can download SRTM data for any global location** - Test with multiple locations
- [ ] **Handles multi-tile areas** - Test bbox spanning multiple 5° tiles
- [ ] **Caches data to avoid re-downloads** - Second fetch is instant
- [ ] **Progress callback for UI** - Callback receives updates
- [ ] **Error handling for no internet/server down** - Graceful error messages

---

## 📂 Cache Location

**Default Cache Directory:**
```
Windows: C:\Users\<username>\AppData\Local\Temp\realterrain_srtm_cache\
Mac: /tmp/realterrain_srtm_cache/
Linux: /tmp/realterrain_srtm_cache/
```

**Cache Structure:**
```
realterrain_srtm_cache/
├── srtm_11_04.tif    (SRTM tile)
├── srtm_12_04.tif
├── srtm_11_05.tif
└── merged.vrt        (temporary virtual raster)
```

**Clear Cache:**
```python
from data_sources.srtm import SRTMFetcher

fetcher = SRTMFetcher()
fetcher.clear_cache()
print("Cache cleared")
```

---

## 🔍 Test Scenarios

### Scenario 1: Small Area (Single Tile)

**Location:** San Francisco
**Bbox:** (-122.5, 37.7, -122.4, 37.8)
**Expected:**
- Single tile download
- ~0.1° x 0.1° area
- Elevation 0-300m
- Fast download (<30 seconds)

### Scenario 2: Large Area (Multiple Tiles)

**Location:** California Central Valley
**Bbox:** (-122.0, 36.0, -119.0, 39.0)
**Expected:**
- Multiple tiles (4-6 tiles)
- Automatic tile merging
- Elevation 0-2000m
- Longer download (1-2 minutes)

### Scenario 3: High Elevation

**Location:** Himalayas
**Bbox:** (86.8, 27.8, 87.2, 28.2)
**Expected:**
- Max elevation >8000m
- Some snow/glacier areas may have no-data

### Scenario 4: Below Sea Level

**Location:** Dead Sea
**Bbox:** (35.4, 31.4, 35.6, 31.6)
**Expected:**
- Min elevation < -400m (Dead Sea is lowest point on Earth)

### Scenario 5: Ocean Area (No Data)

**Location:** Pacific Ocean
**Bbox:** (-160.0, 20.0, -159.0, 21.0)
**Expected:**
- Most/all pixels are no-data (NaN)
- SRTM only covers land

### Scenario 6: Cache Performance

**Test:**
1. Fetch area (first time)
2. Note download time
3. Fetch same area again
4. Second fetch should be <1 second

---

## 🐛 Troubleshooting

### Error: "GDAL is required"

**Cause:** GDAL not available in Python environment

**Solution:**
- Use QGIS Python Console (GDAL included)
- Or install GDAL: `pip install gdal`
- Or use OSGeo4W Shell on Windows

### Error: "Failed to download SRTM tile"

**Cause:** Network issue or server down

**Solution:**
- Check internet connection
- Try again later (server may be busy)
- Check URL in browser: https://srtm.csi.cgiar.org/

### Error: "Failed to open tile"

**Cause:** Corrupted download or cache

**Solution:**
```python
from data_sources.srtm import SRTMFetcher
fetcher = SRTMFetcher()
fetcher.clear_cache()
# Try again
```

### Slow Downloads

**Cause:** Large tiles (~25MB each)

**Solution:**
- Normal for first download
- Use cache for subsequent fetches
- Use smaller bounding boxes for testing

### All NaN Values

**Cause:** Area is over ocean or outside SRTM coverage

**Solution:**
- SRTM only covers 60°N to 56°S
- Only covers land areas
- Check bbox is correct

---

## 📊 Performance Expectations

### Download Times (30 Mbps connection):

- **Single tile:** 20-40 seconds
- **2-4 tiles:** 1-2 minutes
- **5+ tiles:** 2-5 minutes

### Processing Times:

- **Single tile read:** <1 second
- **Multi-tile merge:** 1-3 seconds
- **Cache lookup:** <0.1 seconds

### Cache Sizes:

- **Single tile:** ~25 MB
- **10 tiles:** ~250 MB
- **Typical session:** 100-500 MB

---

## 📝 Data Quality Notes

**SRTM Characteristics:**
- ✅ Global coverage (80% of land)
- ✅ Free and open
- ✅ Consistent resolution
- ⚠️ Voids in mountainous areas (filled in newer versions)
- ⚠️ Some areas have lower quality
- ⚠️ Vertical accuracy ±16m

**Best For:**
- General terrain modeling
- Game development
- Visualization
- Regional analysis

**Not Ideal For:**
- High-precision surveying
- Urban detail
- Recent terrain changes

---

## 🎯 Next Steps

Once SRTM fetcher is verified:

1. **TASK-202:** Create Elevation Data Processor
   - Resampling
   - Format conversion
   - No-data filling

2. **TASK-203:** Implement Heightmap Export
   - .rterrain format
   - UE5 compatibility
   - Metadata packaging

3. **Integration:** Connect to main dialog
   - Export button triggers SRTM fetch
   - Progress bar updates
   - Error handling in UI

---

## 💡 Usage in Plugin

**Future Integration:**

```python
# In export handler
from data_sources.srtm import fetch_srtm_elevation

def export_terrain(config):
    bbox = (
        config['area']['min_lon'],
        config['area']['min_lat'],
        config['area']['max_lon'],
        config['area']['max_lat']
    )

    # Fetch elevation with progress callback
    elevation = fetch_srtm_elevation(
        bbox,
        resolution=config['elevation']['resolution'],
        progress_callback=lambda msg, pct: update_progress_bar(pct, msg)
    )

    # Process and export...
```

---

**Need Help?** Check QGIS Python Console for detailed error messages and stack traces.
