"""
Material Classifier

Analyzes terrain and satellite data to automatically generate material masks.
Classifies terrain into grass, rock, dirt, sand, snow, forest, and water.
"""

import numpy as np
from scipy import ndimage
from typing import Dict, Tuple, Optional
import logging
from PIL import Image


logger = logging.getLogger(__name__)


class MaterialClassifier:
    """
    Automatic material classification for terrain.

    Analyzes:
    - Slope (steep = rock, flat = grass)
    - Elevation (high = snow, low = grass)
    - Satellite colors (green = vegetation, brown = dirt, blue = water)
    - Proximity to water

    Generates:
    - Grass mask
    - Rock mask
    - Dirt mask
    - Sand mask
    - Snow mask
    - Forest mask
    - Water mask
    """

    def __init__(self):
        """Initialize material classifier."""
        pass

    def classify(
        self,
        heightmap: np.ndarray,
        satellite: Optional[np.ndarray] = None,
        resolution: float = 30.0
    ) -> Dict[str, np.ndarray]:
        """
        Classify terrain materials.

        Args:
            heightmap: Elevation data (height, width) in meters
            satellite: Optional RGB satellite imagery (height, width, 3)
            resolution: Data resolution in meters

        Returns:
            dict: Material masks {name: numpy array (0.0-1.0 float)}

        Example:
            >>> classifier = MaterialClassifier()
            >>> masks = classifier.classify(heightmap, satellite)
            >>> print(f"Grass coverage: {masks['grass'].mean() * 100:.1f}%")
        """
        logger.info("Starting material classification...")

        # Calculate slope
        logger.info("  Calculating slope...")
        slope = self._calculate_slope(heightmap, resolution)

        # Calculate elevation stats
        min_elev = heightmap.min()
        max_elev = heightmap.max()
        elev_range = max_elev - min_elev

        logger.info(f"  Elevation: {min_elev:.1f}m - {max_elev:.1f}m (range: {elev_range:.1f}m)")
        logger.info(f"  Slope: {slope.min():.1f}° - {slope.max():.1f}°")

        # Initialize masks
        masks = {}

        # 1. Water mask (from satellite if available)
        if satellite is not None:
            logger.info("  Detecting water from satellite...")
            masks['water'] = self._detect_water(satellite, heightmap)
        else:
            masks['water'] = np.zeros_like(heightmap, dtype=np.float32)

        # 2. Snow mask (high elevation)
        logger.info("  Detecting snow...")
        masks['snow'] = self._detect_snow(heightmap, slope)

        # 3. Rock mask (steep slopes + high elevation)
        logger.info("  Detecting rock...")
        masks['rock'] = self._detect_rock(slope, heightmap)

        # 4. Sand mask (near water, flat, low elevation)
        logger.info("  Detecting sand...")
        masks['sand'] = self._detect_sand(heightmap, slope, masks['water'], satellite)

        # 5. Forest mask (from satellite if available)
        if satellite is not None:
            logger.info("  Detecting forest...")
            masks['forest'] = self._detect_forest(satellite, slope)
        else:
            masks['forest'] = np.zeros_like(heightmap, dtype=np.float32)

        # 6. Dirt mask (medium slope, brown colors)
        logger.info("  Detecting dirt...")
        masks['dirt'] = self._detect_dirt(slope, heightmap, satellite)

        # 7. Grass mask (everywhere else)
        logger.info("  Detecting grass...")
        masks['grass'] = self._detect_grass(
            slope, heightmap, satellite, masks
        )

        # Normalize masks (ensure they sum to ~1.0)
        logger.info("  Normalizing masks...")
        masks = self._normalize_masks(masks)

        # Smooth transitions
        logger.info("  Smoothing transitions...")
        masks = self._smooth_masks(masks)

        logger.info("Material classification complete!")

        return masks

    def _calculate_slope(
        self,
        heightmap: np.ndarray,
        resolution: float
    ) -> np.ndarray:
        """
        Calculate slope in degrees.

        Args:
            heightmap: Elevation data
            resolution: Pixel resolution in meters

        Returns:
            numpy.ndarray: Slope in degrees
        """
        # Calculate gradients
        dy, dx = np.gradient(heightmap, resolution)

        # Calculate slope magnitude
        slope_rad = np.arctan(np.sqrt(dx**2 + dy**2))
        slope_deg = np.degrees(slope_rad)

        return slope_deg

    def _detect_water(
        self,
        satellite: np.ndarray,
        heightmap: np.ndarray
    ) -> np.ndarray:
        """
        Detect water from satellite imagery (blue pixels).

        Args:
            satellite: RGB satellite imagery
            heightmap: Elevation data

        Returns:
            numpy.ndarray: Water mask (0.0-1.0)
        """
        # Normalize satellite to float
        sat_float = satellite.astype(np.float32) / 255.0

        # Extract channels
        r = sat_float[:, :, 0]
        g = sat_float[:, :, 1]
        b = sat_float[:, :, 2]

        # Water is blue (high B, low R, low G)
        water_score = np.zeros_like(r)

        # Blue > Red and Blue > Green
        water_score += np.clip((b - r) * 2.0, 0, 1)
        water_score += np.clip((b - g) * 2.0, 0, 1)

        # Normalize
        water_score = np.clip(water_score / 2.0, 0, 1)

        # Threshold
        water_mask = (water_score > 0.3).astype(np.float32)

        # Dilate slightly (water bodies)
        water_mask = ndimage.binary_dilation(water_mask, iterations=2).astype(np.float32)

        return water_mask

    def _detect_snow(
        self,
        heightmap: np.ndarray,
        slope: np.ndarray
    ) -> np.ndarray:
        """
        Detect snow (very high elevation).

        Args:
            heightmap: Elevation data
            slope: Slope in degrees

        Returns:
            numpy.ndarray: Snow mask (0.0-1.0)
        """
        min_elev = heightmap.min()
        max_elev = heightmap.max()
        elev_range = max_elev - min_elev

        # Snow threshold (top 15% of elevation range)
        snow_threshold = max_elev - (elev_range * 0.15)

        # Normalized elevation above snow line
        snow_score = np.clip(
            (heightmap - snow_threshold) / (elev_range * 0.15),
            0, 1
        )

        # Less snow on very steep slopes (avalanches)
        slope_factor = np.clip(1.0 - (slope - 45.0) / 15.0, 0, 1)
        snow_score *= slope_factor

        return snow_score

    def _detect_rock(
        self,
        slope: np.ndarray,
        heightmap: np.ndarray
    ) -> np.ndarray:
        """
        Detect rock (steep slopes + high elevation).

        Args:
            slope: Slope in degrees
            heightmap: Elevation data

        Returns:
            numpy.ndarray: Rock mask (0.0-1.0)
        """
        # Rock starts at 30° slope
        slope_score = np.clip((slope - 30.0) / 30.0, 0, 1)

        # More rock at higher elevations
        min_elev = heightmap.min()
        max_elev = heightmap.max()
        elev_range = max_elev - min_elev

        elev_normalized = (heightmap - min_elev) / (elev_range + 1e-6)
        elev_score = np.clip(elev_normalized * 1.5, 0, 1)

        # Combine (slope is primary)
        rock_score = slope_score * 0.7 + elev_score * 0.3

        return rock_score

    def _detect_sand(
        self,
        heightmap: np.ndarray,
        slope: np.ndarray,
        water_mask: np.ndarray,
        satellite: Optional[np.ndarray]
    ) -> np.ndarray:
        """
        Detect sand (near water, flat, low elevation, tan color).

        Args:
            heightmap: Elevation data
            slope: Slope in degrees
            water_mask: Water mask
            satellite: Optional satellite imagery

        Returns:
            numpy.ndarray: Sand mask (0.0-1.0)
        """
        # Distance to water
        if water_mask.sum() > 0:
            # Distance transform (in pixels)
            distance_to_water = ndimage.distance_transform_edt(1 - water_mask)

            # Normalize (sand within ~50 pixels of water)
            water_proximity = np.clip(1.0 - distance_to_water / 50.0, 0, 1)
        else:
            water_proximity = np.zeros_like(slope)

        # Flat areas (slope < 5°)
        flatness = np.clip(1.0 - slope / 5.0, 0, 1)

        # Low elevation
        min_elev = heightmap.min()
        max_elev = heightmap.max()
        elev_range = max_elev - min_elev

        low_elev = np.clip(
            1.0 - (heightmap - min_elev) / (elev_range * 0.3),
            0, 1
        )

        # Combine
        sand_score = water_proximity * flatness * low_elev

        # Boost if satellite shows tan/beige colors
        if satellite is not None:
            sat_float = satellite.astype(np.float32) / 255.0
            r = sat_float[:, :, 0]
            g = sat_float[:, :, 1]
            b = sat_float[:, :, 2]

            # Tan is high R+G, low B
            tan_score = np.clip((r + g) / 2.0 - b * 0.5, 0, 1)
            sand_score *= (1.0 + tan_score * 0.5)

        return np.clip(sand_score, 0, 1)

    def _detect_forest(
        self,
        satellite: np.ndarray,
        slope: np.ndarray
    ) -> np.ndarray:
        """
        Detect forest (dense green vegetation).

        Args:
            satellite: RGB satellite imagery
            slope: Slope in degrees

        Returns:
            numpy.ndarray: Forest mask (0.0-1.0)
        """
        sat_float = satellite.astype(np.float32) / 255.0

        r = sat_float[:, :, 0]
        g = sat_float[:, :, 1]
        b = sat_float[:, :, 2]

        # Dark green (high G, lower R and B)
        green_score = np.zeros_like(r)

        # Green > Red and Green > Blue
        green_score += np.clip((g - r) * 2.0, 0, 1)
        green_score += np.clip((g - b) * 1.5, 0, 1)

        # Dark (not too bright)
        brightness = (r + g + b) / 3.0
        darkness = np.clip(1.0 - (brightness - 0.3) / 0.4, 0, 1)

        # Combine
        vegetation_score = green_score * darkness

        # Less forest on steep slopes
        slope_factor = np.clip(1.0 - (slope - 35.0) / 20.0, 0, 1)

        forest_score = vegetation_score * slope_factor

        # Threshold (only strong vegetation = forest)
        forest_mask = (forest_score > 0.4).astype(np.float32)

        return forest_mask

    def _detect_dirt(
        self,
        slope: np.ndarray,
        heightmap: np.ndarray,
        satellite: Optional[np.ndarray]
    ) -> np.ndarray:
        """
        Detect dirt (medium slope, brown colors).

        Args:
            slope: Slope in degrees
            heightmap: Elevation data
            satellite: Optional satellite imagery

        Returns:
            numpy.ndarray: Dirt mask (0.0-1.0)
        """
        # Medium slopes (10° - 30°)
        slope_score = np.zeros_like(slope)
        slope_score += np.clip((slope - 10.0) / 10.0, 0, 1)  # Ramp up 10-20°
        slope_score *= np.clip(1.0 - (slope - 20.0) / 10.0, 0, 1)  # Ramp down 20-30°

        # Mid elevation
        min_elev = heightmap.min()
        max_elev = heightmap.max()
        elev_range = max_elev - min_elev

        elev_normalized = (heightmap - min_elev) / (elev_range + 1e-6)

        # Peak at 40% elevation
        elev_score = 1.0 - np.abs(elev_normalized - 0.4) * 2.0
        elev_score = np.clip(elev_score, 0, 1)

        # Combine
        dirt_score = slope_score * 0.6 + elev_score * 0.4

        # Boost if satellite shows brown colors
        if satellite is not None:
            sat_float = satellite.astype(np.float32) / 255.0
            r = sat_float[:, :, 0]
            g = sat_float[:, :, 1]
            b = sat_float[:, :, 2]

            # Brown is moderate R+G, low B
            brown_score = np.clip((r + g) / 2.0 - b, 0, 1)
            brown_score *= np.clip(1.0 - np.abs((r + g + b) / 3.0 - 0.4), 0, 1)

            dirt_score *= (1.0 + brown_score * 0.5)

        return np.clip(dirt_score, 0, 1)

    def _detect_grass(
        self,
        slope: np.ndarray,
        heightmap: np.ndarray,
        satellite: Optional[np.ndarray],
        other_masks: Dict[str, np.ndarray]
    ) -> np.ndarray:
        """
        Detect grass (default for gentle slopes, not covered by other materials).

        Args:
            slope: Slope in degrees
            heightmap: Elevation data
            satellite: Optional satellite imagery
            other_masks: Other material masks

        Returns:
            numpy.ndarray: Grass mask (0.0-1.0)
        """
        # Start with flat areas
        flatness = np.clip(1.0 - slope / 20.0, 0, 1)

        # Low-mid elevation
        min_elev = heightmap.min()
        max_elev = heightmap.max()
        elev_range = max_elev - min_elev

        elev_normalized = (heightmap - min_elev) / (elev_range + 1e-6)

        # Peak at 20% elevation
        elev_score = 1.0 - np.abs(elev_normalized - 0.2) * 1.5
        elev_score = np.clip(elev_score, 0, 1)

        # Combine
        grass_score = flatness * 0.7 + elev_score * 0.3

        # Boost if satellite shows green
        if satellite is not None:
            sat_float = satellite.astype(np.float32) / 255.0
            g = sat_float[:, :, 1]
            r = sat_float[:, :, 0]
            b = sat_float[:, :, 2]

            # Light green (high G, not too dark)
            green_score = np.clip((g - (r + b) / 2.0) * 1.5, 0, 1)
            brightness = (r + g + b) / 3.0
            light_score = np.clip((brightness - 0.3) / 0.4, 0, 1)

            grass_color = green_score * light_score

            grass_score *= (1.0 + grass_color * 0.5)

        # Reduce where other materials are present
        for name, mask in other_masks.items():
            if name != 'grass':
                grass_score *= (1.0 - mask * 0.8)

        return np.clip(grass_score, 0, 1)

    def _normalize_masks(
        self,
        masks: Dict[str, np.ndarray]
    ) -> Dict[str, np.ndarray]:
        """
        Normalize masks so they sum to 1.0 at each pixel.

        Args:
            masks: Material masks

        Returns:
            dict: Normalized masks
        """
        # Stack all masks
        mask_stack = np.stack(list(masks.values()), axis=0)

        # Sum across materials
        total = mask_stack.sum(axis=0) + 1e-6  # Avoid division by zero

        # Normalize
        normalized = {}
        for i, name in enumerate(masks.keys()):
            normalized[name] = masks[name] / total

        return normalized

    def _smooth_masks(
        self,
        masks: Dict[str, np.ndarray],
        sigma: float = 2.0
    ) -> Dict[str, np.ndarray]:
        """
        Smooth mask transitions with Gaussian filter.

        Args:
            masks: Material masks
            sigma: Gaussian sigma

        Returns:
            dict: Smoothed masks
        """
        smoothed = {}

        for name, mask in masks.items():
            smoothed[name] = ndimage.gaussian_filter(mask, sigma=sigma)

        # Re-normalize after smoothing
        smoothed = self._normalize_masks(smoothed)

        return smoothed

    def export_masks_png(
        self,
        masks: Dict[str, np.ndarray],
        output_dir: str
    ) -> Dict[str, str]:
        """
        Export masks as 8-bit grayscale PNG files.

        Args:
            masks: Material masks (0.0-1.0 float)
            output_dir: Output directory

        Returns:
            dict: Paths to created PNG files {name: path}

        Example:
            >>> classifier.export_masks_png(masks, 'output/masks/')
            {'grass': 'output/masks/grass_mask.png', ...}
        """
        import os
        os.makedirs(output_dir, exist_ok=True)

        created_files = {}

        for name, mask in masks.items():
            # Convert to 8-bit (0-255)
            mask_8bit = (mask * 255).astype(np.uint8)

            # Save as PNG
            output_path = os.path.join(output_dir, f"{name}_mask.png")
            img = Image.fromarray(mask_8bit, mode='L')
            img.save(output_path)

            created_files[name] = output_path

        return created_files

    def get_statistics(
        self,
        masks: Dict[str, np.ndarray]
    ) -> Dict[str, Dict]:
        """
        Get statistics about material coverage.

        Args:
            masks: Material masks

        Returns:
            dict: Statistics per material
        """
        stats = {}

        for name, mask in masks.items():
            stats[name] = {
                'coverage_percent': float(mask.mean() * 100),
                'min': float(mask.min()),
                'max': float(mask.max()),
                'mean': float(mask.mean()),
                'std': float(mask.std())
            }

        return stats


def classify_materials(
    heightmap: np.ndarray,
    satellite: Optional[np.ndarray] = None,
    resolution: float = 30.0
) -> Dict[str, np.ndarray]:
    """
    Convenience function to classify terrain materials.

    Args:
        heightmap: Elevation data
        satellite: Optional satellite imagery
        resolution: Data resolution in meters

    Returns:
        dict: Material masks

    Example:
        >>> from data_sources.srtm import fetch_srtm_elevation
        >>> from data_sources.sentinel2_fetcher import fetch_sentinel2_imagery
        >>> heightmap = fetch_srtm_elevation(bbox)
        >>> satellite = fetch_sentinel2_imagery(bbox)
        >>> masks = classify_materials(heightmap, satellite)
        >>> print(f"Grass: {masks['grass'].mean() * 100:.1f}%")
    """
    classifier = MaterialClassifier()
    return classifier.classify(heightmap, satellite, resolution)
