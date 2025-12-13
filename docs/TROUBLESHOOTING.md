# RealTerrain Studio - Troubleshooting Guide

**Version:** 1.0.0
**Last Updated:** December 13, 2024

---

## 📋 Table of Contents

1. [Quick Diagnostics](#quick-diagnostics)
2. [Common Issues & Solutions](#common-issues--solutions)
3. [Data Fetching Problems](#data-fetching-problems)
4. [Export Problems](#export-problems)
5. [UE5 Import Problems](#ue5-import-problems)
6. [Performance Issues](#performance-issues)
7. [License & Activation Issues](#license--activation-issues)
8. [Error Messages Explained](#error-messages-explained)
9. [Advanced Troubleshooting](#advanced-troubleshooting)
10. [Getting Help](#getting-help)

---

## 🔍 Quick Diagnostics

Before diving into specific issues, run these quick checks:

### System Check

**In QGIS Python Console** (`Plugins` → `Python Console`):

```python
import sys
import platform

print("=" * 50)
print("SYSTEM DIAGNOSTICS")
print("=" * 50)

# System info
print(f"OS: {platform.system()} {platform.release()}")
print(f"Python: {sys.version}")

# Check QGIS
try:
    from qgis.core import Qgis
    print(f"QGIS: {Qgis.QGIS_VERSION}")
except Exception as e:
    print(f"QGIS: ERROR - {e}")

# Check required packages
packages = ['numpy', 'requests', 'PIL', 'osgeo']
for pkg in packages:
    try:
        __import__(pkg)
        print(f"{pkg}: ✓ Installed")
    except ImportError:
        print(f"{pkg}: ✗ MISSING")

# Check RealTerrain Studio
try:
    from realterrain_studio import __version__
    print(f"RealTerrain Studio: {__version__}")
except Exception as e:
    print(f"RealTerrain Studio: ERROR - {e}")

print("=" * 50)
```

**Expected Output:**
```
==================================================
SYSTEM DIAGNOSTICS
==================================================
OS: Windows 10
Python: 3.9.5
QGIS: 3.34.1
numpy: ✓ Installed
requests: ✓ Installed
PIL: ✓ Installed
osgeo: ✓ Installed
RealTerrain Studio: 1.0.0
==================================================
```

If you see ✗ MISSING or ERROR, that's your issue. See [Installation Guide](INSTALLATION.md).

### Connection Check

Test internet connectivity to data sources:

```python
import requests

sources = {
    'SRTM': 'https://srtm.csi.cgiar.org',
    'Sentinel Hub': 'https://services.sentinel-hub.com',
    'Overpass API': 'https://overpass-api.de/api/status',
    'License Server': 'https://api.realterrainstudio.com/health'
}

print("CONNECTION CHECK")
print("=" * 50)

for name, url in sources.items():
    try:
        response = requests.get(url, timeout=5)
        status = "✓ OK" if response.status_code == 200 else f"⚠ {response.status_code}"
        print(f"{name}: {status}")
    except requests.Timeout:
        print(f"{name}: ✗ TIMEOUT")
    except requests.RequestException as e:
        print(f"{name}: ✗ ERROR - {e}")

print("=" * 50)
```

---

## 🛠️ Common Issues & Solutions

### Issue: Plugin Not Appearing in QGIS

**Symptoms:**
- No RealTerrain Studio icon in toolbar
- No menu item under `Plugins`

**Solutions:**

1. **Check Plugin is Installed:**
   - `Plugins` → `Manage and Install Plugins` → `Installed`
   - Look for "RealTerrain Studio"
   - If unchecked, check the box
   - Restart QGIS

2. **Check for Errors:**
   - `View` → `Panels` → `Log Messages`
   - Look for red errors related to RealTerrain Studio
   - Common error: `ModuleNotFoundError: No module named 'numpy'`
     - Fix: Install missing package (see Quick Diagnostics above)

3. **Reinstall Plugin:**
   - Uninstall: `Plugins` → `Manage and Install Plugins` → `Installed` → `Uninstall Plugin`
   - Reinstall from repository or ZIP
   - Restart QGIS

4. **Check QGIS Version:**
   - `Help` → `About`
   - Requires QGIS 3.28+
   - If older, update QGIS

---

### Issue: "No Internet Connection" Error

**Symptoms:**
- Error message: "Network error downloading elevation data"
- Download progress stuck at 0%

**Solutions:**

1. **Verify Internet Connection:**
   - Open web browser, visit https://google.com
   - If no connection, check your network

2. **Check Firewall:**
   - Windows: `Settings` → `Privacy & Security` → `Windows Security` → `Firewall & network protection`
   - Allow QGIS through firewall
   - Or temporarily disable firewall for testing

3. **Check Proxy Settings:**
   - If behind corporate proxy:
   - `Settings` → `Options` → `Network`
   - Configure proxy settings
   - Example:
     ```
     Proxy host: proxy.company.com
     Port: 8080
     User: your_username
     Password: your_password
     ```

4. **Try Different Data Source:**
   - If SRTM fails, try ASTER
   - Data sources have different servers

5. **DNS Issues:**
   - Try using Google DNS:
   - Windows: `Network Settings` → `Change adapter options` → `Properties` → `TCP/IPv4`
   - DNS: 8.8.8.8, 8.8.4.4

---

### Issue: Bounding Box Won't Draw

**Symptoms:**
- Click "Draw Bounding Box" but nothing happens
- Can't select area on map

**Solutions:**

1. **Check Map Layer:**
   - Need a base map layer loaded
   - Add one: `Browser Panel` → `XYZ Tiles` → `OpenStreetMap`
   - Drag onto map

2. **Check CRS (Coordinate Reference System):**
   - Bottom right of QGIS, should show: `EPSG:4326` or `EPSG:3857`
   - If different, click it and set to `EPSG:4326`

3. **Tool Not Active:**
   - Click the "Draw Bounding Box" button again
   - Cursor should change to crosshair
   - Click and drag on map

4. **QGIS Tools Conflicting:**
   - Disable other tools
   - Try: `View` → `Toolbars` → Uncheck all except RealTerrain Studio

---

### Issue: Export Fails Immediately

**Symptoms:**
- Click "Export" but fails in seconds
- Error: "Export failed"

**Solutions:**

1. **Check Bounding Box:**
   - Coordinates must be valid:
     - Longitude: -180 to 180
     - Latitude: -90 to 90
   - Min must be less than Max
   - Run diagnostic:
   ```python
   bbox = (-122.5, 37.7, -122.4, 37.8)  # Your bbox

   min_lon, min_lat, max_lon, max_lat = bbox

   assert -180 <= min_lon <= 180, "Invalid min_lon"
   assert -180 <= max_lon <= 180, "Invalid max_lon"
   assert -90 <= min_lat <= 90, "Invalid min_lat"
   assert -90 <= max_lat <= 90, "Invalid max_lat"
   assert min_lon < max_lon, "Min longitude > Max"
   assert min_lat < max_lat, "Min latitude > Max"

   print("✓ Bounding box is valid!")
   ```

2. **Check Disk Space:**
   - Exports can be large (100MB - 1GB+)
   - Ensure enough free space on target drive
   - Windows: `This PC` → Check drive
   - macOS: `About This Mac` → `Storage`
   - Linux: `df -h`

3. **Check Write Permissions:**
   - Try exporting to different location
   - Use: `C:\Terrains\` (Windows) or `~/Terrains/` (macOS/Linux)
   - Avoid system folders like `C:\Program Files\`

4. **Check Log for Specific Error:**
   - `View` → `Panels` → `Log Messages`
   - Look for the red error message
   - Copy error and search in this guide

---

### Issue: Export Takes Forever

**Symptoms:**
- Export starts but progress bar doesn't move
- Stuck at 0% or specific percentage

**Solutions:**

1. **Check Internet Speed:**
   - Run speed test: https://fast.com
   - Slow connection = slow downloads
   - Typical export requires 10-500MB download

2. **Reduce Area Size:**
   - Large areas take longer
   - 10km² at 10m resolution can take 10-20 minutes
   - Try smaller test area first

3. **Reduce Resolution:**
   - 10m resolution = 10x more data than 30m
   - Use 30m for testing
   - Use 10m for final export

4. **Check Server Status:**
   - Data sources can be slow or down
   - Try again later
   - Or try different data source

5. **Not Stuck, Just Slow:**
   - Check QGIS bottom status bar for activity
   - Check Task Manager / Activity Monitor for network usage
   - If downloading, it's working (just slow)

---

## 📡 Data Fetching Problems

### No Elevation Data Available

**Symptoms:**
- Error: "No elevation data available for this location"
- Heightmap is blank/black

**Solutions:**

1. **Check Location:**
   - Is the area over ocean?
     - SRTM only covers land
     - Try coastal area with land
   - Is the area in polar region?
     - SRTM covers 60°N to 56°S only
     - Use ASTER (covers up to 83°)

2. **Try Different Data Source:**
   - SRTM missing? Try ASTER
   - Settings: `Data Sources` → `Elevation` → `Source: ASTER GDEM`

3. **Check Data Coverage:**
   - SRTM Coverage Map: https://srtm.csi.cgiar.org/srtmdata/
   - Green = available, Red = not available

---

### Satellite Imagery is Cloudy

**Symptoms:**
- Exported satellite image has white clouds
- Can't see terrain clearly

**Solutions:**

1. **Use Date Range Filter:**
   - Click "Advanced" in Satellite Imagery section
   - Set date range:
     - Start: 6 months ago
     - End: Today
   - System will find clearest image in that range

2. **Try Different Season:**
   - Some locations are clearer in certain seasons
   - Example: Europe is clearer in summer

3. **Enable Cloud Filtering** (Pro):
   - Automatically selects least cloudy images
   - Settings: `Satellite Imagery` → `Cloud Filtering: On`

4. **Use Different Satellite:**
   - Sentinel-2 cloudy? Try Landsat 8
   - Different satellites, different cloud patterns

---

### OSM Data Incomplete

**Symptoms:**
- Missing roads or buildings
- Rural area has no data

**Solutions:**

1. **Check OSM Coverage:**
   - Visit: https://www.openstreetmap.org
   - Navigate to your area
   - If roads/buildings not on OSM, they won't export

2. **Contribute to OSM:**
   - You can add missing data!
   - Tutorial: https://learnosm.org
   - Changes appear in RealTerrain Studio within 24 hours

3. **Use Alternative:**
   - For buildings: Try satellite imagery analysis (Pro feature)
   - For roads: Manually add in UE5 using Landscape Splines

4. **Verify Filters:**
   - Check you have "Roads" and "Buildings" enabled
   - Check filter settings haven't excluded your features

---

### Download Keeps Failing

**Symptoms:**
- Error: "Failed to download tile after 3 attempts"
- Some tiles download, others fail

**Solutions:**

1. **Automatic Retry:**
   - RealTerrain Studio retries 3 times automatically
   - Wait for it to complete

2. **Check Specific Error:**
   - Error 429: "Rate limit exceeded"
     - You're downloading too fast
     - Wait 1 minute, try again
     - Reduce area size

   - Error 503: "Service unavailable"
     - Server is down
     - Try again later (after 10-15 minutes)

   - Error timeout:
     - Slow connection
     - Increase timeout in settings
     - Or use smaller area

3. **Clear Cache:**
   - Settings → `Clear Cache`
   - Try export again
   - Corrupted cache can cause issues

4. **VPN Issues:**
   - Some data sources block VPNs
   - Try disabling VPN temporarily

---

## 💾 Export Problems

### Exported Files Are Corrupt

**Symptoms:**
- Can't open heightmap PNG
- JSON files have errors
- UE5 won't import

**Solutions:**

1. **Check Disk Space During Export:**
   - Export might have failed due to full disk
   - Partial files = corrupted
   - Free up space, re-export

2. **Antivirus Interference:**
   - Some antivirus software blocks file creation
   - Temporarily disable, try again
   - Add QGIS to whitelist

3. **Re-export:**
   - Delete all files from export folder
   - Export again
   - Don't interrupt export process

4. **Verify Files:**
   ```python
   import json
   from pathlib import Path
   from PIL import Image

   export_dir = Path(r"C:\Terrains\MyTerrain")

   # Check heightmap
   try:
       img = Image.open(export_dir / "terrain_heightmap.png")
       print(f"✓ Heightmap OK: {img.size}")
   except Exception as e:
       print(f"✗ Heightmap ERROR: {e}")

   # Check metadata
   try:
       with open(export_dir / "terrain_metadata.json") as f:
           meta = json.load(f)
       print(f"✓ Metadata OK: {len(meta)} keys")
   except Exception as e:
       print(f"✗ Metadata ERROR: {e}")
   ```

---

### Wrong Scale/Size

**Symptoms:**
- Terrain is too small/large in UE5
- Mountains are flat or too tall

**Solutions:**

1. **Check Height Scale:**
   - In export settings: `Height Scale`
   - Default: 1.0 (realistic)
   - Increase for more dramatic terrain
   - Decrease to flatten

2. **Check Metadata:**
   - Open `terrain_metadata.json`
   - Verify `scale_factor` is correct
   - If wrong, you can manually edit

3. **UE5 Import Scale:**
   - In UE5 import dialog:
   - `Z Scale` parameter
   - Adjust to correct height

4. **Re-export with Correct Settings:**
   - Check "Preview" before export
   - Verify dimensions are correct

---

### Missing Satellite Texture

**Symptoms:**
- Heightmap exports but no satellite image
- `terrain_satellite.jpg` missing

**Solutions:**

1. **Check Option Was Enabled:**
   - Did you check "Satellite Imagery" before export?
   - Re-export with it enabled

2. **Check Satellite Download:**
   - Look in log for satellite download messages
   - If failed, see "Data Fetching Problems" above

3. **Check File Size:**
   - Navigate to export folder
   - If `terrain_satellite.jpg` is 0 KB → failed
   - Re-export

4. **Fallback:**
   - Export satellite separately:
   - Disable all except "Satellite Imagery"
   - Export to same folder
   - Will create `terrain_satellite.jpg`

---

## 🎮 UE5 Import Problems

### Can't Find Import Option

**Symptoms:**
- No "Import Terrain" in Tools menu
- UE5 plugin doesn't appear

**Solutions:**

1. **Check Plugin is Installed:**
   - `Edit` → `Plugins`
   - Search: "RealTerrain Studio"
   - If not found, install plugin (see [Installation Guide](INSTALLATION.md))

2. **Enable Plugin:**
   - If found but unchecked, check the box
   - Click "Restart Now"

3. **Check UE5 Version:**
   - Requires UE5.3+
   - `Help` → `About Unreal Engine`
   - If older, update UE5

---

### Import Fails with Error

**Symptoms:**
- Import starts but fails
- Error in UE5 log

**Common Errors:**

**Error:** "Failed to load heightmap"

**Solution:**
- Heightmap file corrupted or missing
- Check file exists: `terrain_heightmap.png`
- Re-export from QGIS

---

**Error:** "Heightmap dimensions not power of 2"

**Solution:**
- UE5 Landscape requires power-of-2 dimensions
- Common sizes: 1024x1024, 2048x2048, 4096x4096
- In export settings, enable "Force power-of-2 output"
- Re-export

---

**Error:** "Out of memory"

**Solution:**
- Terrain too large for available RAM
- Use smaller terrain
- Or reduce heightmap resolution
- Or export in tiles

---

**Error:** "Material assignment failed"

**Solution:**
- Missing UE5 material assets
- Re-install UE5 plugin (includes materials)
- Or disable auto-material assignment
- Manually assign materials after import

---

### Terrain Looks Wrong

**Symptoms:**
- Terrain imported but looks incorrect
- Wrong location, scale, or appearance

**Issues:**

**1. Terrain is Flat:**
- Check Z Scale in import settings
- Try: 2.0 or 5.0
- Re-import

**2. Terrain is Upside Down:**
- Flip heightmap:
- Export settings: "Flip vertical: On"
- Re-export and import

**3. Terrain is in Wrong Location:**
- Check import location coordinates
- Should match real-world location
- Adjust in import dialog

**4. Textures Stretched:**
- UV scale issue
- Adjust "Texture Scale" in import settings
- Or adjust in UE5 material

**5. Materials Look Wrong:**
- Check "Material Classification" was enabled in export
- Re-import with materials
- Or manually paint in UE5

---

### Roads Don't Appear

**Symptoms:**
- Terrain imports but no roads
- Roads in export but not in UE5

**Solutions:**

1. **Check Roads Were Exported:**
   - Look for `terrain_roads.json` in export folder
   - If missing, re-export with "Roads" enabled

2. **Check Import Settings:**
   - "Import Roads" option must be checked
   - Re-import with roads enabled

3. **Roads are There But Hard to See:**
   - Zoom in close
   - Roads are Landscape Splines (thin lines)
   - Select: `Window` → `World Outliner` → Search "Road"

4. **Manual Road Import:**
   - `Tools` → `RealTerrain Studio` → `Import Roads Only`
   - Select `terrain_roads.json`
   - Roads will be added to existing landscape

---

## ⚡ Performance Issues

### QGIS Freezes During Export

**Symptoms:**
- QGIS becomes unresponsive
- Can't cancel export

**Solutions:**

1. **Wait:**
   - Large exports can take 5-20 minutes
   - QGIS may appear frozen but is working
   - Check Task Manager / Activity Monitor for disk/network activity

2. **Reduce Export Size:**
   - Don't export huge areas (>50km²)
   - Use lower resolution
   - Export in smaller chunks

3. **Increase QGIS Memory:**
   - `Settings` → `Options` → `System`
   - `Override system locale → Yes`
   - Increase cache size

4. **Close Other Applications:**
   - Free up RAM for QGIS
   - Disable browser, video players, etc.

---

### Export Uses Too Much Disk Space

**Symptoms:**
- Export creates multi-GB files
- Running out of disk space

**Solutions:**

1. **Check What's Large:**
   - Satellite imagery: 10m resolution for 10km² = ~500MB
   - Heightmap: ~50MB
   - Vector data: ~10MB

2. **Reduce Satellite Quality:**
   - Use 20m instead of 10m (4x smaller)
   - Use JPEG compression (lossy but smaller)
   - Settings: `Satellite Imagery` → `Quality: Medium`

3. **Export Only What You Need:**
   - Testing? Just export elevation (no satellite)
   - Prototyping? Use lower resolution
   - Final export? Then use high quality

4. **Use SSD:**
   - Exports to HDD are slower
   - Use fast SSD for export folder

5. **Clean Up Old Exports:**
   - Delete test exports you don't need
   - Clear cache: Settings → `Clear Cache`

---

### UE5 Import is Slow

**Symptoms:**
- Import takes 10+ minutes
- UE5 becomes unresponsive

**Solutions:**

1. **This is Normal for Large Terrains:**
   - 10km² at 10m = 5-10 minutes import time
   - Progress bar shows ETA

2. **Speed Up Import:**
   - Use lower LOD settings
   - Disable "Generate Collisions" during import (add later)
   - Import without materials first, add materials later

3. **Use Tiling:**
   - Instead of one huge terrain, export as multiple tiles
   - Import tiles separately
   - Faster and better for performance

---

## 🔐 License & Activation Issues

### License Key Not Accepted

**Symptoms:**
- Error: "Invalid license key"
- License won't activate

**Solutions:**

1. **Verify License Key:**
   - Format: `RTSP-XXXX-XXXX-XXXX-XXXX`
   - Copy-paste carefully (no extra spaces)
   - Check email for correct key

2. **Check License Type:**
   - Free trial keys expire after 30 days
   - Check expiration date in email

3. **Check Internet Connection:**
   - License validation requires internet
   - Temporary network issue? Try again

4. **Contact Support:**
   - support@realterrainstudio.com
   - Include:
     - License key (last 4 characters only)
     - Error message
     - Purchase receipt

---

### Monthly Limit Exceeded

**Symptoms:**
- Error: "Monthly export limit exceeded"
- Free tier: 100km²/month

**Solutions:**

1. **Check Usage:**
   - Click "License Info"
   - Shows: "Used: 95km² / 100km²"

2. **Wait for Reset:**
   - Limit resets on first day of month
   - Or upgrade to Pro (unlimited)

3. **Delete Old Exports:**
   - Deleting exported files doesn't free up quota
   - Quota is based on downloads, not disk usage

4. **Upgrade to Pro:**
   - Unlimited exports
   - https://realterrainstudio.com/pricing

---

### License Deactivation Issues

**Symptoms:**
- Can't deactivate license
- Want to move license to another machine

**Solutions:**

1. **Normal Deactivation:**
   - In QGIS: License section → "Deactivate"
   - Confirm deactivation
   - Can then activate on different computer

2. **Remote Deactivation:**
   - Lost access to original computer?
   - Log in to: https://realterrainstudio.com/account
   - View active licenses
   - Click "Deactivate" for old computer

3. **License Limits:**
   - Pro license: 3 simultaneous activations
   - If at limit, must deactivate one first

---

## 🚨 Error Messages Explained

### Network Errors

**"Connection timeout"**
- **Meaning:** Server didn't respond in time
- **Fix:** Try again, check internet connection

**"Connection refused"**
- **Meaning:** Server rejected connection
- **Fix:** Server may be down, try later or different source

**"Rate limit exceeded (429)"**
- **Meaning:** Too many requests too fast
- **Fix:** Wait 60 seconds, try again

**"Server error (500, 502, 503)"**
- **Meaning:** Server is having issues
- **Fix:** Try again in 10-15 minutes

---

### Validation Errors

**"Bounding box too large"**
- **Meaning:** Selected area exceeds limits
- **Free tier:** Max 10km × 10km per export
- **Fix:** Select smaller area or upgrade to Pro

**"Bounding box too small"**
- **Meaning:** Area is < 0.01km²
- **Fix:** Draw larger bounding box

**"Invalid coordinates"**
- **Meaning:** Coordinates out of range
- **Fix:** Check longitude (-180 to 180), latitude (-90 to 90)

---

### GDAL Errors

**"GDAL not available"**
- **Meaning:** GDAL library not found
- **Fix:** Reinstall QGIS (includes GDAL)

**"Failed to create raster"**
- **Meaning:** Can't write output file
- **Fix:** Check disk space, permissions

**"Geotransform error"**
- **Meaning:** Coordinate conversion failed
- **Fix:** Check CRS settings, try different projection

---

### License Errors

**"License expired"**
- **Meaning:** Subscription ended
- **Fix:** Renew at: https://realterrainstudio.com/renew

**"License limit reached"**
- **Meaning:** Too many activations
- **Fix:** Deactivate unused computers

**"Invalid license server response"**
- **Meaning:** Can't contact license server
- **Fix:** Check firewall, internet connection

---

## 🔬 Advanced Troubleshooting

### Enable Debug Logging

Get detailed logs for troubleshooting:

**In QGIS Python Console:**

```python
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

# Now perform export - you'll see detailed logs
```

Logs appear in: `View` → `Panels` → `Log Messages`

Save logs to file:

```python
import logging
from pathlib import Path

log_file = Path.home() / "realterrain_debug.log"

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

print(f"Logging to: {log_file}")
```

---

### Clear All Caches

Sometimes cached data causes issues:

```python
from pathlib import Path
import shutil

# Clear QGIS cache
qgis_cache = Path.home() / ".qgis2" / "cache"
if qgis_cache.exists():
    shutil.rmtree(qgis_cache)
    print("✓ Cleared QGIS cache")

# Clear RealTerrain Studio cache
rt_cache = Path.home() / "AppData" / "Roaming" / "RealTerrainStudio" / "cache"
if rt_cache.exists():
    shutil.rmtree(rt_cache)
    print("✓ Cleared RealTerrain cache")

print("Restart QGIS for changes to take effect")
```

---

### Reset All Settings

If settings are corrupted:

```python
from pathlib import Path

settings_file = Path.home() / "AppData" / "Roaming" / "RealTerrainStudio" / "settings.json"

if settings_file.exists():
    settings_file.unlink()
    print("✓ Settings reset")
    print("Restart QGIS to regenerate default settings")
```

---

### Diagnostic Export

Create a diagnostic report for support:

```python
import json
import platform
import sys
from pathlib import Path
from datetime import datetime

report = {
    "timestamp": datetime.now().isoformat(),
    "system": {
        "os": platform.system(),
        "os_version": platform.release(),
        "python_version": sys.version,
    },
    "qgis": {},
    "packages": {},
    "realterrain": {}
}

# QGIS info
try:
    from qgis.core import Qgis
    report["qgis"]["version"] = Qgis.QGIS_VERSION
except Exception as e:
    report["qgis"]["error"] = str(e)

# Package versions
packages = ['numpy', 'requests', 'PIL', 'osgeo']
for pkg in packages:
    try:
        mod = __import__(pkg)
        version = getattr(mod, '__version__', 'unknown')
        report["packages"][pkg] = version
    except ImportError:
        report["packages"][pkg] = "NOT INSTALLED"

# RealTerrain info
try:
    from realterrain_studio import __version__
    report["realterrain"]["version"] = __version__
except Exception as e:
    report["realterrain"]["error"] = str(e)

# Save report
report_path = Path.home() / "realterrain_diagnostic.json"
with open(report_path, 'w') as f:
    json.dump(report, f, indent=2)

print(f"Diagnostic report saved to: {report_path}")
print("Send this file to support@realterrainstudio.com")
```

---

### Test Individual Components

Test each component separately:

**1. Test Elevation Fetcher:**

```python
from realterrain_studio.data_sources.srtm import fetch_srtm_elevation

bbox = (-122.5, 37.7, -122.4, 37.8)  # San Francisco
try:
    elevation = fetch_srtm_elevation(bbox, resolution=30)
    print(f"✓ Elevation fetch OK: {elevation.shape}")
except Exception as e:
    print(f"✗ Elevation fetch FAILED: {e}")
```

**2. Test Satellite Fetcher:**

```python
from realterrain_studio.data_sources.sentinel2_fetcher import fetch_sentinel2_imagery

bbox = (-122.5, 37.7, -122.4, 37.8)
try:
    imagery = fetch_sentinel2_imagery(bbox, resolution=10)
    print(f"✓ Satellite fetch OK: {imagery.shape}")
except Exception as e:
    print(f"✗ Satellite fetch FAILED: {e}")
```

**3. Test OSM Fetcher:**

```python
from realterrain_studio.data_sources.osm_fetcher import OSMFetcher

fetcher = OSMFetcher()
bbox = (-122.5, 37.7, -122.4, 37.8)
filters = {'roads': True, 'buildings': True}

try:
    data = fetcher.fetch_osm_data(bbox, filters)
    print(f"✓ OSM fetch OK: {len(data.get('roads', []))} roads, {len(data.get('buildings', []))} buildings")
except Exception as e:
    print(f"✗ OSM fetch FAILED: {e}")
```

---

## 📞 Getting Help

### Before Contacting Support

Please try:
1. Run Quick Diagnostics (top of this guide)
2. Search this guide for your specific error
3. Check community forum for similar issues
4. Clear cache and retry

### Contacting Support

**Email:** support@realterrainstudio.com

**Include:**
1. Diagnostic report (see Advanced Troubleshooting)
2. Error message (copy-paste or screenshot)
3. Steps to reproduce
4. What you've tried already
5. QGIS version
6. Operating system

**Example Good Support Request:**

```
Subject: Export fails with "Network timeout" error

System: Windows 11, QGIS 3.34.1, RealTerrain Studio 1.0.0

Issue: When exporting terrain for bbox (-122.5, 37.7, -122.4, 37.8),
export fails after ~30 seconds with error:
"Network timeout downloading elevation tile"

What I've tried:
- Verified internet connection (fast.com shows 100 Mbps)
- Tried different location - same error
- Cleared cache - didn't help
- Reinstalled plugin - didn't help

Attached: realterrain_diagnostic.json

Can you help?
```

### Response Times

- **Free tier:** 1-3 business days
- **Pro license:** 12-24 hours
- **Critical issues:** Within 6 hours (Pro only)

### Community Support

**Discord:** https://discord.gg/realterrainstudio
- Fastest community help
- Share screenshots, get real-time help

**Forum:** https://forum.realterrainstudio.com
- In-depth troubleshooting
- Search past issues

**GitHub Issues:** https://github.com/realterrainstudio/qgis-plugin/issues
- Bug reports
- Feature requests

---

## 📚 Additional Resources

- [User Guide](USER_GUIDE.md) - Full feature documentation
- [Installation Guide](INSTALLATION.md) - Setup instructions
- [API Documentation](API_DOCUMENTATION.md) - For developers
- [Error Handling Guide](ERROR_HANDLING.md) - Developer error handling
- [Video Tutorials](https://youtube.com/realterrainstudio) - Visual guides

---

**Still stuck? We're here to help!**

📧 support@realterrainstudio.com
💬 https://discord.gg/realterrainstudio

---

**Last Updated:** December 13, 2024
**Version:** 1.0.0
**For:** RealTerrain Studio
**By:** RealTerrain Studio Team
