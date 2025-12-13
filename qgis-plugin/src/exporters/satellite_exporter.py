"""
Satellite Texture Exporter

Processes and exports satellite imagery as textures for game engines.
Supports JPEG (compressed), TGA (lossless), and PNG formats.
"""

import os
import numpy as np
from pathlib import Path
from typing import Optional, Tuple, Dict, Any
from PIL import Image, ImageEnhance
import json


class SatelliteExporter:
    """
    Exports satellite imagery as game-ready textures.

    Features:
    - Multiple formats (JPEG, TGA, PNG)
    - Color correction (brightness, contrast, saturation)
    - Dimension matching with heightmap
    - Metadata generation
    - Size optimization
    """

    def __init__(self):
        """Initialize the satellite exporter."""
        pass

    def export_jpeg(
        self,
        imagery: np.ndarray,
        output_path: str,
        quality: int = 90,
        optimize: bool = True,
        color_correction: Optional[Dict[str, float]] = None
    ) -> str:
        """
        Export satellite imagery as JPEG.

        Args:
            imagery: RGB imagery as numpy array (H, W, 3) uint8
            output_path: Output file path
            quality: JPEG quality (0-100, default 90)
            optimize: Apply JPEG optimization
            color_correction: Optional dict with 'brightness', 'contrast', 'saturation'

        Returns:
            str: Path to created JPEG file
        """
        # Apply color correction if requested
        if color_correction:
            imagery = self._apply_color_correction(imagery, color_correction)

        # Convert numpy to PIL Image
        img = Image.fromarray(imagery, mode='RGB')

        # Save as JPEG
        img.save(
            output_path,
            'JPEG',
            quality=quality,
            optimize=optimize,
            progressive=True  # Progressive JPEG for better web display
        )

        return output_path

    def export_tga(
        self,
        imagery: np.ndarray,
        output_path: str,
        color_correction: Optional[Dict[str, float]] = None
    ) -> str:
        """
        Export satellite imagery as TGA (lossless).

        Args:
            imagery: RGB imagery as numpy array
            output_path: Output file path
            color_correction: Optional color correction

        Returns:
            str: Path to created TGA file
        """
        # Apply color correction if requested
        if color_correction:
            imagery = self._apply_color_correction(imagery, color_correction)

        # Convert to PIL Image
        img = Image.fromarray(imagery, mode='RGB')

        # Save as TGA
        img.save(output_path, 'TGA')

        return output_path

    def export_png(
        self,
        imagery: np.ndarray,
        output_path: str,
        optimize: bool = True,
        color_correction: Optional[Dict[str, float]] = None
    ) -> str:
        """
        Export satellite imagery as PNG.

        Args:
            imagery: RGB imagery as numpy array
            output_path: Output file path
            optimize: Apply PNG optimization
            color_correction: Optional color correction

        Returns:
            str: Path to created PNG file
        """
        # Apply color correction if requested
        if color_correction:
            imagery = self._apply_color_correction(imagery, color_correction)

        # Convert to PIL Image
        img = Image.fromarray(imagery, mode='RGB')

        # Save as PNG
        img.save(output_path, 'PNG', optimize=optimize)

        return output_path

    def match_dimensions(
        self,
        imagery: np.ndarray,
        target_size: Tuple[int, int],
        method: str = 'bilinear'
    ) -> np.ndarray:
        """
        Resize imagery to match target dimensions.

        Args:
            imagery: Input imagery
            target_size: Target (height, width)
            method: Resampling method ('nearest', 'bilinear', 'bicubic', 'lanczos')

        Returns:
            numpy.ndarray: Resized imagery
        """
        # Convert to PIL
        img = Image.fromarray(imagery, mode='RGB')

        # Map method names to PIL constants
        resample_methods = {
            'nearest': Image.Resampling.NEAREST,
            'bilinear': Image.Resampling.BILINEAR,
            'bicubic': Image.Resampling.BICUBIC,
            'lanczos': Image.Resampling.LANCZOS
        }

        resample = resample_methods.get(method, Image.Resampling.BILINEAR)

        # Resize (PIL uses (width, height))
        target_height, target_width = target_size
        resized = img.resize((target_width, target_height), resample)

        # Convert back to numpy
        return np.array(resized)

    def _apply_color_correction(
        self,
        imagery: np.ndarray,
        correction: Dict[str, float]
    ) -> np.ndarray:
        """
        Apply color correction to imagery.

        Args:
            imagery: Input imagery
            correction: Dict with 'brightness', 'contrast', 'saturation' (1.0 = no change)

        Returns:
            numpy.ndarray: Corrected imagery
        """
        # Convert to PIL
        img = Image.fromarray(imagery, mode='RGB')

        # Apply brightness
        if 'brightness' in correction:
            brightness = correction['brightness']
            enhancer = ImageEnhance.Brightness(img)
            img = enhancer.enhance(brightness)

        # Apply contrast
        if 'contrast' in correction:
            contrast = correction['contrast']
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(contrast)

        # Apply saturation
        if 'saturation' in correction:
            saturation = correction['saturation']
            enhancer = ImageEnhance.Color(img)
            img = enhancer.enhance(saturation)

        # Convert back to numpy
        return np.array(img)

    def create_metadata(
        self,
        imagery: np.ndarray,
        bbox: Tuple[float, float, float, float],
        output_path: str,
        format: str = 'jpeg',
        quality: Optional[int] = None,
        color_correction: Optional[Dict[str, float]] = None,
        source: str = 'Sentinel-2'
    ) -> str:
        """
        Create metadata file for satellite texture.

        Args:
            imagery: The imagery array
            bbox: Bounding box
            output_path: Path to metadata file
            format: Export format
            quality: JPEG quality if applicable
            color_correction: Applied color correction
            source: Imagery source

        Returns:
            str: Path to metadata file
        """
        height, width = imagery.shape[:2]

        metadata = {
            'type': 'satellite_texture',
            'source': source,
            'format': format.upper(),
            'dimensions': {
                'width': int(width),
                'height': int(height)
            },
            'bbox': {
                'min_lon': bbox[0],
                'min_lat': bbox[1],
                'max_lon': bbox[2],
                'max_lat': bbox[3]
            },
            'channels': 'RGB',
            'bit_depth': 8,
            'color_space': 'sRGB'
        }

        # Add quality if JPEG
        if format.lower() == 'jpeg' and quality is not None:
            metadata['quality'] = quality

        # Add color correction if applied
        if color_correction:
            metadata['color_correction'] = color_correction

        # Calculate file size if exists
        texture_path = output_path.replace('_meta.json', f'.{format.lower()}')
        if os.path.exists(texture_path):
            file_size = os.path.getsize(texture_path)
            metadata['file_size_bytes'] = file_size
            metadata['file_size_mb'] = round(file_size / (1024 * 1024), 2)

        # Write metadata
        with open(output_path, 'w') as f:
            json.dump(metadata, f, indent=2)

        return output_path

    def export_with_metadata(
        self,
        imagery: np.ndarray,
        output_dir: str,
        base_name: str,
        bbox: Tuple[float, float, float, float],
        format: str = 'jpeg',
        quality: int = 90,
        color_correction: Optional[Dict[str, float]] = None,
        match_heightmap_size: Optional[Tuple[int, int]] = None
    ) -> Dict[str, str]:
        """
        Export satellite texture with metadata.

        Args:
            imagery: RGB imagery
            output_dir: Output directory
            base_name: Base filename (without extension)
            bbox: Bounding box
            format: Export format ('jpeg', 'tga', 'png')
            quality: JPEG quality (if applicable)
            color_correction: Optional color correction
            match_heightmap_size: Optional (height, width) to match

        Returns:
            dict: Paths to created files {'texture': path, 'metadata': path}
        """
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)

        # Match dimensions if requested
        if match_heightmap_size is not None:
            imagery = self.match_dimensions(imagery, match_heightmap_size)

        # Determine output paths
        texture_path = os.path.join(output_dir, f"{base_name}.{format.lower()}")
        metadata_path = os.path.join(output_dir, f"{base_name}_meta.json")

        # Export based on format
        if format.lower() == 'jpeg':
            self.export_jpeg(
                imagery,
                texture_path,
                quality=quality,
                color_correction=color_correction
            )
        elif format.lower() == 'tga':
            self.export_tga(
                imagery,
                texture_path,
                color_correction=color_correction
            )
        elif format.lower() == 'png':
            self.export_png(
                imagery,
                texture_path,
                color_correction=color_correction
            )
        else:
            raise ValueError(f"Unsupported format: {format}")

        # Create metadata
        self.create_metadata(
            imagery,
            bbox,
            metadata_path,
            format=format,
            quality=quality if format.lower() == 'jpeg' else None,
            color_correction=color_correction
        )

        return {
            'texture': texture_path,
            'metadata': metadata_path
        }

    def get_file_size_mb(self, file_path: str) -> float:
        """Get file size in MB."""
        if os.path.exists(file_path):
            return os.path.getsize(file_path) / (1024 * 1024)
        return 0.0

    def calculate_optimal_quality(
        self,
        imagery: np.ndarray,
        target_size_mb: float = 50.0
    ) -> int:
        """
        Calculate optimal JPEG quality to hit target file size.

        Args:
            imagery: Input imagery
            target_size_mb: Target file size in MB

        Returns:
            int: Recommended JPEG quality (0-100)
        """
        # Test with quality 90
        test_path = 'temp_quality_test.jpg'

        try:
            img = Image.fromarray(imagery, mode='RGB')
            img.save(test_path, 'JPEG', quality=90)

            test_size_mb = os.path.getsize(test_path) / (1024 * 1024)

            # Estimate quality needed
            if test_size_mb <= target_size_mb:
                recommended_quality = 90
            else:
                # Linear approximation (rough estimate)
                ratio = target_size_mb / test_size_mb
                recommended_quality = int(90 * ratio)
                recommended_quality = max(60, min(95, recommended_quality))

            # Clean up
            os.remove(test_path)

            return recommended_quality

        except Exception as e:
            # Default to 85
            return 85


def export_satellite_texture(
    imagery: np.ndarray,
    output_path: str,
    bbox: Tuple[float, float, float, float],
    format: str = 'jpeg',
    quality: int = 90,
    match_heightmap: Optional[np.ndarray] = None,
    color_correction: Optional[Dict[str, float]] = None
) -> Dict[str, str]:
    """
    Convenience function to export satellite texture.

    Args:
        imagery: RGB imagery array
        output_path: Output file path (texture will be created)
        bbox: Bounding box
        format: Export format ('jpeg', 'tga', 'png')
        quality: JPEG quality
        match_heightmap: Optional heightmap to match dimensions
        color_correction: Optional color correction dict

    Returns:
        dict: Paths to created files

    Example:
        >>> from data_sources.sentinel2_fetcher import fetch_sentinel2_imagery
        >>> bbox = (-122.5, 37.7, -122.4, 37.8)
        >>> imagery = fetch_sentinel2_imagery(bbox, resolution=10)
        >>> result = export_satellite_texture(
        ...     imagery,
        ...     'satellite.jpg',
        ...     bbox,
        ...     quality=90
        ... )
        >>> print(f"Texture: {result['texture']}")
        >>> print(f"Metadata: {result['metadata']}")
    """
    exporter = SatelliteExporter()

    # Get output directory and base name
    output_path = Path(output_path)
    output_dir = output_path.parent
    base_name = output_path.stem

    # Match heightmap dimensions if provided
    match_size = None
    if match_heightmap is not None:
        match_size = match_heightmap.shape[:2]

    return exporter.export_with_metadata(
        imagery,
        str(output_dir),
        base_name,
        bbox,
        format=format,
        quality=quality,
        color_correction=color_correction,
        match_heightmap_size=match_size
    )
