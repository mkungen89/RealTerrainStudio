"""
Elevation Data Processor

Processes raw elevation data into various formats for export.
Handles resampling, no-data filling, smoothing, and format conversion.
"""

import numpy as np
from typing import Tuple, Optional, Dict
from pathlib import Path
from scipy import ndimage
from scipy.interpolate import griddata

try:
    from osgeo import gdal, osr
    GDAL_AVAILABLE = True
except ImportError:
    GDAL_AVAILABLE = False


class ElevationProcessor:
    """
    Processes elevation data for export.

    Provides resampling, no-data filling, smoothing, and format conversion.
    """

    def __init__(self):
        """Initialize the elevation processor."""
        if not GDAL_AVAILABLE:
            raise ImportError("GDAL is required. Please install GDAL.")

    def resample(
        self,
        elevation: np.ndarray,
        target_resolution: Tuple[int, int],
        method: str = 'bilinear'
    ) -> np.ndarray:
        """
        Resample elevation data to target resolution.

        Args:
            elevation: Input elevation array
            target_resolution: Target (height, width)
            method: Resampling method ('nearest', 'bilinear', 'cubic')

        Returns:
            numpy.ndarray: Resampled elevation data
        """
        if method == 'nearest':
            order = 0
        elif method == 'bilinear':
            order = 1
        elif method == 'cubic':
            order = 3
        else:
            raise ValueError(f"Unknown resampling method: {method}")

        # Calculate zoom factors
        zoom_y = target_resolution[0] / elevation.shape[0]
        zoom_x = target_resolution[1] / elevation.shape[1]

        # Resample using scipy
        resampled = ndimage.zoom(elevation, (zoom_y, zoom_x), order=order)

        return resampled.astype(np.float32)

    def fill_nodata(
        self,
        elevation: np.ndarray,
        method: str = 'linear'
    ) -> np.ndarray:
        """
        Fill no-data (NaN) values in elevation data.

        Args:
            elevation: Elevation array with potential NaN values
            method: Filling method ('linear', 'nearest', 'cubic', 'zero')

        Returns:
            numpy.ndarray: Elevation with no-data filled
        """
        if not np.any(np.isnan(elevation)):
            # No NaN values, return as-is
            return elevation

        if method == 'zero':
            # Simple: replace NaN with 0
            return np.nan_to_num(elevation, nan=0.0)

        # Create mask of valid data
        mask = ~np.isnan(elevation)

        if not np.any(mask):
            # All NaN, return zeros
            return np.zeros_like(elevation)

        # Get coordinates of valid and invalid points
        valid_coords = np.array(np.where(mask)).T
        invalid_coords = np.array(np.where(~mask)).T

        if len(invalid_coords) == 0:
            return elevation

        # Get valid values
        valid_values = elevation[mask]

        # Interpolate invalid points
        if method == 'nearest':
            filled_values = griddata(
                valid_coords,
                valid_values,
                invalid_coords,
                method='nearest'
            )
        elif method == 'linear':
            # Try linear first, fall back to nearest for extrapolation
            filled_values = griddata(
                valid_coords,
                valid_values,
                invalid_coords,
                method='linear',
                fill_value=np.nan
            )
            # Fill any remaining NaNs with nearest
            still_nan = np.isnan(filled_values)
            if np.any(still_nan):
                filled_values[still_nan] = griddata(
                    valid_coords,
                    valid_values,
                    invalid_coords[still_nan],
                    method='nearest'
                )
        elif method == 'cubic':
            # Try cubic first, fall back to nearest
            filled_values = griddata(
                valid_coords,
                valid_values,
                invalid_coords,
                method='cubic',
                fill_value=np.nan
            )
            still_nan = np.isnan(filled_values)
            if np.any(still_nan):
                filled_values[still_nan] = griddata(
                    valid_coords,
                    valid_values,
                    invalid_coords[still_nan],
                    method='nearest'
                )
        else:
            raise ValueError(f"Unknown filling method: {method}")

        # Create output array
        filled = elevation.copy()
        filled[~mask] = filled_values

        return filled

    def smooth(
        self,
        elevation: np.ndarray,
        sigma: float = 1.0,
        preserve_peaks: bool = True
    ) -> np.ndarray:
        """
        Apply smoothing to elevation data.

        Args:
            elevation: Input elevation array
            sigma: Gaussian sigma (larger = more smoothing)
            preserve_peaks: If True, uses median filter for peak preservation

        Returns:
            numpy.ndarray: Smoothed elevation data
        """
        if preserve_peaks:
            # Median filter preserves edges better
            kernel_size = int(sigma * 2) * 2 + 1  # Ensure odd
            smoothed = ndimage.median_filter(elevation, size=kernel_size)
        else:
            # Gaussian blur for smooth gradients
            smoothed = ndimage.gaussian_filter(elevation, sigma=sigma)

        return smoothed.astype(np.float32)

    def calculate_statistics(self, elevation: np.ndarray) -> Dict:
        """
        Calculate statistics for elevation data.

        Args:
            elevation: Elevation array

        Returns:
            dict: Statistics including min, max, mean, std, range
        """
        # Ignore NaN values
        valid = elevation[~np.isnan(elevation)]

        if len(valid) == 0:
            return {
                'min': 0.0,
                'max': 0.0,
                'mean': 0.0,
                'std': 0.0,
                'range': 0.0,
                'valid_pixels': 0,
                'total_pixels': elevation.size,
                'valid_percentage': 0.0
            }

        stats = {
            'min': float(np.min(valid)),
            'max': float(np.max(valid)),
            'mean': float(np.mean(valid)),
            'std': float(np.std(valid)),
            'range': float(np.max(valid) - np.min(valid)),
            'valid_pixels': len(valid),
            'total_pixels': elevation.size,
            'valid_percentage': (len(valid) / elevation.size) * 100.0
        }

        return stats

    def normalize(
        self,
        elevation: np.ndarray,
        min_val: Optional[float] = None,
        max_val: Optional[float] = None,
        target_range: Tuple[float, float] = (0.0, 1.0)
    ) -> np.ndarray:
        """
        Normalize elevation data to a target range.

        Args:
            elevation: Input elevation array
            min_val: Minimum value (if None, uses data min)
            max_val: Maximum value (if None, uses data max)
            target_range: Target (min, max) range

        Returns:
            numpy.ndarray: Normalized elevation
        """
        if min_val is None:
            min_val = np.nanmin(elevation)
        if max_val is None:
            max_val = np.nanmax(elevation)

        if max_val == min_val:
            # Constant elevation, return middle of target range
            return np.full_like(elevation, (target_range[0] + target_range[1]) / 2)

        # Normalize to 0-1
        normalized = (elevation - min_val) / (max_val - min_val)

        # Scale to target range
        normalized = normalized * (target_range[1] - target_range[0]) + target_range[0]

        return normalized.astype(np.float32)

    def to_geotiff(
        self,
        elevation: np.ndarray,
        output_path: str,
        bbox: Tuple[float, float, float, float],
        crs: str = 'EPSG:4326'
    ):
        """
        Export elevation to GeoTIFF format.

        Args:
            elevation: Elevation array
            output_path: Output file path
            bbox: Bounding box (min_lon, min_lat, max_lon, max_lat)
            crs: Coordinate reference system
        """
        driver = gdal.GetDriverByName('GTiff')

        # Create dataset
        dataset = driver.Create(
            output_path,
            elevation.shape[1],  # width
            elevation.shape[0],  # height
            1,  # bands
            gdal.GDT_Float32
        )

        if dataset is None:
            raise ValueError(f"Failed to create GeoTIFF: {output_path}")

        # Set geotransform
        min_lon, min_lat, max_lon, max_lat = bbox
        pixel_width = (max_lon - min_lon) / elevation.shape[1]
        pixel_height = (max_lat - min_lat) / elevation.shape[0]

        geotransform = [
            min_lon,          # top left x
            pixel_width,      # w-e pixel resolution
            0,                # rotation
            max_lat,          # top left y
            0,                # rotation
            -pixel_height     # n-s pixel resolution (negative)
        ]

        dataset.SetGeoTransform(geotransform)

        # Set projection
        srs = osr.SpatialReference()
        srs.ImportFromEPSG(int(crs.split(':')[1]))
        dataset.SetProjection(srs.ExportToWkt())

        # Write data
        band = dataset.GetRasterBand(1)
        band.WriteArray(elevation)
        band.SetNoDataValue(np.nan)

        # Close dataset
        dataset = None

    def to_png16(
        self,
        elevation: np.ndarray,
        output_path: str,
        normalize: bool = True
    ):
        """
        Export elevation to 16-bit PNG.

        Args:
            elevation: Elevation array
            output_path: Output file path
            normalize: If True, normalize to 0-65535 range
        """
        if normalize:
            # Normalize to 16-bit range
            min_val = np.nanmin(elevation)
            max_val = np.nanmax(elevation)

            if max_val > min_val:
                normalized = (elevation - min_val) / (max_val - min_val)
                elevation_16 = (normalized * 65535).astype(np.uint16)
            else:
                elevation_16 = np.zeros_like(elevation, dtype=np.uint16)
        else:
            # Clip to 16-bit range
            elevation_16 = np.clip(elevation, 0, 65535).astype(np.uint16)

        # Handle NaN values
        elevation_16 = np.nan_to_num(elevation_16, nan=0)

        # Use PIL to save
        try:
            from PIL import Image
            img = Image.fromarray(elevation_16, mode='I;16')
            img.save(output_path)
        except ImportError:
            # Fallback: use GDAL
            driver = gdal.GetDriverByName('PNG')
            dataset = driver.Create(
                output_path,
                elevation_16.shape[1],
                elevation_16.shape[0],
                1,
                gdal.GDT_UInt16
            )
            band = dataset.GetRasterBand(1)
            band.WriteArray(elevation_16)
            dataset = None

    def to_raw(
        self,
        elevation: np.ndarray,
        output_path: str,
        bit_depth: int = 16
    ):
        """
        Export elevation to RAW format (binary).

        Args:
            elevation: Elevation array
            output_path: Output file path
            bit_depth: Bit depth (8 or 16)
        """
        if bit_depth == 8:
            # Normalize to 0-255
            min_val = np.nanmin(elevation)
            max_val = np.nanmax(elevation)

            if max_val > min_val:
                normalized = (elevation - min_val) / (max_val - min_val)
                data = (normalized * 255).astype(np.uint8)
            else:
                data = np.zeros_like(elevation, dtype=np.uint8)

        elif bit_depth == 16:
            # Normalize to 0-65535
            min_val = np.nanmin(elevation)
            max_val = np.nanmax(elevation)

            if max_val > min_val:
                normalized = (elevation - min_val) / (max_val - min_val)
                data = (normalized * 65535).astype(np.uint16)
            else:
                data = np.zeros_like(elevation, dtype=np.uint16)
        else:
            raise ValueError(f"Unsupported bit depth: {bit_depth}")

        # Handle NaN
        data = np.nan_to_num(data, nan=0)

        # Write to file
        data.tofile(output_path)


def process_elevation(
    elevation: np.ndarray,
    target_resolution: Optional[Tuple[int, int]] = None,
    fill_nodata: bool = True,
    smooth: bool = False,
    smooth_sigma: float = 1.0
) -> np.ndarray:
    """
    Convenience function to process elevation data.

    Args:
        elevation: Input elevation array
        target_resolution: Optional target (height, width)
        fill_nodata: Whether to fill NaN values
        smooth: Whether to apply smoothing
        smooth_sigma: Smoothing strength

    Returns:
        numpy.ndarray: Processed elevation

    Example:
        >>> elevation = fetch_srtm_elevation(bbox)
        >>> processed = process_elevation(
        ...     elevation,
        ...     target_resolution=(1024, 1024),
        ...     fill_nodata=True,
        ...     smooth=True
        ... )
    """
    processor = ElevationProcessor()

    # Fill no-data
    if fill_nodata:
        elevation = processor.fill_nodata(elevation, method='linear')

    # Resample
    if target_resolution is not None:
        elevation = processor.resample(elevation, target_resolution, method='bilinear')

    # Smooth
    if smooth:
        elevation = processor.smooth(elevation, sigma=smooth_sigma)

    return elevation
