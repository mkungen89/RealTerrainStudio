"""
OSM Objects List Exporter

Exports OpenStreetMap objects as structured lists for UE5 spawning.
Supports JSON and CSV formats.
"""

import json
import csv
import os
from typing import Dict, List, Tuple, Optional
from pathlib import Path


class OSMExporter:
    """
    Exports OSM objects in UE5-ready format.

    Features:
    - JSON export (complete object data)
    - CSV export (simplified for spreadsheet viewing)
    - Category organization (roads, buildings, POIs, etc.)
    - Position conversion (lat/lon and UE5 coordinates)
    - Metadata inclusion
    """

    def __init__(self):
        """Initialize OSM exporter."""
        pass

    def export_json(
        self,
        ue5_data: Dict,
        output_path: str,
        bbox: Tuple[float, float, float, float],
        terrain_origin: Tuple[float, float, float] = (0, 0, 0)
    ) -> str:
        """
        Export OSM objects as JSON.

        Args:
            ue5_data: Converted UE5 data (from OSMToUE5Converter)
            output_path: Output JSON file path
            bbox: Bounding box
            terrain_origin: UE5 terrain origin

        Returns:
            str: Path to created JSON file

        Example:
            >>> exporter = OSMExporter()
            >>> exporter.export_json(
            ...     ue5_data,
            ...     'osm_objects.json',
            ...     bbox
            ... )
        """
        # Build export structure
        export_data = {
            'metadata': {
                'bbox': {
                    'min_lon': bbox[0],
                    'min_lat': bbox[1],
                    'max_lon': bbox[2],
                    'max_lat': bbox[3]
                },
                'terrain_origin': {
                    'x': terrain_origin[0],
                    'y': terrain_origin[1],
                    'z': terrain_origin[2]
                },
                'counts': {
                    'buildings': len(ue5_data.get('buildings', [])),
                    'roads': len(ue5_data.get('roads', [])),
                    'pois': len(ue5_data.get('pois', [])),
                    'other': len(ue5_data.get('other', []))
                }
            },
            'roads': self._format_roads_json(ue5_data.get('roads', [])),
            'buildings': self._format_buildings_json(ue5_data.get('buildings', [])),
            'pois': self._format_pois_json(ue5_data.get('pois', [])),
            'other': self._format_other_json(ue5_data.get('other', []))
        }

        # Write JSON
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)

        return output_path

    def _format_roads_json(self, roads: List[Dict]) -> List[Dict]:
        """Format roads for JSON export."""
        formatted = []

        for road in roads:
            # Convert spline points to simple [x, y, z] arrays
            points = [
                [p[0], p[1], p[2]]
                for p in road.get('spline_points', [])
            ]

            formatted.append({
                'id': f"way_{road.get('osm_id', 0)}",
                'type': road.get('highway_type', 'unknown'),
                'name': road.get('name', ''),
                'points': points,
                'width': road.get('width', 500),  # cm
                'lanes': road.get('lanes', 2),
                'tags': road.get('tags', {})
            })

        return formatted

    def _format_buildings_json(self, buildings: List[Dict]) -> List[Dict]:
        """Format buildings for JSON export."""
        formatted = []

        for building in buildings:
            # Convert footprint to simple [x, y, z] arrays
            footprint = [
                [p[0], p[1], p[2]]
                for p in building.get('footprint', [])
            ]

            # Position
            pos = building.get('position', (0, 0, 0))

            formatted.append({
                'id': f"way_{building.get('osm_id', 0)}",
                'type': building.get('building_type', 'yes'),
                'position': [pos[0], pos[1], pos[2]],
                'rotation': building.get('rotation', 0.0),
                'footprint': footprint,
                'height': building.get('height', 300),  # cm
                'levels': building.get('levels', 1),
                'tags': building.get('tags', {})
            })

        return formatted

    def _format_pois_json(self, pois: List[Dict]) -> List[Dict]:
        """Format POIs for JSON export."""
        formatted = []

        for poi in pois:
            # Position
            pos = poi.get('position', (0, 0, 0))

            formatted.append({
                'id': f"node_{poi.get('osm_id', 0)}",
                'type': poi.get('amenity', 'unknown'),
                'name': poi.get('name', ''),
                'position': [pos[0], pos[1], pos[2]],
                'tags': poi.get('tags', {})
            })

        return formatted

    def _format_other_json(self, others: List[Dict]) -> List[Dict]:
        """Format other OSM features for JSON export."""
        formatted = []

        for other in others:
            tags = other.get('tags', {})

            formatted.append({
                'id': f"way_{other.get('id', 0)}",
                'tags': tags
            })

        return formatted

    def export_csv(
        self,
        ue5_data: Dict,
        output_dir: str,
        bbox: Tuple[float, float, float, float]
    ) -> Dict[str, str]:
        """
        Export OSM objects as CSV files (one per category).

        Args:
            ue5_data: Converted UE5 data
            output_dir: Output directory
            bbox: Bounding box

        Returns:
            dict: Paths to created CSV files

        Example:
            >>> exporter = OSMExporter()
            >>> files = exporter.export_csv(ue5_data, 'output/', bbox)
            >>> print(files['buildings'])  # 'output/buildings.csv'
        """
        os.makedirs(output_dir, exist_ok=True)

        created_files = {}

        # Export buildings
        if ue5_data.get('buildings'):
            buildings_path = os.path.join(output_dir, 'buildings.csv')
            self._export_buildings_csv(ue5_data['buildings'], buildings_path)
            created_files['buildings'] = buildings_path

        # Export roads
        if ue5_data.get('roads'):
            roads_path = os.path.join(output_dir, 'roads.csv')
            self._export_roads_csv(ue5_data['roads'], roads_path)
            created_files['roads'] = roads_path

        # Export POIs
        if ue5_data.get('pois'):
            pois_path = os.path.join(output_dir, 'pois.csv')
            self._export_pois_csv(ue5_data['pois'], pois_path)
            created_files['pois'] = pois_path

        return created_files

    def _export_buildings_csv(self, buildings: List[Dict], output_path: str):
        """Export buildings to CSV."""
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)

            # Header
            writer.writerow([
                'ID', 'Type', 'X (cm)', 'Y (cm)', 'Z (cm)',
                'Rotation (deg)', 'Height (cm)', 'Levels', 'Name'
            ])

            # Data
            for building in buildings:
                pos = building.get('position', (0, 0, 0))
                tags = building.get('tags', {})

                writer.writerow([
                    f"way_{building.get('osm_id', 0)}",
                    building.get('building_type', 'yes'),
                    pos[0],
                    pos[1],
                    pos[2],
                    building.get('rotation', 0.0),
                    building.get('height', 300),
                    building.get('levels', 1),
                    tags.get('name', '')
                ])

    def _export_roads_csv(self, roads: List[Dict], output_path: str):
        """Export roads to CSV."""
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)

            # Header
            writer.writerow([
                'ID', 'Type', 'Name', 'Width (cm)', 'Lanes', 'Points Count'
            ])

            # Data
            for road in roads:
                writer.writerow([
                    f"way_{road.get('osm_id', 0)}",
                    road.get('highway_type', 'unknown'),
                    road.get('name', ''),
                    road.get('width', 500),
                    road.get('lanes', 2),
                    len(road.get('spline_points', []))
                ])

    def _export_pois_csv(self, pois: List[Dict], output_path: str):
        """Export POIs to CSV."""
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)

            # Header
            writer.writerow([
                'ID', 'Type', 'Name', 'X (cm)', 'Y (cm)', 'Z (cm)'
            ])

            # Data
            for poi in pois:
                pos = poi.get('position', (0, 0, 0))

                writer.writerow([
                    f"node_{poi.get('osm_id', 0)}",
                    poi.get('amenity', 'unknown'),
                    poi.get('name', ''),
                    pos[0],
                    pos[1],
                    pos[2]
                ])

    def export_complete(
        self,
        ue5_data: Dict,
        output_dir: str,
        bbox: Tuple[float, float, float, float],
        terrain_origin: Tuple[float, float, float] = (0, 0, 0),
        format: str = 'both'
    ) -> Dict[str, str]:
        """
        Export complete OSM data in specified format(s).

        Args:
            ue5_data: Converted UE5 data
            output_dir: Output directory
            bbox: Bounding box
            terrain_origin: UE5 terrain origin
            format: 'json', 'csv', or 'both'

        Returns:
            dict: Paths to created files

        Example:
            >>> exporter = OSMExporter()
            >>> files = exporter.export_complete(
            ...     ue5_data,
            ...     'output/',
            ...     bbox,
            ...     format='both'
            ... )
            >>> print(files['json'])  # 'output/osm_objects.json'
            >>> print(files['buildings_csv'])  # 'output/buildings.csv'
        """
        os.makedirs(output_dir, exist_ok=True)

        created_files = {}

        # Export JSON
        if format in ['json', 'both']:
            json_path = os.path.join(output_dir, 'osm_objects.json')
            self.export_json(ue5_data, json_path, bbox, terrain_origin)
            created_files['json'] = json_path

        # Export CSV
        if format in ['csv', 'both']:
            csv_files = self.export_csv(ue5_data, output_dir, bbox)
            for key, path in csv_files.items():
                created_files[f'{key}_csv'] = path

        return created_files

    def create_summary(
        self,
        ue5_data: Dict,
        output_path: str
    ) -> str:
        """
        Create summary statistics file.

        Args:
            ue5_data: Converted UE5 data
            output_path: Output text file path

        Returns:
            str: Path to created summary file
        """
        buildings = ue5_data.get('buildings', [])
        roads = ue5_data.get('roads', [])
        pois = ue5_data.get('pois', [])

        # Count by type
        building_types = {}
        for building in buildings:
            btype = building.get('building_type', 'yes')
            building_types[btype] = building_types.get(btype, 0) + 1

        road_types = {}
        for road in roads:
            rtype = road.get('highway_type', 'unknown')
            road_types[rtype] = road_types.get(rtype, 0) + 1

        poi_types = {}
        for poi in pois:
            ptype = poi.get('amenity', 'unknown')
            poi_types[ptype] = poi_types.get(ptype, 0) + 1

        # Write summary
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("OSM Objects Summary\n")
            f.write("=" * 60 + "\n\n")

            f.write(f"Total Objects: {len(buildings) + len(roads) + len(pois)}\n\n")

            f.write(f"Buildings: {len(buildings)}\n")
            for btype, count in sorted(building_types.items(), key=lambda x: -x[1]):
                f.write(f"  {btype}: {count}\n")
            f.write("\n")

            f.write(f"Roads: {len(roads)}\n")
            for rtype, count in sorted(road_types.items(), key=lambda x: -x[1]):
                f.write(f"  {rtype}: {count}\n")
            f.write("\n")

            f.write(f"POIs: {len(pois)}\n")
            for ptype, count in sorted(poi_types.items(), key=lambda x: -x[1]):
                f.write(f"  {ptype}: {count}\n")

        return output_path


def export_osm_objects(
    ue5_data: Dict,
    output_path: str,
    bbox: Tuple[float, float, float, float],
    format: str = 'json',
    terrain_origin: Tuple[float, float, float] = (0, 0, 0)
) -> str:
    """
    Convenience function to export OSM objects.

    Args:
        ue5_data: Converted UE5 data
        output_path: Output file path (or directory for CSV)
        bbox: Bounding box
        format: 'json' or 'csv'
        terrain_origin: UE5 terrain origin

    Returns:
        str: Path to created file(s)

    Example:
        >>> from data_sources.osm_fetcher import fetch_osm_data
        >>> from data_sources.osm_to_ue5_converter import convert_osm_to_ue5
        >>> from exporters.osm_exporter import export_osm_objects
        >>>
        >>> osm_data = fetch_osm_data(bbox, filters)
        >>> ue5_data = convert_osm_to_ue5(osm_data, bbox, heightmap)
        >>> export_osm_objects(ue5_data, 'osm_objects.json', bbox)
    """
    exporter = OSMExporter()

    if format == 'json':
        return exporter.export_json(ue5_data, output_path, bbox, terrain_origin)
    elif format == 'csv':
        output_dir = output_path if os.path.isdir(output_path) else os.path.dirname(output_path)
        exporter.export_csv(ue5_data, output_dir, bbox)
        return output_dir
    else:
        raise ValueError(f"Unknown format: {format}")
