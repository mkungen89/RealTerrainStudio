"""
Heightmap Exporter

Exports elevation data as heightmaps in various formats for game engines.
"""

import numpy as np
from pathlib import Path
from typing import Optional, Tuple, Dict

from ..data_sources.elevation_processor import ElevationProcessor
from .rterrain_format import create_rterrain_package


class HeightmapExporter:
    """Exports elevation data as heightmaps."""

    def __init__(self):
        """Initialize the heightmap exporter."""
        self.processor = ElevationProcessor()

    def export_rterrain(
        self,
        elevation: np.ndarray,
        output_path: str,
        project_name: str,
        bbox: Tuple[float, float, float, float],
        resolution: int = 30,
        target_size: Optional[Tuple[int, int]] = None,
        fill_nodata: bool = True,
        smooth: bool = False,
        smooth_sigma: float = 1.0,
        **kwargs
    ) -> str:
        """
        Export elevation as .rterrain package.

        Args:
            elevation: Elevation data as numpy array
            output_path: Output file path
            project_name: Name of the project
            bbox: Bounding box (min_lon, min_lat, max_lon, max_lat)
            resolution: Data resolution in meters
            target_size: Optional target (height, width) for resampling
            fill_nodata: Whether to fill NaN values
            smooth: Whether to apply smoothing
            smooth_sigma: Smoothing strength
            **kwargs: Additional data (satellite, materials, etc.)

        Returns:
            str: Path to created .rterrain file
        """
        # Process elevation
        processed = self._process_elevation(
            elevation,
            target_size=target_size,
            fill_nodata=fill_nodata,
            smooth=smooth,
            smooth_sigma=smooth_sigma
        )

        # Create package
        rterrain_path = create_rterrain_package(
            output_path,
            project_name,
            bbox,
            processed,
            resolution=resolution,
            **kwargs
        )

        return rterrain_path

    def export_png16(
        self,
        elevation: np.ndarray,
        output_path: str,
        target_size: Optional[Tuple[int, int]] = None,
        fill_nodata: bool = True,
        smooth: bool = False,
        smooth_sigma: float = 1.0
    ) -> str:
        """
        Export elevation as 16-bit PNG heightmap.

        Args:
            elevation: Elevation data
            output_path: Output file path
            target_size: Optional target size
            fill_nodata: Whether to fill NaN
            smooth: Whether to smooth
            smooth_sigma: Smoothing strength

        Returns:
            str: Path to created PNG file
        """
        # Process elevation
        processed = self._process_elevation(
            elevation,
            target_size=target_size,
            fill_nodata=fill_nodata,
            smooth=smooth,
            smooth_sigma=smooth_sigma
        )

        # Export as PNG16
        self.processor.to_png16(processed, output_path, normalize=True)

        return output_path

    def export_geotiff(
        self,
        elevation: np.ndarray,
        output_path: str,
        bbox: Tuple[float, float, float, float],
        target_size: Optional[Tuple[int, int]] = None,
        fill_nodata: bool = True,
        smooth: bool = False,
        smooth_sigma: float = 1.0,
        crs: str = 'EPSG:4326'
    ) -> str:
        """
        Export elevation as GeoTIFF.

        Args:
            elevation: Elevation data
            output_path: Output file path
            bbox: Bounding box
            target_size: Optional target size
            fill_nodata: Whether to fill NaN
            smooth: Whether to smooth
            smooth_sigma: Smoothing strength
            crs: Coordinate reference system

        Returns:
            str: Path to created GeoTIFF file
        """
        # Process elevation
        processed = self._process_elevation(
            elevation,
            target_size=target_size,
            fill_nodata=fill_nodata,
            smooth=smooth,
            smooth_sigma=smooth_sigma
        )

        # Export as GeoTIFF
        self.processor.to_geotiff(processed, output_path, bbox, crs=crs)

        return output_path

    def export_raw(
        self,
        elevation: np.ndarray,
        output_path: str,
        target_size: Optional[Tuple[int, int]] = None,
        fill_nodata: bool = True,
        smooth: bool = False,
        smooth_sigma: float = 1.0,
        bit_depth: int = 16
    ) -> str:
        """
        Export elevation as RAW binary.

        Args:
            elevation: Elevation data
            output_path: Output file path
            target_size: Optional target size
            fill_nodata: Whether to fill NaN
            smooth: Whether to smooth
            smooth_sigma: Smoothing strength
            bit_depth: 8 or 16

        Returns:
            str: Path to created RAW file
        """
        # Process elevation
        processed = self._process_elevation(
            elevation,
            target_size=target_size,
            fill_nodata=fill_nodata,
            smooth=smooth,
            smooth_sigma=smooth_sigma
        )

        # Export as RAW
        self.processor.to_raw(processed, output_path, bit_depth=bit_depth)

        return output_path

    def _process_elevation(
        self,
        elevation: np.ndarray,
        target_size: Optional[Tuple[int, int]] = None,
        fill_nodata: bool = True,
        smooth: bool = False,
        smooth_sigma: float = 1.0
    ) -> np.ndarray:
        """
        Process elevation data.

        Args:
            elevation: Input elevation
            target_size: Optional target size
            fill_nodata: Fill NaN values
            smooth: Apply smoothing
            smooth_sigma: Smoothing strength

        Returns:
            numpy.ndarray: Processed elevation
        """
        processed = elevation.copy()

        # Fill no-data
        if fill_nodata:
            processed = self.processor.fill_nodata(processed, method='linear')

        # Resample
        if target_size is not None:
            processed = self.processor.resample(
                processed,
                target_size,
                method='bilinear'
            )

        # Smooth
        if smooth:
            processed = self.processor.smooth(
                processed,
                sigma=smooth_sigma,
                preserve_peaks=False
            )

        return processed

    def get_statistics(self, elevation: np.ndarray) -> Dict:
        """
        Get statistics for elevation data.

        Args:
            elevation: Elevation array

        Returns:
            dict: Statistics
        """
        return self.processor.calculate_statistics(elevation)


def export_heightmap(
    elevation: np.ndarray,
    output_path: str,
    bbox: Tuple[float, float, float, float],
    project_name: str = "Terrain",
    format: str = "rterrain",
    **kwargs
) -> str:
    """
    Convenience function to export heightmap.

    Args:
        elevation: Elevation data
        output_path: Output path
        bbox: Bounding box
        project_name: Project name
        format: Export format ('rterrain', 'png16', 'geotiff', 'raw')
        **kwargs: Additional export options

    Returns:
        str: Path to exported file

    Example:
        >>> elevation = fetch_srtm_elevation(bbox)
        >>> export_heightmap(
        ...     elevation,
        ...     'terrain.rterrain',
        ...     bbox,
        ...     project_name='San Francisco',
        ...     target_size=(1024, 1024)
        ... )
    """
    exporter = HeightmapExporter()

    if format == 'rterrain':
        return exporter.export_rterrain(
            elevation,
            output_path,
            project_name,
            bbox,
            **kwargs
        )
    elif format == 'png16':
        return exporter.export_png16(elevation, output_path, **kwargs)
    elif format == 'geotiff':
        return exporter.export_geotiff(elevation, output_path, bbox, **kwargs)
    elif format == 'raw':
        return exporter.export_raw(elevation, output_path, **kwargs)
    else:
        raise ValueError(f"Unknown format: {format}")
