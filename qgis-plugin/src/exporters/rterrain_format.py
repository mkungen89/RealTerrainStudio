"""
.rterrain Package Format

Custom container format for RealTerrain Studio exports.
Single file containing heightmap, textures, materials, OSM data, and metadata.

Extension: .rterrain
MIME type: application/vnd.realterrain.package
"""

import struct
import json
import zlib
import hashlib
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, BinaryIO
import numpy as np


class RTerrainFormat:
    """
    RealTerrain Package Format writer and reader.

    File structure:
    - Magic number (4 bytes): b'RTER'
    - Version (4 bytes): uint32
    - Header size (4 bytes): uint32
    - Header (JSON metadata, variable size)
    - Data blocks (multiple, each with size + compressed data)
    - Checksum (32 bytes): SHA256
    """

    MAGIC_NUMBER = b'RTER'
    VERSION = 1

    def __init__(self):
        """Initialize the RTerrainFormat handler."""
        self.header = {}
        self.data_blocks = {}
        self._data_block_index = {}

    def create_package(
        self,
        output_path: str,
        project_info: Dict[str, Any],
        heightmap: Optional[np.ndarray] = None,
        satellite: Optional[bytes] = None,
        materials: Optional[Dict[str, np.ndarray]] = None,
        osm_data: Optional[Dict] = None,
        vegetation: Optional[Dict] = None,
        tactical: Optional[Dict] = None,
        profile_config: Optional[Dict] = None
    ):
        """
        Create a .rterrain package file.

        Args:
            output_path: Path to output .rterrain file
            project_info: Project metadata (name, bbox, resolution, etc.)
            heightmap: Elevation data as numpy array
            satellite: Satellite imagery (JPEG bytes)
            materials: Dict of material masks {name: numpy array}
            osm_data: OSM objects data
            vegetation: Vegetation spawn data
            tactical: Tactical analysis data (MILSIM)
            profile_config: Game profile configuration
        """
        # Create header
        self.header = self._create_header(
            project_info,
            heightmap,
            satellite,
            materials,
            osm_data,
            vegetation,
            tactical
        )

        with open(output_path, 'wb') as f:
            # 1. Write magic number
            f.write(self.MAGIC_NUMBER)

            # 2. Write version
            f.write(struct.pack('<I', self.VERSION))

            # 3. Write header
            header_json = json.dumps(self.header, indent=2)
            header_bytes = header_json.encode('utf-8')
            f.write(struct.pack('<I', len(header_bytes)))
            f.write(header_bytes)

            # 4. Write data blocks
            if heightmap is not None:
                self._write_data_block(f, 'heightmap', heightmap)

            if satellite is not None:
                self._write_data_block(f, 'satellite', satellite)

            if materials is not None:
                for name, mask in materials.items():
                    self._write_data_block(f, f'material_{name}', mask)

            if osm_data is not None:
                self._write_data_block(f, 'osm_data', osm_data)

            if vegetation is not None:
                self._write_data_block(f, 'vegetation', vegetation)

            if tactical is not None:
                self._write_data_block(f, 'tactical', tactical)

            if profile_config is not None:
                self._write_data_block(f, 'profile', profile_config)

            # 5. Write data block index
            index_json = json.dumps(self._data_block_index)
            index_bytes = index_json.encode('utf-8')
            f.write(struct.pack('<I', len(index_bytes)))
            f.write(index_bytes)

            # 6. Write checksum
            self._write_checksum(f)

    def _create_header(
        self,
        project_info: Dict,
        heightmap: Optional[np.ndarray],
        satellite: Optional[bytes],
        materials: Optional[Dict],
        osm_data: Optional[Dict],
        vegetation: Optional[Dict],
        tactical: Optional[Dict]
    ) -> Dict:
        """Create metadata header."""
        header = {
            "format": "RealTerrain Package",
            "version": self.VERSION,
            "created": datetime.now().isoformat(),
            "plugin_version": "1.0.0",
            "project": {
                "name": project_info.get('name', 'Unnamed'),
                "profile": project_info.get('profile', 'custom'),
                "location": project_info.get('location', 'Unknown'),
                "bbox": project_info.get('bbox', [0, 0, 0, 0]),
                "area_km2": project_info.get('area_km2', 0)
            },
            "terrain": {
                "resolution_m": project_info.get('resolution', 30),
                "coordinate_system": "WGS84"
            },
            "content": {},
            "ue5": {
                "recommended_lod_levels": 5,
                "nanite_recommended": False
            },
            "data_blocks": []
        }

        # Add heightmap info
        if heightmap is not None:
            header["terrain"]["heightmap_size"] = list(heightmap.shape)
            header["terrain"]["min_elevation"] = float(np.nanmin(heightmap))
            header["terrain"]["max_elevation"] = float(np.nanmax(heightmap))
            header["content"]["heightmap"] = True
            header["data_blocks"].append("heightmap")

        # Add satellite info
        if satellite is not None:
            header["textures"] = {
                "satellite_format": "JPEG",
                "satellite_size_bytes": len(satellite),
                "compression": "high"
            }
            header["content"]["satellite"] = True
            header["data_blocks"].append("satellite")

        # Add materials info
        if materials is not None:
            header["textures"]["material_layers"] = list(materials.keys())
            header["content"]["materials"] = True
            for name in materials.keys():
                header["data_blocks"].append(f"material_{name}")

        # Add OSM info
        if osm_data is not None:
            header["content"]["osm_objects"] = len(osm_data.get('objects', []))
            header["data_blocks"].append("osm_data")

        # Add vegetation info
        if vegetation is not None:
            header["content"]["vegetation_spawns"] = len(vegetation.get('spawns', []))
            header["data_blocks"].append("vegetation")

        # Add tactical info
        if tactical is not None:
            header["content"]["tactical_analysis"] = True
            header["data_blocks"].append("tactical")

        return header

    def _write_data_block(self, f: BinaryIO, block_name: str, data: Any):
        """Write a compressed data block."""
        start_pos = f.tell()

        # Prepare data for compression
        if isinstance(data, np.ndarray):
            # Numpy array - store as bytes
            data_bytes = data.tobytes()
            data_type = 'numpy'
            data_dtype = str(data.dtype)
            data_shape = list(data.shape)
        elif isinstance(data, bytes):
            # Already bytes (e.g., JPEG)
            data_bytes = data
            data_type = 'bytes'
            data_dtype = None
            data_shape = None
        else:
            # JSON-serializable (dict, list, etc.)
            data_bytes = json.dumps(data).encode('utf-8')
            data_type = 'json'
            data_dtype = None
            data_shape = None

        # Compress
        compressed = zlib.compress(data_bytes, level=9)

        # Create block header
        block_header = {
            'name': block_name,
            'type': data_type,
            'dtype': data_dtype,
            'shape': data_shape,
            'uncompressed_size': len(data_bytes),
            'compressed_size': len(compressed),
            'compression': 'zlib',
            'checksum': hashlib.md5(compressed).hexdigest()
        }

        # Write block header
        block_header_bytes = json.dumps(block_header).encode('utf-8')
        f.write(struct.pack('<I', len(block_header_bytes)))
        f.write(block_header_bytes)

        # Write compressed data
        f.write(compressed)

        # Record in index
        self._data_block_index[block_name] = {
            'offset': start_pos,
            'size': f.tell() - start_pos,
            'type': data_type,
            'compressed_size': len(compressed),
            'uncompressed_size': len(data_bytes)
        }

    def _write_checksum(self, f: BinaryIO):
        """Write file checksum."""
        # Get current position
        end_pos = f.tell()

        # Seek to beginning and calculate checksum
        f.seek(0)
        hasher = hashlib.sha256()

        while f.tell() < end_pos:
            chunk = f.read(8192)
            hasher.update(chunk)

        checksum = hasher.digest()

        # Write checksum at end
        f.seek(end_pos)
        f.write(checksum)

    def read_package(self, rterrain_path: str) -> 'RTerrainFormat':
        """
        Read a .rterrain package file.

        Args:
            rterrain_path: Path to .rterrain file

        Returns:
            RTerrainFormat: Self with loaded data

        Raises:
            ValueError: If file is invalid or corrupted
        """
        with open(rterrain_path, 'rb') as f:
            # 1. Verify magic number
            magic = f.read(4)
            if magic != self.MAGIC_NUMBER:
                raise ValueError(f"Not a valid .rterrain file! Got magic: {magic}")

            # 2. Read version
            version = struct.unpack('<I', f.read(4))[0]
            if version != self.VERSION:
                raise ValueError(f"Unsupported version: {version} (expected {self.VERSION})")

            # 3. Read header
            header_size = struct.unpack('<I', f.read(4))[0]
            header_bytes = f.read(header_size)
            self.header = json.loads(header_bytes.decode('utf-8'))

            # 4. Read data blocks
            file_size = os.path.getsize(rterrain_path)

            # Read until we hit the index (we'll know by size)
            while f.tell() < file_size - 32:  # Leave room for checksum
                try:
                    # Try to read block header size
                    pos_before = f.tell()
                    block_header_size_bytes = f.read(4)

                    if len(block_header_size_bytes) < 4:
                        break

                    block_header_size = struct.unpack('<I', block_header_size_bytes)[0]

                    # Check if this might be the index
                    if block_header_size > 100000:  # Unreasonably large for a block header
                        f.seek(pos_before)
                        break

                    # Read block header
                    block_header_bytes = f.read(block_header_size)
                    block_header = json.loads(block_header_bytes.decode('utf-8'))

                    # Read compressed data
                    compressed = f.read(block_header['compressed_size'])

                    # Verify checksum
                    checksum = hashlib.md5(compressed).hexdigest()
                    if checksum != block_header['checksum']:
                        raise ValueError(f"Checksum mismatch for block {block_header['name']}")

                    # Decompress
                    data_bytes = zlib.decompress(compressed)

                    # Convert back to original type
                    if block_header['type'] == 'numpy':
                        data = np.frombuffer(
                            data_bytes,
                            dtype=block_header['dtype']
                        ).reshape(block_header['shape'])
                    elif block_header['type'] == 'json':
                        data = json.loads(data_bytes.decode('utf-8'))
                    else:  # bytes
                        data = data_bytes

                    self.data_blocks[block_header['name']] = data

                except Exception as e:
                    # Probably reached index or checksum
                    break

            # Note: We skip reading the index since we've already read the blocks
            # The index is mainly for the UE5 plugin to quickly locate blocks

        return self

    def get_heightmap(self) -> Optional[np.ndarray]:
        """Get heightmap data."""
        return self.data_blocks.get('heightmap')

    def get_satellite(self) -> Optional[bytes]:
        """Get satellite image data."""
        return self.data_blocks.get('satellite')

    def get_material(self, name: str) -> Optional[np.ndarray]:
        """Get material mask by name."""
        return self.data_blocks.get(f'material_{name}')

    def get_all_materials(self) -> Dict[str, np.ndarray]:
        """Get all material masks."""
        materials = {}
        for key, value in self.data_blocks.items():
            if key.startswith('material_'):
                material_name = key[9:]  # Remove 'material_' prefix
                materials[material_name] = value
        return materials

    def get_osm_data(self) -> Optional[Dict]:
        """Get OSM objects data."""
        return self.data_blocks.get('osm_data')

    def get_vegetation(self) -> Optional[Dict]:
        """Get vegetation spawn data."""
        return self.data_blocks.get('vegetation')

    def get_tactical(self) -> Optional[Dict]:
        """Get tactical analysis data."""
        return self.data_blocks.get('tactical')

    def get_metadata(self) -> Dict:
        """Get all metadata from header."""
        return self.header

    def list_data_blocks(self) -> list:
        """List all available data blocks."""
        return list(self.data_blocks.keys())


def create_rterrain_package(
    output_path: str,
    project_name: str,
    bbox: tuple,
    heightmap: np.ndarray,
    **kwargs
) -> str:
    """
    Convenience function to create a .rterrain package.

    Args:
        output_path: Output file path
        project_name: Name of the project
        bbox: Bounding box (min_lon, min_lat, max_lon, max_lat)
        heightmap: Elevation data as numpy array
        **kwargs: Additional data (satellite, materials, osm_data, etc.)

    Returns:
        str: Path to created .rterrain file

    Example:
        >>> heightmap = fetch_srtm_elevation(bbox)
        >>> create_rterrain_package(
        ...     'terrain.rterrain',
        ...     'San Francisco',
        ...     (-122.5, 37.7, -122.4, 37.8),
        ...     heightmap,
        ...     satellite=satellite_jpeg,
        ...     materials={'grass': grass_mask, 'rock': rock_mask}
        ... )
    """
    rterrain = RTerrainFormat()

    # Calculate area
    min_lon, min_lat, max_lon, max_lat = bbox
    width_km = abs(max_lon - min_lon) * 111 * np.cos(np.radians((min_lat + max_lat) / 2))
    height_km = abs(max_lat - min_lat) * 111
    area_km2 = width_km * height_km

    project_info = {
        'name': project_name,
        'bbox': bbox,
        'area_km2': round(area_km2, 2),
        'profile': kwargs.get('profile', 'custom'),
        'location': kwargs.get('location', project_name),
        'resolution': kwargs.get('resolution', 30)
    }

    rterrain.create_package(
        output_path,
        project_info,
        heightmap=heightmap,
        satellite=kwargs.get('satellite'),
        materials=kwargs.get('materials'),
        osm_data=kwargs.get('osm_data'),
        vegetation=kwargs.get('vegetation'),
        tactical=kwargs.get('tactical'),
        profile_config=kwargs.get('profile_config')
    )

    return output_path


def read_rterrain_package(rterrain_path: str) -> RTerrainFormat:
    """
    Convenience function to read a .rterrain package.

    Args:
        rterrain_path: Path to .rterrain file

    Returns:
        RTerrainFormat: Loaded package

    Example:
        >>> package = read_rterrain_package('terrain.rterrain')
        >>> heightmap = package.get_heightmap()
        >>> metadata = package.get_metadata()
        >>> print(f"Project: {metadata['project']['name']}")
    """
    rterrain = RTerrainFormat()
    return rterrain.read_package(rterrain_path)
