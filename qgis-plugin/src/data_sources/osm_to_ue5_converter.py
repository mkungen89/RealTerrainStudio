"""
OSM to UE5 Coordinate Converter

Converts OpenStreetMap data (WGS84 lat/lon) to Unreal Engine 5 coordinates (X, Y, Z in cm).
Handles proper ground placement using heightmap data.
"""

import math
import logging
from typing import Dict, List, Tuple, Optional
import numpy as np


logger = logging.getLogger(__name__)


class OSMToUE5Converter:
    """
    Convert OSM data to UE5 coordinate system with proper placement.

    UE5 Coordinate System:
    - X: Forward (North)
    - Y: Right (East)
    - Z: Up (Elevation)
    - Units: Centimeters

    Features:
    - WGS84 to UE5 coordinate transformation
    - Ground elevation sampling from heightmap
    - Building rotation calculation
    - Height estimation from OSM tags
    """

    def __init__(
        self,
        bbox: Tuple[float, float, float, float],
        heightmap: np.ndarray,
        terrain_origin: Tuple[float, float, float] = (0, 0, 0)
    ):
        """
        Initialize converter.

        Args:
            bbox: Bounding box (min_lon, min_lat, max_lon, max_lat)
            heightmap: Elevation data (height, width) in meters
            terrain_origin: UE5 world origin (X, Y, Z) in cm
        """
        self.bbox = bbox
        self.heightmap = heightmap
        self.terrain_origin = terrain_origin

        # Calculate coordinate transformation factors
        self.setup_coordinate_transform()

    def setup_coordinate_transform(self):
        """
        Calculate transformation from WGS84 (lat/lon) to UE5 (X, Y, Z).

        Accounts for Earth curvature (meters per degree varies with latitude).
        """
        min_lon, min_lat, max_lon, max_lat = self.bbox

        # Calculate at center latitude
        lat_center = (min_lat + max_lat) / 2

        # Meters per degree longitude (varies with latitude)
        # Formula: 111,320 * cos(latitude)
        self.meters_per_degree_lon = 111320 * math.cos(math.radians(lat_center))

        # Meters per degree latitude (roughly constant)
        self.meters_per_degree_lat = 110540

        # UE5 uses centimeters
        self.cm_per_degree_lon = self.meters_per_degree_lon * 100
        self.cm_per_degree_lat = self.meters_per_degree_lat * 100

        logger.info(f"Coordinate transform at lat {lat_center:.4f}:")
        logger.info(f"  {self.cm_per_degree_lon:.2f} cm/deg lon")
        logger.info(f"  {self.cm_per_degree_lat:.2f} cm/deg lat")

    def latlon_to_ue5(self, lat: float, lon: float) -> Tuple[float, float, float]:
        """
        Convert lat/lon to UE5 world coordinates (X, Y, Z).

        Args:
            lat: Latitude
            lon: Longitude

        Returns:
            tuple: (X, Y, Z) in UE5 centimeters

        Example:
            >>> converter = OSMToUE5Converter(bbox, heightmap)
            >>> x, y, z = converter.latlon_to_ue5(37.7749, -122.4194)
            >>> print(f"UE5 position: ({x:.0f}, {y:.0f}, {z:.0f}) cm")
        """
        min_lon, min_lat, max_lon, max_lat = self.bbox

        # Calculate offset from terrain origin (in degrees)
        delta_lat = lat - min_lat
        delta_lon = lon - min_lon

        # Convert to UE5 centimeters
        ue5_x = delta_lat * self.cm_per_degree_lat  # North
        ue5_y = delta_lon * self.cm_per_degree_lon  # East

        # Get ground elevation at this point
        ue5_z = self.get_ground_elevation(lat, lon)

        # Add terrain origin offset
        ue5_x += self.terrain_origin[0]
        ue5_y += self.terrain_origin[1]
        ue5_z += self.terrain_origin[2]

        return (ue5_x, ue5_y, ue5_z)

    def get_ground_elevation(self, lat: float, lon: float) -> float:
        """
        Sample heightmap to get ground elevation at lat/lon.

        CRITICAL: This prevents objects from floating in air!

        Args:
            lat: Latitude
            lon: Longitude

        Returns:
            float: Ground elevation in centimeters
        """
        min_lon, min_lat, max_lon, max_lat = self.bbox

        # Normalize to [0, 1]
        norm_x = (lat - min_lat) / (max_lat - min_lat)
        norm_y = (lon - min_lon) / (max_lon - min_lon)

        # Clamp to valid range
        norm_x = max(0, min(1, norm_x))
        norm_y = max(0, min(1, norm_y))

        # Sample heightmap
        height, width = self.heightmap.shape
        pixel_x = int(norm_x * (height - 1))
        pixel_y = int(norm_y * (width - 1))

        # Get elevation value (convert from meters to cm)
        elevation_m = self.heightmap[pixel_x, pixel_y]
        elevation_cm = elevation_m * 100

        return elevation_cm

    def convert_building(self, osm_building: Dict) -> Dict:
        """
        Convert OSM building to UE5 placement data.

        Args:
            osm_building: OSM building data with geometry and tags

        Returns:
            dict: UE5 building placement data

        Example:
            >>> building_data = converter.convert_building(osm_building)
            >>> print(f"Position: {building_data['position']}")
            >>> print(f"Height: {building_data['height']} cm")
        """
        # Get building footprint (polygon)
        geometry = osm_building.get('geometry', [])

        if not geometry:
            logger.warning(f"Building {osm_building.get('id')} has no geometry")
            return None

        # Convert all nodes to UE5 coordinates
        ue5_points = [
            self.latlon_to_ue5(node['lat'], node['lon'])
            for node in geometry
        ]

        # Calculate building center
        center_x = sum(p[0] for p in ue5_points) / len(ue5_points)
        center_y = sum(p[1] for p in ue5_points) / len(ue5_points)
        center_z = sum(p[2] for p in ue5_points) / len(ue5_points)

        # Calculate building rotation (from longest wall)
        rotation = self.calculate_building_rotation(ue5_points)

        # Get building height
        tags = osm_building.get('tags', {})
        height_cm = self.get_building_height(tags)

        # Get number of floors
        levels = int(tags.get('building:levels', 1))

        # Get building type
        building_type = tags.get('building', 'yes')

        return {
            'type': 'building',
            'osm_id': osm_building.get('id'),
            'position': (center_x, center_y, center_z),
            'rotation': rotation,  # Yaw angle in degrees
            'footprint': ue5_points,
            'height': height_cm,
            'levels': levels,
            'building_type': building_type,
            'tags': tags
        }

    def calculate_building_rotation(self, points: List[Tuple[float, float, float]]) -> float:
        """
        Calculate building rotation from footprint.

        Finds longest wall and aligns building to it.
        This ensures buildings face roads correctly!

        Args:
            points: Building footprint points in UE5 coords

        Returns:
            float: Rotation angle in degrees (0-360)
        """
        if len(points) < 2:
            return 0.0

        # Find longest edge
        max_length = 0
        best_angle = 0

        for i in range(len(points) - 1):
            p1 = points[i]
            p2 = points[i + 1]

            # Calculate edge length
            dx = p2[0] - p1[0]
            dy = p2[1] - p1[1]
            length = math.sqrt(dx * dx + dy * dy)

            if length > max_length:
                max_length = length
                # Calculate angle (in degrees)
                best_angle = math.degrees(math.atan2(dy, dx))

        # Normalize to 0-360
        best_angle = best_angle % 360

        return best_angle

    def get_building_height(self, tags: Dict) -> float:
        """
        Get building height from OSM tags.

        Priority:
        1. building:height (explicit)
        2. height (explicit)
        3. building:levels (estimate 3m per floor)
        4. Default (one story = 3m)

        Args:
            tags: OSM tags

        Returns:
            float: Building height in centimeters
        """
        # Check explicit height
        if 'building:height' in tags:
            try:
                height_m = float(tags['building:height'])
                return height_m * 100  # meters to cm
            except ValueError:
                pass

        if 'height' in tags:
            try:
                height_str = tags['height']
                # Handle "10 m" or "10m" format
                height_str = height_str.replace(' m', '').replace('m', '')
                height_m = float(height_str)
                return height_m * 100
            except ValueError:
                pass

        # Estimate from levels
        if 'building:levels' in tags:
            try:
                levels = int(tags['building:levels'])
                height_m = levels * 3.0  # 3m per floor
                return height_m * 100
            except ValueError:
                pass

        # Default: one story = 3m = 300cm
        return 300.0

    def convert_road(self, osm_road: Dict) -> Dict:
        """
        Convert OSM road/way to UE5 spline data.

        Args:
            osm_road: OSM way data with geometry

        Returns:
            dict: UE5 road spline data
        """
        geometry = osm_road.get('geometry', [])

        if not geometry:
            logger.warning(f"Road {osm_road.get('id')} has no geometry")
            return None

        # Convert all points to UE5 coordinates
        spline_points = [
            self.latlon_to_ue5(node['lat'], node['lon'])
            for node in geometry
        ]

        tags = osm_road.get('tags', {})

        # Get road type
        highway_type = tags.get('highway', 'unclassified')

        # Get road width (estimate if not specified)
        width_m = self.estimate_road_width(highway_type, tags)
        width_cm = width_m * 100

        # Get lanes
        lanes = int(tags.get('lanes', 2))

        # Get name
        name = tags.get('name', '')

        return {
            'type': 'road',
            'osm_id': osm_road.get('id'),
            'highway_type': highway_type,
            'spline_points': spline_points,
            'width': width_cm,
            'lanes': lanes,
            'name': name,
            'tags': tags
        }

    def estimate_road_width(self, highway_type: str, tags: Dict) -> float:
        """
        Estimate road width in meters based on type.

        Args:
            highway_type: OSM highway type
            tags: OSM tags

        Returns:
            float: Road width in meters
        """
        # Check explicit width
        if 'width' in tags:
            try:
                width_str = tags['width']
                width_str = width_str.replace(' m', '').replace('m', '')
                return float(width_str)
            except ValueError:
                pass

        # Default widths by road type
        WIDTHS = {
            'motorway': 12.0,
            'trunk': 10.0,
            'primary': 8.0,
            'secondary': 7.0,
            'tertiary': 6.0,
            'residential': 5.0,
            'service': 3.5,
            'track': 3.0,
            'path': 1.5,
            'footway': 1.5,
            'cycleway': 2.0
        }

        return WIDTHS.get(highway_type, 5.0)

    def convert_poi(self, osm_node: Dict) -> Dict:
        """
        Convert OSM POI node to UE5 placement data.

        Args:
            osm_node: OSM node data

        Returns:
            dict: UE5 POI placement data
        """
        lat = osm_node.get('lat')
        lon = osm_node.get('lon')

        if lat is None or lon is None:
            return None

        # Convert to UE5 coordinates
        x, y, z = self.latlon_to_ue5(lat, lon)

        tags = osm_node.get('tags', {})

        # Get POI type
        amenity = tags.get('amenity', 'unknown')

        return {
            'type': 'poi',
            'osm_id': osm_node.get('id'),
            'position': (x, y, z),
            'amenity': amenity,
            'name': tags.get('name', ''),
            'tags': tags
        }

    def convert_all(self, osm_data: Dict) -> Dict:
        """
        Convert all OSM data to UE5 format.

        Args:
            osm_data: OSM data with nodes, ways, relations

        Returns:
            dict: UE5-formatted data with buildings, roads, pois
        """
        ue5_data = {
            'buildings': [],
            'roads': [],
            'pois': [],
            'other': []
        }

        # Convert ways (buildings, roads, etc.)
        for way in osm_data.get('ways', []):
            tags = way.get('tags', {})

            if 'building' in tags:
                building = self.convert_building(way)
                if building:
                    ue5_data['buildings'].append(building)

            elif 'highway' in tags:
                road = self.convert_road(way)
                if road:
                    ue5_data['roads'].append(road)

            else:
                # Other features (water, landuse, etc.)
                ue5_data['other'].append(way)

        # Convert nodes (POIs, street furniture, etc.)
        for node in osm_data.get('nodes', []):
            tags = node.get('tags', {})

            if 'amenity' in tags or 'shop' in tags:
                poi = self.convert_poi(node)
                if poi:
                    ue5_data['pois'].append(poi)

        logger.info(f"Converted to UE5 format:")
        logger.info(f"  Buildings: {len(ue5_data['buildings'])}")
        logger.info(f"  Roads: {len(ue5_data['roads'])}")
        logger.info(f"  POIs: {len(ue5_data['pois'])}")

        return ue5_data


def convert_osm_to_ue5(
    osm_data: Dict,
    bbox: Tuple[float, float, float, float],
    heightmap: np.ndarray,
    terrain_origin: Tuple[float, float, float] = (0, 0, 0)
) -> Dict:
    """
    Convenience function to convert OSM data to UE5 format.

    Args:
        osm_data: OSM data
        bbox: Bounding box
        heightmap: Elevation data
        terrain_origin: UE5 terrain origin

    Returns:
        dict: UE5-formatted data

    Example:
        >>> osm_data = fetch_osm_data(bbox, filters)
        >>> heightmap = fetch_srtm_elevation(bbox)
        >>> ue5_data = convert_osm_to_ue5(osm_data, bbox, heightmap)
        >>> print(f"Buildings: {len(ue5_data['buildings'])}")
    """
    converter = OSMToUE5Converter(bbox, heightmap, terrain_origin)
    return converter.convert_all(osm_data)
