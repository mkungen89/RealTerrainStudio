"""
SRTM Data Fetcher

Downloads elevation data from SRTM (Shuttle Radar Topography Mission).
Provides 30m and 90m resolution elevation data globally.
"""

import os
import tempfile
import requests
import numpy as np
import logging
from pathlib import Path
from typing import Tuple, Optional, Callable
from zipfile import ZipFile
import hashlib

# Import error handling utilities
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.error_handling import (
    DataFetchError,
    NetworkError,
    ValidationError,
    GDALError,
    retry,
    handle_errors,
    validate_bbox,
    validate_resolution,
    handle_network_error,
    handle_gdal_error
)

# Setup logging
logger = logging.getLogger(__name__)

try:
    from osgeo import gdal, osr
    GDAL_AVAILABLE = True
    logger.info("GDAL is available")
except ImportError:
    GDAL_AVAILABLE = False
    logger.warning("GDAL is not available")


class SRTMFetcher:
    """
    Fetches elevation data from SRTM sources.

    SRTM provides free global elevation data:
    - SRTM 1 Arc-Second (~30m resolution)
    - SRTM 3 Arc-Second (~90m resolution)
    """

    # Public SRTM data sources
    SRTM_BASE_URL = "https://srtm.csi.cgiar.org/wp-content/uploads/files/srtm_5x5/TIFF/"

    def __init__(self, cache_dir: Optional[str] = None):
        """
        Initialize SRTM fetcher.

        Args:
            cache_dir: Directory to cache downloaded tiles.
                      If None, uses system temp directory.

        Raises:
            GDALError: If GDAL is not available
        """
        if not GDAL_AVAILABLE:
            logger.error("GDAL is not available")
            raise GDALError(
                "GDAL is required for SRTM data fetching",
                user_message="GDAL library not found. Please install QGIS with GDAL support."
            )

        try:
            if cache_dir is None:
                cache_dir = os.path.join(tempfile.gettempdir(), "realterrain_srtm_cache")

            self.cache_dir = Path(cache_dir)
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"SRTM cache directory: {self.cache_dir}")

        except PermissionError as e:
            logger.error(f"Cannot create cache directory: {e}")
            raise DataFetchError(
                f"Cannot create cache directory {cache_dir}: {e}",
                user_message=f"No permission to create cache directory. Try a different location."
            )
        except Exception as e:
            logger.error(f"Failed to initialize SRTM fetcher: {e}")
            raise DataFetchError(
                f"SRTM fetcher initialization failed: {e}",
                user_message="Failed to initialize elevation data fetcher."
            )

    def fetch_elevation(
        self,
        bbox: Tuple[float, float, float, float],
        resolution: int = 30,
        progress_callback: Optional[Callable[[str, int], None]] = None
    ) -> np.ndarray:
        """
        Fetch elevation data for a bounding box.

        Args:
            bbox: Bounding box as (min_lon, min_lat, max_lon, max_lat)
            resolution: Target resolution in meters (30 or 90)
            progress_callback: Optional callback function(message, percent)

        Returns:
            numpy.ndarray: Elevation data in meters (2D array)

        Raises:
            ValidationError: If bbox is invalid or resolution not supported
            NetworkError: If download fails
            DataFetchError: If data fetching fails
        """
        logger.info(f"Fetching SRTM elevation data for bbox={bbox}, resolution={resolution}m")

        # Validate inputs
        try:
            bbox = validate_bbox(bbox)
            resolution = validate_resolution(resolution, allowed_resolutions=[30, 90])
        except ValidationError as e:
            logger.error(f"Input validation failed: {e}")
            raise

        try:
            if progress_callback:
                progress_callback("Identifying required tiles...", 0)

            # Determine which SRTM tiles are needed
            tiles = self._get_required_tiles(bbox)
            logger.info(f"Need to fetch {len(tiles)} SRTM tile(s): {tiles}")

            if progress_callback:
                progress_callback(f"Need to fetch {len(tiles)} tile(s)", 10)

            # Download and cache tiles
            tile_files = []
            failed_tiles = []

            for i, tile_id in enumerate(tiles):
                percent = 10 + int((i / len(tiles)) * 70)

                if progress_callback:
                    progress_callback(f"Downloading tile {i+1}/{len(tiles)}: {tile_id}", percent)

                try:
                    tile_file = self._fetch_tile(tile_id)
                    tile_files.append(tile_file)
                    logger.debug(f"Successfully fetched tile: {tile_id}")

                except Exception as e:
                    logger.warning(f"Failed to fetch tile {tile_id}: {e}")
                    failed_tiles.append((tile_id, str(e)))
                    # Continue with other tiles

            # Check if we got at least some tiles
            if not tile_files:
                logger.error(f"Failed to fetch any tiles. Errors: {failed_tiles}")
                raise DataFetchError(
                    f"Failed to download elevation data for area. Tiles failed: {len(failed_tiles)}",
                    user_message=(
                        "Could not download elevation data for this area. Possible reasons:\n"
                        "• No SRTM coverage for this location\n"
                        "• Network connection issues\n"
                        "• SRTM server temporarily unavailable\n\n"
                        "Try a different location or check your internet connection."
                    )
                )

            if failed_tiles:
                logger.warning(f"Some tiles failed ({len(failed_tiles)}), continuing with {len(tile_files)} tiles")

            if progress_callback:
                progress_callback("Merging tiles...", 80)

            # Merge tiles if multiple
            if len(tile_files) == 1:
                elevation = self._read_tile(tile_files[0], bbox)
            else:
                elevation = self._merge_tiles(tile_files, bbox)

            # Validate output
            if elevation is None or elevation.size == 0:
                raise DataFetchError(
                    "Elevation data is empty after processing",
                    user_message="Processed elevation data is empty. Try a different area."
                )

            logger.info(f"Successfully fetched elevation data: shape={elevation.shape}, "
                       f"range={np.nanmin(elevation):.1f}m to {np.nanmax(elevation):.1f}m")

            if progress_callback:
                progress_callback("Processing complete", 100)

            return elevation

        except (ValidationError, DataFetchError, NetworkError, GDALError):
            # Re-raise our custom errors
            raise

        except Exception as e:
            logger.exception(f"Unexpected error fetching SRTM data: {e}")
            raise DataFetchError(
                f"Unexpected error fetching elevation data: {e}",
                user_message=f"Failed to fetch elevation data: {str(e)}"
            )

    def _get_required_tiles(self, bbox: Tuple[float, float, float, float]) -> list:
        """
        Determine which SRTM tiles are needed for the bounding box.

        SRTM tiles are 5x5 degrees, named like: srtm_XX_YY

        Args:
            bbox: Bounding box (min_lon, min_lat, max_lon, max_lat)

        Returns:
            list: List of tile IDs needed
        """
        min_lon, min_lat, max_lon, max_lat = bbox

        tiles = []

        # SRTM tiles are 5x5 degrees
        # Tile naming: longitude from 1-72 (5° each), latitude from 1-24 (5° each)

        # Calculate tile ranges
        lon_start = int((min_lon + 180) // 5) + 1
        lon_end = int((max_lon + 180) // 5) + 1
        lat_start = int((60 - max_lat) // 5) + 1
        lat_end = int((60 - min_lat) // 5) + 1

        for lat_tile in range(lat_start, lat_end + 1):
            for lon_tile in range(lon_start, lon_end + 1):
                # SRTM tile naming convention
                tile_id = f"srtm_{lon_tile:02d}_{lat_tile:02d}"
                tiles.append(tile_id)

        return tiles

    @retry(
        max_attempts=3,
        delay=2.0,
        backoff=2.0,
        exceptions=(NetworkError,)
    )
    def _fetch_tile(self, tile_id: str) -> Path:
        """
        Fetch a single SRTM tile, using cache if available.

        Args:
            tile_id: Tile identifier (e.g., "srtm_12_04")

        Returns:
            Path: Path to the cached tile file

        Raises:
            NetworkError: If download fails after retries
            DataFetchError: If tile extraction fails
        """
        # Check cache first
        cache_file = self.cache_dir / f"{tile_id}.tif"

        if cache_file.exists():
            logger.debug(f"Using cached tile: {tile_id}")
            return cache_file

        # Download tile
        url = f"{self.SRTM_BASE_URL}{tile_id}.zip"
        logger.info(f"Downloading SRTM tile from: {url}")

        try:
            # Download with timeout and error handling
            response = handle_network_error(
                requests.get,
                url,
                timeout=60,
                stream=True
            )
            response.raise_for_status()

            # Save zip file temporarily
            zip_path = self.cache_dir / f"{tile_id}.zip"

            # Download with progress tracking
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0

            with open(zip_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)

            logger.debug(f"Downloaded {downloaded} bytes for tile {tile_id}")

            # Extract TIFF from zip
            try:
                with ZipFile(zip_path, 'r') as zip_ref:
                    # Find the .tif file in the zip
                    tif_files = [f for f in zip_ref.namelist() if f.endswith('.tif')]

                    if not tif_files:
                        raise DataFetchError(
                            f"No TIFF file found in {tile_id}.zip",
                            user_message=f"Downloaded tile {tile_id} is corrupted (no TIFF file found)."
                        )

                    # Extract to cache directory
                    zip_ref.extract(tif_files[0], self.cache_dir)

                    # Rename to standard name
                    extracted_file = self.cache_dir / tif_files[0]
                    extracted_file.rename(cache_file)

                logger.debug(f"Extracted tile {tile_id} successfully")

            except Exception as e:
                logger.error(f"Failed to extract tile {tile_id}: {e}")
                raise DataFetchError(
                    f"Failed to extract SRTM tile {tile_id}: {e}",
                    user_message=f"Downloaded tile {tile_id} appears to be corrupted."
                )

            finally:
                # Clean up zip file
                if zip_path.exists():
                    zip_path.unlink()

            return cache_file

        except NetworkError:
            # Re-raise NetworkError for retry decorator
            raise

        except requests.RequestException as e:
            logger.error(f"Network error downloading tile {tile_id}: {e}")
            raise NetworkError(
                f"Failed to download SRTM tile {tile_id}: {e}",
                user_message=f"Network error downloading elevation tile. Check your connection."
            )

        except Exception as e:
            logger.error(f"Unexpected error fetching tile {tile_id}: {e}")
            raise DataFetchError(
                f"Failed to fetch SRTM tile {tile_id}: {e}",
                user_message=f"Unexpected error downloading elevation data."
            )

    def _read_tile(self, tile_file: Path, bbox: Tuple[float, float, float, float]) -> np.ndarray:
        """
        Read elevation data from a single tile, clipped to bounding box.

        Args:
            tile_file: Path to the tile TIFF file
            bbox: Bounding box to clip to

        Returns:
            numpy.ndarray: Elevation data
        """
        dataset = gdal.Open(str(tile_file))

        if dataset is None:
            raise ValueError(f"Failed to open tile: {tile_file}")

        # Get geotransform
        geotransform = dataset.GetGeoTransform()

        min_lon, min_lat, max_lon, max_lat = bbox

        # Calculate pixel coordinates for bbox
        x_min = int((min_lon - geotransform[0]) / geotransform[1])
        y_max = int((min_lat - geotransform[3]) / geotransform[5])
        x_max = int((max_lon - geotransform[0]) / geotransform[1])
        y_min = int((max_lat - geotransform[3]) / geotransform[5])

        # Ensure bounds are within raster
        x_min = max(0, x_min)
        y_min = max(0, y_min)
        x_max = min(dataset.RasterXSize, x_max)
        y_max = min(dataset.RasterYSize, y_max)

        # Read data
        band = dataset.GetRasterBand(1)
        elevation = band.ReadAsArray(x_min, y_min, x_max - x_min, y_max - y_min)

        # Handle no-data values
        no_data = band.GetNoDataValue()
        if no_data is not None:
            elevation = np.where(elevation == no_data, np.nan, elevation)

        dataset = None  # Close dataset

        return elevation.astype(np.float32)

    def _merge_tiles(self, tile_files: list, bbox: Tuple[float, float, float, float]) -> np.ndarray:
        """
        Merge multiple SRTM tiles into a single elevation array.

        Args:
            tile_files: List of tile file paths
            bbox: Bounding box for final output

        Returns:
            numpy.ndarray: Merged elevation data
        """
        # Use GDAL VRT to merge tiles efficiently
        vrt_path = self.cache_dir / "merged.vrt"

        # Build VRT
        vrt_options = gdal.BuildVRTOptions(
            resampleAlg='bilinear',
            outputBounds=bbox
        )

        vrt = gdal.BuildVRT(
            str(vrt_path),
            [str(f) for f in tile_files],
            options=vrt_options
        )

        if vrt is None:
            raise ValueError("Failed to merge tiles")

        # Read merged data
        band = vrt.GetRasterBand(1)
        elevation = band.ReadAsArray()

        # Handle no-data
        no_data = band.GetNoDataValue()
        if no_data is not None:
            elevation = np.where(elevation == no_data, np.nan, elevation)

        vrt = None  # Close

        return elevation.astype(np.float32)

    def clear_cache(self):
        """Clear all cached SRTM tiles."""
        for file in self.cache_dir.glob("*.tif"):
            file.unlink()
        for file in self.cache_dir.glob("*.vrt"):
            file.unlink()

    def get_cache_size(self) -> int:
        """
        Get total size of cached data in bytes.

        Returns:
            int: Cache size in bytes
        """
        total_size = 0
        for file in self.cache_dir.glob("*"):
            if file.is_file():
                total_size += file.stat().st_size
        return total_size


def fetch_srtm_elevation(
    bbox: Tuple[float, float, float, float],
    resolution: int = 30,
    cache_dir: Optional[str] = None,
    progress_callback: Optional[Callable[[str, int], None]] = None
) -> np.ndarray:
    """
    Convenience function to fetch SRTM elevation data.

    Args:
        bbox: Bounding box as (min_lon, min_lat, max_lon, max_lat)
        resolution: Resolution in meters (30 or 90)
        cache_dir: Optional cache directory
        progress_callback: Optional progress callback(message, percent)

    Returns:
        numpy.ndarray: Elevation data in meters

    Example:
        >>> bbox = (-122.5, 37.7, -122.4, 37.8)  # San Francisco
        >>> elevation = fetch_srtm_elevation(bbox, resolution=30)
        >>> print(f"Elevation range: {np.nanmin(elevation):.1f}m to {np.nanmax(elevation):.1f}m")
    """
    fetcher = SRTMFetcher(cache_dir=cache_dir)
    return fetcher.fetch_elevation(bbox, resolution=resolution, progress_callback=progress_callback)
