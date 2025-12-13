"""
OpenStreetMap Data Fetcher

Fetches OSM data with intelligent chunking to handle Overpass API's 50k node limit.
"""

import math
import time
import logging
from typing import Dict, List, Tuple, Optional, Callable
from pathlib import Path
import requests

# Import error handling utilities
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.error_handling import (
    DataFetchError,
    NetworkError,
    ValidationError,
    retry,
    handle_errors,
    validate_bbox,
    handle_network_error
)

# Setup logging
logger = logging.getLogger(__name__)


class OSMFetcher:
    """
    Intelligent OSM data fetcher with automatic chunking.

    Features:
    - Automatic chunking for large areas (50k node Overpass limit)
    - Multiple feature type filtering (roads, buildings, railways, etc.)
    - Rate limiting to be nice to Overpass API
    - Deduplication of overlapping data
    - Progress callbacks
    """

    MAX_NODES = 50_000  # Overpass API limit
    TIMEOUT = 180  # seconds
    RATE_LIMIT_DELAY = 1.0  # seconds between requests

    def __init__(self, overpass_url: str = "https://overpass-api.de/api/interpreter"):
        """
        Initialize OSM fetcher.

        Args:
            overpass_url: Overpass API endpoint URL
        """
        self.overpass_url = overpass_url
        self.chunks_processed = 0
        self.total_chunks = 0
        logger.info(f"OSMFetcher initialized with endpoint: {overpass_url}")

    def fetch_osm_data(
        self,
        bbox: Tuple[float, float, float, float],
        filters: Dict[str, bool],
        progress_callback: Optional[Callable[[int, str], None]] = None
    ) -> Dict:
        """
        Fetch OSM data with automatic chunking.

        Args:
            bbox: Bounding box (min_lon, min_lat, max_lon, max_lat)
            filters: Dict of feature types to fetch (e.g., {'roads': True, 'buildings': True})
            progress_callback: Optional callback(progress_percent, message)

        Returns:
            dict: OSM data with 'nodes', 'ways', 'relations'

        Raises:
            ValidationError: If bbox is invalid
            DataFetchError: If OSM data fetching fails
            NetworkError: If network operations fail

        Example:
            >>> fetcher = OSMFetcher()
            >>> bbox = (-122.5, 37.7, -122.4, 37.8)
            >>> data = fetcher.fetch_osm_data(
            ...     bbox,
            ...     {'roads': True, 'buildings': True}
            ... )
            >>> print(f"Fetched {len(data['ways'])} ways")
        """
        logger.info(f"Fetching OSM data for bbox={bbox}, filters={filters}")

        # Validate inputs
        try:
            bbox = validate_bbox(bbox)
        except ValidationError as e:
            logger.error(f"Invalid bbox: {e}")
            raise

        if not filters or not any(filters.values()):
            raise ValidationError(
                "No feature filters enabled",
                user_message="Please select at least one feature type to fetch (roads, buildings, etc.)"
            )

        try:
            # 1. Estimate data size
            estimated_nodes = self.estimate_node_count(bbox, filters)
            logger.info(f"Estimated nodes: {estimated_nodes:,}")

            # 2. Calculate chunks if needed
            if estimated_nodes > self.MAX_NODES:
                chunks = self.create_chunks(bbox, estimated_nodes)
                logger.info(f"Area too large, splitting into {len(chunks)} chunks")
            else:
                chunks = [bbox]
                logger.info("Area small enough for single query")

            self.total_chunks = len(chunks)
            self.chunks_processed = 0

            # 3. Fetch each chunk
            all_data = {
                'nodes': [],
                'ways': [],
                'relations': []
            }

            failed_chunks = []

            for i, chunk_bbox in enumerate(chunks):
                logger.info(f"Fetching chunk {i+1}/{len(chunks)}")

                try:
                    chunk_data = self.fetch_chunk(chunk_bbox, filters)

                    # Merge data
                    all_data['nodes'].extend(chunk_data.get('nodes', []))
                    all_data['ways'].extend(chunk_data.get('ways', []))
                    all_data['relations'].extend(chunk_data.get('relations', []))

                    logger.debug(f"Chunk {i+1}: {len(chunk_data['nodes'])} nodes, "
                                f"{len(chunk_data['ways'])} ways, "
                                f"{len(chunk_data['relations'])} relations")

                    # Progress callback
                    if progress_callback:
                        progress = int((i + 1) / len(chunks) * 100)
                        progress_callback(progress, f"Chunk {i+1}/{len(chunks)}")

                    self.chunks_processed = i + 1

                    # Rate limiting (be nice to Overpass API)
                    if i < len(chunks) - 1:
                        time.sleep(self.RATE_LIMIT_DELAY)

                except NetworkError as e:
                    logger.warning(f"Network error fetching chunk {i+1}: {e}")
                    failed_chunks.append((i+1, str(e)))
                    # Continue with other chunks for graceful degradation
                    continue

                except Exception as e:
                    logger.error(f"Unexpected error fetching chunk {i+1}: {e}")
                    failed_chunks.append((i+1, str(e)))
                    continue

            # Check if we got any data
            total_items = (len(all_data['nodes']) +
                          len(all_data['ways']) +
                          len(all_data['relations']))

            if total_items == 0:
                logger.error(f"Failed to fetch any OSM data. All {len(chunks)} chunks failed.")
                raise DataFetchError(
                    f"Failed to fetch OSM data for area. All chunks failed.",
                    user_message=(
                        "Could not download OpenStreetMap data. Possible reasons:\n"
                        "• Overpass API is temporarily unavailable\n"
                        "• Network connection issues\n"
                        "• No OSM data available for this area\n\n"
                        "Try again in a few minutes or select a different area."
                    )
                )

            if failed_chunks:
                logger.warning(f"{len(failed_chunks)} chunk(s) failed, continuing with partial data")
                logger.warning(f"Failed chunks: {failed_chunks}")

            # 4. Remove duplicates (nodes/ways on chunk boundaries)
            logger.info("Removing duplicates...")
            deduplicated = self.remove_duplicates(all_data)

            logger.info(f"Successfully fetched OSM data: {len(deduplicated['nodes'])} nodes, "
                       f"{len(deduplicated['ways'])} ways, "
                       f"{len(deduplicated['relations'])} relations")

            return deduplicated

        except (ValidationError, DataFetchError, NetworkError):
            # Re-raise our custom errors
            raise

        except Exception as e:
            logger.exception(f"Unexpected error fetching OSM data: {e}")
            raise DataFetchError(
                f"Unexpected error fetching OSM data: {e}",
                user_message=f"Failed to fetch OpenStreetMap data: {str(e)}"
            )

    def estimate_node_count(
        self,
        bbox: Tuple[float, float, float, float],
        filters: Dict[str, bool]
    ) -> int:
        """
        Estimate number of nodes in area based on size and feature density.

        Args:
            bbox: Bounding box
            filters: Feature types to fetch

        Returns:
            int: Estimated node count
        """
        area_km2 = self.calculate_area(bbox)

        # Density estimates (nodes per km²) based on typical urban areas
        DENSITY = {
            'roads': 500,
            'buildings': 2000,
            'power_lines': 300,
            'railways': 100,
            'water': 200,
            'poi': 500,
            'street_furniture': 1000,
            'landuse': 300,
            'natural': 200,
            'barriers': 400
        }

        estimated = 0
        for feature_type, enabled in filters.items():
            if enabled and feature_type in DENSITY:
                estimated += DENSITY[feature_type] * area_km2

        # Add 30% buffer for safety
        estimated = int(estimated * 1.3)

        logger.info(f"Area: {area_km2:.2f} km², Estimated nodes: {estimated:,}")

        return estimated

    def calculate_area(self, bbox: Tuple[float, float, float, float]) -> float:
        """
        Calculate area of bounding box in km².

        Args:
            bbox: (min_lon, min_lat, max_lon, max_lat)

        Returns:
            float: Area in km²
        """
        min_lon, min_lat, max_lon, max_lat = bbox

        # Calculate at center latitude
        lat_center = (min_lat + max_lat) / 2

        # Meters per degree
        meters_per_degree_lon = 111320 * math.cos(math.radians(lat_center))
        meters_per_degree_lat = 110540

        # Calculate dimensions
        width_m = (max_lon - min_lon) * meters_per_degree_lon
        height_m = (max_lat - min_lat) * meters_per_degree_lat

        # Area in km²
        area_km2 = (width_m * height_m) / 1_000_000

        return area_km2

    def create_chunks(
        self,
        bbox: Tuple[float, float, float, float],
        estimated_nodes: int
    ) -> List[Tuple[float, float, float, float]]:
        """
        Split bounding box into smaller chunks.

        Args:
            bbox: Original bounding box
            estimated_nodes: Estimated total nodes

        Returns:
            list: List of chunk bboxes
        """
        min_lon, min_lat, max_lon, max_lat = bbox

        # Calculate how many chunks needed
        chunks_needed = math.ceil(estimated_nodes / self.MAX_NODES)

        # Split in grid (e.g., 2x2, 3x3, 4x4)
        grid_size = math.ceil(math.sqrt(chunks_needed))

        # Calculate step sizes
        lon_step = (max_lon - min_lon) / grid_size
        lat_step = (max_lat - min_lat) / grid_size

        chunks = []
        for i in range(grid_size):
            for j in range(grid_size):
                chunk_bbox = (
                    min_lon + j * lon_step,  # min_lon
                    min_lat + i * lat_step,  # min_lat
                    min_lon + (j + 1) * lon_step,  # max_lon
                    min_lat + (i + 1) * lat_step   # max_lat
                )
                chunks.append(chunk_bbox)

        logger.info(f"Split into {grid_size}×{grid_size} grid = {len(chunks)} chunks")

        return chunks

    @retry(
        max_attempts=3,
        delay=2.0,
        backoff=2.0,
        exceptions=(NetworkError,)
    )
    def fetch_chunk(
        self,
        bbox: Tuple[float, float, float, float],
        filters: Dict[str, bool]
    ) -> Dict:
        """
        Fetch single chunk from Overpass API with automatic retry.

        Args:
            bbox: Chunk bounding box
            filters: Feature filters

        Returns:
            dict: OSM data for this chunk

        Raises:
            NetworkError: If API request fails after retries
            DataFetchError: If response parsing fails
        """
        query = self.build_overpass_query(bbox, filters)
        logger.debug(f"Overpass query for chunk: {len(query)} chars")

        try:
            # Use error handling wrapper for network operations
            response = handle_network_error(
                requests.post,
                self.overpass_url,
                data={'data': query},
                timeout=self.TIMEOUT
            )
            response.raise_for_status()

            # Parse JSON response
            try:
                data = response.json()
            except ValueError as e:
                raise DataFetchError(
                    f"Invalid JSON response from Overpass API: {e}",
                    user_message="Received invalid data from OpenStreetMap. Try again."
                )

            # Parse and return OSM data
            return self.parse_overpass_response(data)

        except requests.Timeout:
            logger.error(f"Overpass API timeout after {self.TIMEOUT}s")
            raise NetworkError(
                f"Overpass API request timeout after {self.TIMEOUT}s",
                user_message="OpenStreetMap server is taking too long to respond. Try a smaller area or try again later."
            )

        except requests.HTTPError as e:
            status_code = e.response.status_code if e.response else 'unknown'
            logger.error(f"Overpass API HTTP error {status_code}: {e}")

            if status_code == 429:
                raise NetworkError(
                    f"Overpass API rate limit exceeded: {e}",
                    user_message="Too many requests to OpenStreetMap. Please wait a minute and try again."
                )
            elif status_code >= 500:
                raise NetworkError(
                    f"Overpass API server error {status_code}: {e}",
                    user_message="OpenStreetMap server is temporarily unavailable. Try again later."
                )
            else:
                raise NetworkError(
                    f"Overpass API error {status_code}: {e}",
                    user_message=f"OpenStreetMap request failed (error {status_code}). Try again."
                )

        except NetworkError:
            # Re-raise for retry decorator
            raise

        except requests.RequestException as e:
            logger.error(f"Overpass API request error: {e}")
            raise NetworkError(
                f"Failed to fetch OSM data from Overpass API: {e}",
                user_message="Network error connecting to OpenStreetMap. Check your connection."
            )

        except Exception as e:
            logger.error(f"Unexpected error in fetch_chunk: {e}")
            raise DataFetchError(
                f"Unexpected error fetching OSM chunk: {e}",
                user_message=f"Failed to fetch OpenStreetMap data: {str(e)}"
            )

    def build_overpass_query(
        self,
        bbox: Tuple[float, float, float, float],
        filters: Dict[str, bool]
    ) -> str:
        """
        Build Overpass QL query based on filters.

        Args:
            bbox: Bounding box
            filters: Feature filters

        Returns:
            str: Overpass QL query
        """
        min_lon, min_lat, max_lon, max_lat = bbox
        bbox_str = f"{min_lat},{min_lon},{max_lat},{max_lon}"

        # Start query
        query = f"[out:json][timeout:{self.TIMEOUT}];\n(\n"

        # Add filters based on enabled features
        if filters.get('roads'):
            query += f'  way["highway"]({bbox_str});\n'

        if filters.get('buildings'):
            query += f'  way["building"]({bbox_str});\n'
            query += f'  relation["building"]({bbox_str});\n'

        if filters.get('railways'):
            query += f'  way["railway"]({bbox_str});\n'

        if filters.get('power_lines'):
            query += f'  way["power"="line"]({bbox_str});\n'
            query += f'  node["power"="tower"]({bbox_str});\n'
            query += f'  node["power"="pole"]({bbox_str});\n'

        if filters.get('water'):
            query += f'  way["natural"="water"]({bbox_str});\n'
            query += f'  way["waterway"]({bbox_str});\n'
            query += f'  relation["natural"="water"]({bbox_str});\n'

        if filters.get('poi'):
            query += f'  node["amenity"]({bbox_str});\n'
            query += f'  way["amenity"]({bbox_str});\n'

        if filters.get('street_furniture'):
            query += f'  node["highway"="street_lamp"]({bbox_str});\n'
            query += f'  node["amenity"="bench"]({bbox_str});\n'
            query += f'  node["amenity"="waste_basket"]({bbox_str});\n'
            query += f'  node["highway"="traffic_signals"]({bbox_str});\n'

        if filters.get('landuse'):
            query += f'  way["landuse"]({bbox_str});\n'
            query += f'  relation["landuse"]({bbox_str});\n'

        if filters.get('natural'):
            query += f'  way["natural"]({bbox_str});\n'
            query += f'  relation["natural"]({bbox_str});\n'

        if filters.get('barriers'):
            query += f'  way["barrier"]({bbox_str});\n'
            query += f'  node["barrier"]({bbox_str});\n'

        # End query - request geometry to be included
        query += ");\nout geom;"

        return query

    def parse_overpass_response(self, data: Dict) -> Dict:
        """
        Parse Overpass API JSON response.

        Args:
            data: Raw Overpass JSON response

        Returns:
            dict: Parsed OSM data
        """
        elements = data.get('elements', [])

        parsed = {
            'nodes': [],
            'ways': [],
            'relations': []
        }

        for element in elements:
            elem_type = element.get('type')

            if elem_type == 'node':
                parsed['nodes'].append({
                    'id': element.get('id'),
                    'lat': element.get('lat'),
                    'lon': element.get('lon'),
                    'tags': element.get('tags', {})
                })

            elif elem_type == 'way':
                # Extract geometry if available
                geometry = []
                if 'geometry' in element:
                    geometry = [
                        {'lat': pt['lat'], 'lon': pt['lon']}
                        for pt in element['geometry']
                    ]

                parsed['ways'].append({
                    'id': element.get('id'),
                    'nodes': element.get('nodes', []),
                    'geometry': geometry,
                    'tags': element.get('tags', {})
                })

            elif elem_type == 'relation':
                parsed['relations'].append({
                    'id': element.get('id'),
                    'members': element.get('members', []),
                    'tags': element.get('tags', {})
                })

        return parsed

    def remove_duplicates(self, data: Dict) -> Dict:
        """
        Remove duplicate nodes/ways/relations from overlapping chunks.

        Args:
            data: OSM data with potential duplicates

        Returns:
            dict: Deduplicated OSM data
        """
        # Use sets to track unique IDs
        seen_nodes = set()
        seen_ways = set()
        seen_relations = set()

        unique_data = {
            'nodes': [],
            'ways': [],
            'relations': []
        }

        # Deduplicate nodes
        for node in data['nodes']:
            node_id = node.get('id')
            if node_id and node_id not in seen_nodes:
                unique_data['nodes'].append(node)
                seen_nodes.add(node_id)

        # Deduplicate ways
        for way in data['ways']:
            way_id = way.get('id')
            if way_id and way_id not in seen_ways:
                unique_data['ways'].append(way)
                seen_ways.add(way_id)

        # Deduplicate relations
        for relation in data['relations']:
            relation_id = relation.get('id')
            if relation_id and relation_id not in seen_relations:
                unique_data['relations'].append(relation)
                seen_relations.add(relation_id)

        # Log deduplication stats
        nodes_removed = len(data['nodes']) - len(unique_data['nodes'])
        ways_removed = len(data['ways']) - len(unique_data['ways'])
        relations_removed = len(data['relations']) - len(unique_data['relations'])

        if nodes_removed > 0:
            logger.info(f"Removed {nodes_removed} duplicate nodes")
        if ways_removed > 0:
            logger.info(f"Removed {ways_removed} duplicate ways")
        if relations_removed > 0:
            logger.info(f"Removed {relations_removed} duplicate relations")

        return unique_data

    def get_statistics(self, data: Dict) -> Dict:
        """
        Get statistics about fetched OSM data.

        Args:
            data: OSM data

        Returns:
            dict: Statistics
        """
        stats = {
            'total_nodes': len(data['nodes']),
            'total_ways': len(data['ways']),
            'total_relations': len(data['relations']),
            'feature_counts': {}
        }

        # Count features by type
        for way in data['ways']:
            tags = way.get('tags', {})

            # Roads
            if 'highway' in tags:
                highway_type = tags['highway']
                key = f'highway:{highway_type}'
                stats['feature_counts'][key] = stats['feature_counts'].get(key, 0) + 1

            # Buildings
            if 'building' in tags:
                stats['feature_counts']['building'] = stats['feature_counts'].get('building', 0) + 1

            # Railways
            if 'railway' in tags:
                stats['feature_counts']['railway'] = stats['feature_counts'].get('railway', 0) + 1

            # Water
            if 'waterway' in tags or tags.get('natural') == 'water':
                stats['feature_counts']['water'] = stats['feature_counts'].get('water', 0) + 1

        # Count POI nodes
        poi_count = 0
        for node in data['nodes']:
            if 'amenity' in node.get('tags', {}):
                poi_count += 1

        if poi_count > 0:
            stats['feature_counts']['poi'] = poi_count

        return stats


def fetch_osm_data(
    bbox: Tuple[float, float, float, float],
    filters: Dict[str, bool],
    progress_callback: Optional[Callable[[int, str], None]] = None
) -> Dict:
    """
    Convenience function to fetch OSM data.

    Args:
        bbox: Bounding box (min_lon, min_lat, max_lon, max_lat)
        filters: Feature filters
        progress_callback: Optional progress callback

    Returns:
        dict: OSM data

    Example:
        >>> bbox = (-122.5, 37.7, -122.4, 37.8)
        >>> data = fetch_osm_data(
        ...     bbox,
        ...     {'roads': True, 'buildings': True, 'poi': True}
        ... )
        >>> print(f"Fetched {len(data['ways'])} ways")
    """
    fetcher = OSMFetcher()
    return fetcher.fetch_osm_data(bbox, filters, progress_callback)
