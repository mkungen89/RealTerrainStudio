# RealTerrain Studio - API Documentation

**Version:** 1.0.0
**Last Updated:** December 13, 2024

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Core Modules](#core-modules)
3. [Data Sources](#data-sources)
4. [Export System](#export-system)
5. [Error Handling](#error-handling)
6. [Utilities](#utilities)
7. [Examples](#examples)
8. [Type Reference](#type-reference)

---

## 🎯 Overview

RealTerrain Studio provides a comprehensive Python API for fetching, processing, and exporting real-world geographic data.

### Installation

```python
# RealTerrain Studio is a QGIS plugin
# Import after installing in QGIS

from realterrain_studio import RealTerrainExporter
from realterrain_studio.data_sources import (
    fetch_srtm_elevation,
    fetch_sentinel2_imagery,
    OSMFetcher
)
```

### Quick Start

```python
from realterrain_studio import RealTerrainExporter

# Create exporter
exporter = RealTerrainExporter()

# Define area (San Francisco)
bbox = (-122.5, 37.7, -122.4, 37.8)

# Configure export
config = {
    'elevation': {'enabled': True, 'resolution': 30},
    'satellite': {'enabled': True, 'resolution': 10},
    'osm': {'enabled': True, 'features': ['roads', 'buildings']}
}

# Export
result = exporter.export(
    bbox=bbox,
    config=config,
    output_path='C:/Terrains/SanFrancisco/'
)

print(f"Export complete: {result['output_files']}")
```

---

## 🏗️ Core Modules

### RealTerrainExporter

Main class for exporting terrain data.

#### Class Definition

```python
class RealTerrainExporter:
    """
    Main exporter for RealTerrain Studio.

    Coordinates data fetching, processing, and export.
    """

    def __init__(
        self,
        license_key: Optional[str] = None,
        cache_dir: Optional[str] = None
    ):
        """
        Initialize exporter.

        Args:
            license_key: Optional Pro license key
            cache_dir: Directory for caching downloaded data
        """
```

#### Methods

##### export()

Export terrain data for a bounding box.

```python
def export(
    self,
    bbox: Tuple[float, float, float, float],
    config: Dict,
    output_path: str,
    progress_callback: Optional[Callable[[str, int], None]] = None
) -> Dict:
    """
    Export terrain data.

    Args:
        bbox: Bounding box (min_lon, min_lat, max_lon, max_lat)
        config: Export configuration dictionary
        output_path: Directory to save output files
        progress_callback: Optional callback(message: str, percent: int)

    Returns:
        Dict with export results:
        {
            'success': True,
            'output_files': ['heightmap.png', 'satellite.jpg', ...],
            'metadata': {...},
            'stats': {
                'area_km2': 4.2,
                'download_mb': 45.3,
                'duration_seconds': 127
            }
        }

    Raises:
        ValidationError: If bbox or config invalid
        DataFetchError: If data cannot be fetched
        ExportError: If export fails

    Example:
        >>> exporter = RealTerrainExporter()
        >>> result = exporter.export(
        ...     bbox=(-122.5, 37.7, -122.4, 37.8),
        ...     config={'elevation': {'enabled': True}},
        ...     output_path='C:/Terrains/Test/'
        ... )
        >>> print(result['output_files'])
        ['terrain_heightmap.png', 'terrain_metadata.json']
    """
```

**Configuration Dictionary:**

```python
config = {
    # Elevation data
    'elevation': {
        'enabled': bool,              # Enable elevation data
        'resolution': int,            # Resolution in meters (10, 20, 30, 90)
        'source': str,                # 'srtm', 'aster', 'lidar'
        'fill_nodata': bool,          # Fill gaps in data
        'height_scale': float         # Vertical exaggeration (default: 1.0)
    },

    # Satellite imagery
    'satellite': {
        'enabled': bool,              # Enable satellite imagery
        'resolution': int,            # Resolution in meters (10, 20, 30)
        'source': str,                # 'sentinel2', 'landsat8'
        'date_range': Tuple[str, str],# (start_date, end_date) ISO format
        'max_cloud_cover': float,     # Max cloud cover % (0-100)
        'quality': int                # JPEG quality (0-100)
    },

    # OpenStreetMap data
    'osm': {
        'enabled': bool,              # Enable OSM data
        'features': List[str],        # ['roads', 'buildings', 'waterways', 'landuse']
        'filters': Dict               # Feature-specific filters
    },

    # Material classification
    'materials': {
        'enabled': bool,              # Enable material classification
        'method': str                 # 'satellite_analysis', 'osm_tags', 'both'
    },

    # Output format
    'output': {
        'format': str,                # 'rterrain', 'separate_files', 'fbx'
        'heightmap_format': str,      # 'png16', 'raw', 'tiff'
        'compress': bool,             # Compress output
        'power_of_two': bool          # Force power-of-2 dimensions for UE5
    }
}
```

##### preview()

Preview export without downloading data.

```python
def preview(
    self,
    bbox: Tuple[float, float, float, float],
    config: Dict
) -> Dict:
    """
    Preview export details without downloading.

    Args:
        bbox: Bounding box
        config: Export configuration

    Returns:
        Dict with preview information:
        {
            'area_km2': 4.2,
            'estimated_download_mb': 45.3,
            'estimated_duration_seconds': 120,
            'data_sources': ['SRTM', 'Sentinel-2', 'OSM'],
            'output_dimensions': (2048, 2048),
            'tiles_required': {
                'elevation': 4,
                'satellite': 16
            }
        }

    Example:
        >>> preview = exporter.preview(bbox, config)
        >>> print(f"Will download ~{preview['estimated_download_mb']} MB")
    """
```

##### validate_config()

Validate configuration dictionary.

```python
def validate_config(self, config: Dict) -> Tuple[bool, Optional[str]]:
    """
    Validate export configuration.

    Args:
        config: Configuration dictionary

    Returns:
        Tuple of (is_valid: bool, error_message: Optional[str])

    Example:
        >>> valid, error = exporter.validate_config(config)
        >>> if not valid:
        ...     print(f"Config error: {error}")
    """
```

---

## 📡 Data Sources

### SRTM Elevation Data

Fetch SRTM (Shuttle Radar Topography Mission) elevation data.

#### fetch_srtm_elevation()

```python
def fetch_srtm_elevation(
    bbox: Tuple[float, float, float, float],
    resolution: int = 30,
    cache_dir: Optional[str] = None,
    progress_callback: Optional[Callable[[str, int], None]] = None
) -> np.ndarray:
    """
    Fetch SRTM elevation data.

    Args:
        bbox: Bounding box (min_lon, min_lat, max_lon, max_lat)
        resolution: Resolution in meters (30 or 90)
        cache_dir: Optional cache directory
        progress_callback: Optional progress callback

    Returns:
        numpy.ndarray: Elevation data in meters (height, width)
                      dtype: float32
                      nodata value: -9999.0

    Raises:
        ValidationError: If bbox or resolution invalid
        DataFetchError: If data cannot be fetched
        NetworkError: If download fails

    Example:
        >>> bbox = (-122.5, 37.7, -122.4, 37.8)
        >>> elevation = fetch_srtm_elevation(bbox, resolution=30)
        >>> print(f"Elevation range: {elevation.min():.1f}m to {elevation.max():.1f}m")
        Elevation range: 0.0m to 281.5m

    Coverage:
        - Latitude: 60°N to 56°S
        - Resolution: 30m (SRTM-1) or 90m (SRTM-3)
        - Accuracy: ±16m vertical

    Notes:
        - Data is automatically cached
        - Tiles are merged seamlessly
        - Gaps are filled using interpolation
    """
```

#### SRTMFetcher Class

```python
class SRTMFetcher:
    """Low-level SRTM data fetcher."""

    def __init__(self, cache_dir: Optional[str] = None):
        """Initialize fetcher with cache directory."""

    def fetch_elevation(
        self,
        bbox: Tuple[float, float, float, float],
        resolution: int = 30,
        progress_callback: Optional[Callable[[str, int], None]] = None
    ) -> np.ndarray:
        """Fetch elevation data (same as fetch_srtm_elevation)."""

    def get_required_tiles(
        self,
        bbox: Tuple[float, float, float, float]
    ) -> List[str]:
        """
        Get list of SRTM tile IDs required for bbox.

        Returns:
            List of tile IDs (e.g., ['N37W123', 'N37W122'])
        """

    def get_tile_bounds(self, tile_id: str) -> Tuple[float, float, float, float]:
        """Get bounding box for a tile ID."""

    def clear_cache(self):
        """Clear cached elevation tiles."""
```

---

### Sentinel-2 Satellite Imagery

Fetch Sentinel-2 satellite imagery.

#### fetch_sentinel2_imagery()

```python
def fetch_sentinel2_imagery(
    bbox: Tuple[float, float, float, float],
    resolution: int = 10,
    max_cloud_cover: float = 20.0,
    date_range: Optional[Tuple[str, str]] = None,
    cache_dir: Optional[str] = None,
    progress_callback: Optional[Callable[[str, int], None]] = None
) -> np.ndarray:
    """
    Fetch Sentinel-2 satellite imagery.

    Args:
        bbox: Bounding box
        resolution: Resolution in meters (10, 20, or 60)
        max_cloud_cover: Maximum cloud cover percentage (0-100)
        date_range: Optional (start_date, end_date) as ISO strings
                   e.g., ('2024-01-01', '2024-12-31')
        cache_dir: Optional cache directory
        progress_callback: Optional progress callback

    Returns:
        numpy.ndarray: RGB imagery (height, width, 3)
                      dtype: uint8
                      range: 0-255

    Raises:
        ValidationError: If parameters invalid
        DataFetchError: If imagery cannot be fetched
        GDALError: If GDAL not available

    Example:
        >>> bbox = (-122.5, 37.7, -122.4, 37.8)
        >>> imagery = fetch_sentinel2_imagery(
        ...     bbox,
        ...     resolution=10,
        ...     max_cloud_cover=10.0,
        ...     date_range=('2024-06-01', '2024-08-31')
        ... )
        >>> print(f"Imagery shape: {imagery.shape}")
        Imagery shape: (2048, 2048, 3)

    Data Source:
        - Sentinel-2 Level 2A (atmospherically corrected)
        - Updated every 5 days
        - 10m resolution for RGB bands
        - Global coverage

    Notes:
        - Automatically selects clearest image in date range
        - Cloud masking applied
        - Color correction for realistic appearance
    """
```

#### Sentinel2Fetcher Class

```python
class Sentinel2Fetcher:
    """Low-level Sentinel-2 imagery fetcher."""

    def __init__(
        self,
        cache_dir: Optional[str] = None,
        api_key: Optional[str] = None
    ):
        """
        Initialize fetcher.

        Args:
            cache_dir: Cache directory
            api_key: Optional API key for Sentinel Hub
        """

    def fetch_imagery(
        self,
        bbox: Tuple[float, float, float, float],
        resolution: int = 10,
        max_cloud_cover: float = 20.0,
        date_range: Optional[Tuple[str, str]] = None,
        progress_callback: Optional[Callable[[str, int], None]] = None
    ) -> np.ndarray:
        """Fetch imagery (same as fetch_sentinel2_imagery)."""

    def search_scenes(
        self,
        bbox: Tuple[float, float, float, float],
        date_range: Optional[Tuple[str, str]] = None,
        max_cloud_cover: float = 20.0
    ) -> List[Dict]:
        """
        Search for available scenes.

        Returns:
            List of scene metadata dictionaries:
            [
                {
                    'id': 'S2A_MSIL2A_...',
                    'date': '2024-07-15',
                    'cloud_cover': 5.2,
                    'preview_url': 'https://...'
                },
                ...
            ]
        """

    def export_as_jpeg(
        self,
        imagery: np.ndarray,
        output_path: str,
        quality: int = 90
    ) -> str:
        """Export imagery as JPEG."""

    def export_as_png(
        self,
        imagery: np.ndarray,
        output_path: str
    ) -> str:
        """Export imagery as PNG."""
```

---

### OpenStreetMap Data

Fetch roads, buildings, and other features from OpenStreetMap.

#### OSMFetcher Class

```python
class OSMFetcher:
    """Fetch OpenStreetMap data via Overpass API."""

    def __init__(
        self,
        overpass_url: str = "https://overpass-api.de/api/interpreter",
        cache_dir: Optional[str] = None
    ):
        """
        Initialize OSM fetcher.

        Args:
            overpass_url: Overpass API endpoint
            cache_dir: Optional cache directory
        """

    def fetch_osm_data(
        self,
        bbox: Tuple[float, float, float, float],
        filters: Dict[str, bool],
        progress_callback: Optional[Callable[[str, int], None]] = None
    ) -> Dict:
        """
        Fetch OSM data for bounding box.

        Args:
            bbox: Bounding box
            filters: Feature filters:
                {
                    'roads': bool,
                    'buildings': bool,
                    'waterways': bool,
                    'landuse': bool,
                    'amenities': bool
                }
            progress_callback: Optional progress callback

        Returns:
            Dict with OSM features:
            {
                'roads': [
                    {
                        'id': 123456,
                        'type': 'primary',
                        'name': 'Main Street',
                        'geometry': [(lon, lat), ...],
                        'tags': {'highway': 'primary', 'lanes': '2', ...}
                    },
                    ...
                ],
                'buildings': [
                    {
                        'id': 789012,
                        'geometry': [(lon, lat), ...],  # Polygon
                        'height': 15.0,                 # meters
                        'tags': {'building': 'residential', ...}
                    },
                    ...
                ],
                'waterways': [...],
                'landuse': [...],
                'amenities': [...]
            }

        Raises:
            ValidationError: If bbox or filters invalid
            NetworkError: If Overpass API fails
            DataFetchError: If no data available

        Example:
            >>> fetcher = OSMFetcher()
            >>> data = fetcher.fetch_osm_data(
            ...     bbox=(-122.5, 37.7, -122.4, 37.8),
            ...     filters={'roads': True, 'buildings': True}
            ... )
            >>> print(f"Found {len(data['roads'])} roads")
            >>> print(f"Found {len(data['buildings'])} buildings")

        Notes:
            - Large areas are automatically chunked
            - Respects Overpass API rate limits
            - Automatic retry on transient errors
        """

    def fetch_chunk(
        self,
        bbox: Tuple[float, float, float, float],
        filters: Dict[str, bool]
    ) -> Dict:
        """
        Fetch single chunk (internal method).

        Called automatically by fetch_osm_data for large areas.
        """

    def build_overpass_query(
        self,
        bbox: Tuple[float, float, float, float],
        filters: Dict[str, bool]
    ) -> str:
        """
        Build Overpass QL query string.

        Returns:
            Overpass QL query

        Example:
            >>> query = fetcher.build_overpass_query(
            ...     bbox=(-122.5, 37.7, -122.4, 37.8),
            ...     filters={'roads': True}
            ... )
            >>> print(query)
            [out:json][timeout:180];
            (
              way["highway"](-122.5,37.7,-122.4,37.8);
            );
            out body;
            >;
            out skel qt;
        """
```

---

## 💾 Export System

### Export Formats

#### RTerrainFormat

Native .rterrain format (recommended).

```python
class RTerrainFormat:
    """
    Export as .rterrain file (binary format).

    Contains all data:
    - Heightmap
    - Satellite texture
    - Roads (splines)
    - Buildings
    - Materials
    - Metadata
    """

    @staticmethod
    def export(
        elevation: np.ndarray,
        satellite: Optional[np.ndarray],
        osm_data: Optional[Dict],
        materials: Optional[np.ndarray],
        metadata: Dict,
        output_path: str
    ) -> str:
        """
        Export as .rterrain file.

        Args:
            elevation: Elevation array (float32)
            satellite: Optional RGB imagery (uint8)
            osm_data: Optional OSM features dict
            materials: Optional material classification (uint8)
            metadata: Metadata dict
            output_path: Output file path

        Returns:
            str: Path to exported file

        Example:
            >>> RTerrainFormat.export(
            ...     elevation=elevation_data,
            ...     satellite=imagery_data,
            ...     osm_data=osm_features,
            ...     materials=material_map,
            ...     metadata={'bbox': bbox, ...},
            ...     output_path='C:/Terrains/terrain.rterrain'
            ... )
        """

    @staticmethod
    def load(file_path: str) -> Dict:
        """
        Load .rterrain file.

        Returns:
            Dict with all terrain data
        """
```

#### SeparateFilesFormat

Export as separate files (heightmap, textures, JSON).

```python
class SeparateFilesFormat:
    """Export as separate files."""

    @staticmethod
    def export(
        elevation: np.ndarray,
        satellite: Optional[np.ndarray],
        osm_data: Optional[Dict],
        materials: Optional[np.ndarray],
        metadata: Dict,
        output_dir: str,
        config: Dict
    ) -> List[str]:
        """
        Export as separate files.

        Args:
            elevation: Elevation array
            satellite: Optional imagery
            osm_data: Optional OSM data
            materials: Optional materials
            metadata: Metadata
            output_dir: Output directory
            config: Export configuration:
                {
                    'heightmap_format': 'png16' | 'raw' | 'tiff',
                    'satellite_format': 'jpg' | 'png' | 'tga',
                    'jpeg_quality': 90,
                    'compress': True
                }

        Returns:
            List of exported file paths

        Files Created:
            - terrain_heightmap.png (or .raw, .tiff)
            - terrain_satellite.jpg (if satellite provided)
            - terrain_roads.json (if OSM roads)
            - terrain_buildings.json (if OSM buildings)
            - terrain_materials.png (if materials)
            - terrain_metadata.json (always)
        """
```

---

## ⚠️ Error Handling

### Exception Hierarchy

```python
class RTerrainError(Exception):
    """Base exception for RealTerrain Studio."""

    def __init__(
        self,
        message: str,
        user_message: Optional[str] = None,
        recoverable: bool = True
    ):
        """
        Args:
            message: Technical error message (for logs)
            user_message: User-friendly message (for UI)
            recoverable: Whether user can recover from error
        """
        self.message = message
        self.user_message = user_message or message
        self.recoverable = recoverable

class NetworkError(RTerrainError):
    """Network-related errors."""
    pass

class DataFetchError(RTerrainError):
    """Data fetching errors."""
    pass

class ValidationError(RTerrainError):
    """Input validation errors."""

    def __init__(self, message: str, field: Optional[str] = None, **kwargs):
        """
        Args:
            message: Error message
            field: Field name that failed validation
        """
        super().__init__(message, **kwargs)
        self.field = field

class ExportError(RTerrainError):
    """Export operation errors."""
    pass

class GDALError(RTerrainError):
    """GDAL/geospatial processing errors."""
    pass

class LicenseError(RTerrainError):
    """License validation errors."""

    def __init__(self, message: str, **kwargs):
        # License errors are not recoverable
        super().__init__(message, recoverable=False, **kwargs)
```

### Error Handling Decorators

#### @retry

Automatically retry operations on failure.

```python
from realterrain_studio.utils.error_handling import retry

@retry(
    max_attempts=3,
    delay=1.0,
    backoff=2.0,
    exceptions=(NetworkError,),
    on_retry=None
)
def download_tile(tile_id):
    """
    Download tile with automatic retry.

    Will retry up to 3 times on NetworkError.
    Delays: 1s, 2s, 4s
    """
    response = requests.get(f"https://example.com/{tile_id}")
    return response.content
```

**Parameters:**
- `max_attempts`: Maximum number of attempts (default: 3)
- `delay`: Initial delay between retries in seconds (default: 1.0)
- `backoff`: Delay multiplier after each retry (default: 2.0)
- `exceptions`: Tuple of exceptions to catch (default: all)
- `on_retry`: Optional callback(attempt: int, error: Exception)

#### @handle_errors

Catch errors and return default value.

```python
from realterrain_studio.utils.error_handling import handle_errors

@handle_errors(
    default_return=None,
    log_traceback=True,
    user_message="Failed to load data"
)
def load_data(file_path):
    """
    Load data from file.

    Returns None if file doesn't exist or is invalid.
    """
    with open(file_path, 'r') as f:
        return json.load(f)
```

---

## 🔧 Utilities

### Validation Functions

#### validate_bbox()

```python
from realterrain_studio.utils.error_handling import validate_bbox

def validate_bbox(
    bbox: Tuple[float, float, float, float]
) -> Tuple[float, float, float, float]:
    """
    Validate and normalize bounding box.

    Args:
        bbox: (min_lon, min_lat, max_lon, max_lat)

    Returns:
        Normalized bbox

    Raises:
        ValidationError: If invalid

    Checks:
        - 4 numeric values
        - Longitude: -180 to 180, min < max
        - Latitude: -90 to 90, min < max
        - Size: Not too small (<0.001°) or too large (>10°)

    Example:
        >>> bbox = validate_bbox((-122.5, 37.7, -122.4, 37.8))
        >>> print(bbox)
        (-122.5, 37.7, -122.4, 37.8)
    """
```

#### validate_file_path()

```python
from realterrain_studio.utils.error_handling import validate_file_path

def validate_file_path(
    path: str,
    must_exist: bool = False,
    extension: Optional[str] = None
) -> Path:
    """
    Validate file path.

    Args:
        path: File path
        must_exist: Whether file must exist
        extension: Required extension (e.g., '.tif')

    Returns:
        Path object

    Raises:
        ValidationError: If invalid

    Example:
        >>> path = validate_file_path(
        ...     "C:/Terrains/heightmap.png",
        ...     extension=".png"
        ... )
    """
```

#### validate_resolution()

```python
from realterrain_studio.utils.error_handling import validate_resolution

def validate_resolution(
    resolution: int,
    allowed_resolutions: Optional[List[int]] = None
) -> int:
    """
    Validate resolution parameter.

    Args:
        resolution: Resolution in meters
        allowed_resolutions: Optional list of allowed values

    Returns:
        Validated resolution

    Raises:
        ValidationError: If invalid

    Example:
        >>> res = validate_resolution(30, allowed_resolutions=[10, 20, 30])
        >>> print(res)
        30
    """
```

### Helper Functions

#### safe_divide()

```python
def safe_divide(
    numerator: float,
    denominator: float,
    default: float = 0.0
) -> float:
    """
    Division that never crashes on zero.

    Example:
        >>> safe_divide(10, 0, default=999)
        999.0
    """
```

#### ensure_directory()

```python
def ensure_directory(path: str) -> Path:
    """
    Create directory if it doesn't exist.

    Example:
        >>> dir_path = ensure_directory("C:/Terrains/Cache")
        >>> print(dir_path.exists())
        True
    """
```

---

## 📚 Examples

### Example 1: Basic Terrain Export

```python
from realterrain_studio import RealTerrainExporter

# Create exporter
exporter = RealTerrainExporter(
    license_key="RTSP-XXXX-XXXX-XXXX-XXXX"  # Or None for free tier
)

# Define area (London)
london_bbox = (-0.2, 51.4, 0.0, 51.6)

# Configure export
config = {
    'elevation': {
        'enabled': True,
        'resolution': 30,
        'source': 'srtm'
    },
    'satellite': {
        'enabled': True,
        'resolution': 10,
        'max_cloud_cover': 20
    },
    'osm': {
        'enabled': True,
        'features': ['roads', 'buildings']
    },
    'output': {
        'format': 'rterrain'
    }
}

# Preview before export
preview = exporter.preview(london_bbox, config)
print(f"Will download ~{preview['estimated_download_mb']:.1f} MB")
print(f"Estimated time: {preview['estimated_duration_seconds']}s")

# Export
result = exporter.export(
    bbox=london_bbox,
    config=config,
    output_path='C:/Terrains/London/',
    progress_callback=lambda msg, pct: print(f"[{pct}%] {msg}")
)

print(f"Success! Exported to: {result['output_files']}")
```

### Example 2: Elevation Only

```python
from realterrain_studio.data_sources.srtm import fetch_srtm_elevation
import matplotlib.pyplot as plt

# Fetch elevation for Mount Everest region
everest_bbox = (86.8, 27.9, 87.0, 28.1)

elevation = fetch_srtm_elevation(
    bbox=everest_bbox,
    resolution=30,
    progress_callback=lambda msg, pct: print(f"{msg} ({pct}%)")
)

print(f"Elevation shape: {elevation.shape}")
print(f"Height range: {elevation.min():.0f}m to {elevation.max():.0f}m")

# Visualize
plt.imshow(elevation, cmap='terrain')
plt.colorbar(label='Elevation (m)')
plt.title('Mount Everest Region')
plt.show()
```

### Example 3: OSM Data Only

```python
from realterrain_studio.data_sources.osm_fetcher import OSMFetcher

# Fetch OSM data for Manhattan
manhattan_bbox = (-74.02, 40.70, -73.97, 40.78)

fetcher = OSMFetcher()
osm_data = fetcher.fetch_osm_data(
    bbox=manhattan_bbox,
    filters={
        'roads': True,
        'buildings': True,
        'amenities': True
    }
)

print(f"Roads: {len(osm_data['roads'])}")
print(f"Buildings: {len(osm_data['buildings'])}")
print(f"Amenities: {len(osm_data['amenities'])}")

# Analyze roads
road_types = {}
for road in osm_data['roads']:
    road_type = road['tags'].get('highway', 'unknown')
    road_types[road_type] = road_types.get(road_type, 0) + 1

print("\nRoad types:")
for road_type, count in sorted(road_types.items(), key=lambda x: -x[1]):
    print(f"  {road_type}: {count}")
```

### Example 4: Custom Progress Callback

```python
from realterrain_studio import RealTerrainExporter
from tqdm import tqdm

class ProgressBar:
    """Custom progress bar using tqdm."""

    def __init__(self):
        self.pbar = tqdm(total=100, desc="Export")
        self.last_pct = 0

    def callback(self, message: str, percent: int):
        # Update progress
        self.pbar.update(percent - self.last_pct)
        self.last_pct = percent

        # Update description
        self.pbar.set_description(message)

        if percent >= 100:
            self.pbar.close()

# Use custom progress bar
progress = ProgressBar()
exporter = RealTerrainExporter()

result = exporter.export(
    bbox=(-122.5, 37.7, -122.4, 37.8),
    config={...},
    output_path='C:/Terrains/Test/',
    progress_callback=progress.callback
)
```

### Example 5: Error Handling

```python
from realterrain_studio import RealTerrainExporter
from realterrain_studio.utils.error_handling import (
    ValidationError,
    NetworkError,
    DataFetchError,
    ExportError
)

exporter = RealTerrainExporter()

try:
    result = exporter.export(
        bbox=invalid_bbox,
        config=config,
        output_path='C:/Terrains/Test/'
    )

except ValidationError as e:
    print(f"Invalid input: {e.user_message}")
    print(f"Field: {e.field}")
    # Can fix and retry

except NetworkError as e:
    print(f"Network problem: {e.user_message}")
    # Retry or check connection

except DataFetchError as e:
    print(f"Data unavailable: {e.user_message}")
    # Try different location or source

except ExportError as e:
    print(f"Export failed: {e.user_message}")
    # Check disk space, permissions

except Exception as e:
    print(f"Unexpected error: {e}")
    # Report bug
```

---

## 📘 Type Reference

### Common Types

```python
from typing import Tuple, Dict, List, Optional, Callable

# Bounding box
BBox = Tuple[float, float, float, float]  # (min_lon, min_lat, max_lon, max_lat)

# Progress callback
ProgressCallback = Callable[[str, int], None]  # (message, percent)

# Coordinate
Coord = Tuple[float, float]  # (longitude, latitude)

# RGB color
RGB = Tuple[int, int, int]  # (red, green, blue) 0-255

# Configuration dictionary
ExportConfig = Dict[str, Any]

# Metadata
Metadata = Dict[str, Any]
```

### Array Types

```python
import numpy as np
from numpy.typing import NDArray

# Elevation data
ElevationArray = NDArray[np.float32]  # (height, width), values in meters

# RGB imagery
ImageryArray = NDArray[np.uint8]  # (height, width, 3), values 0-255

# Material classification
MaterialArray = NDArray[np.uint8]  # (height, width), material IDs

# Boolean mask
MaskArray = NDArray[np.bool_]  # (height, width)
```

---

## 📞 Support

For API support:
- **Documentation:** https://docs.realterrainstudio.com
- **Examples:** https://github.com/realterrainstudio/examples
- **API Reference:** https://api-docs.realterrainstudio.com
- **Discord:** https://discord.gg/realterrainstudio

---

**Last Updated:** December 13, 2024
**Version:** 1.0.0
**For:** RealTerrain Studio
**By:** RealTerrain Studio Team
