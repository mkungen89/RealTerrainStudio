# Copyright RealTerrain Studio. All Rights Reserved.

"""
Pytest configuration and fixtures for RealTerrain Studio backend tests.
"""

import pytest
import tempfile
import shutil
from pathlib import Path


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test outputs."""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    # Cleanup after test
    shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def sample_bbox():
    """Sample bounding box for San Francisco area (small for fast tests)."""
    return {
        'min_lon': -122.45,
        'min_lat': 37.75,
        'max_lon': -122.40,
        'max_lat': 37.80
    }


@pytest.fixture
def sample_metadata():
    """Sample metadata for terrain export."""
    return {
        'heightmap': {
            'width': 1024,
            'height': 1024,
            'min_elevation': 0.0,
            'max_elevation': 100.0,
            'pixel_size_x': 30.0,
            'pixel_size_y': 30.0,
            'crs': 'EPSG:4326',
            'bounds': [-122.45, 37.75, -122.40, 37.80]
        },
        'satellite': {
            'width': 2048,
            'height': 2048,
            'format': 'JPEG',
            'source': 'Sentinel-2'
        },
        'export_info': {
            'timestamp': '2025-12-10T12:00:00Z',
            'exporter_version': '1.0.0',
            'coordinate_system': 'EPSG:4326'
        }
    }


@pytest.fixture
def mock_heightmap_data():
    """Generate mock heightmap data (small 64x64 array)."""
    import numpy as np
    # Create a simple gradient heightmap
    x = np.linspace(0, 1, 64)
    y = np.linspace(0, 1, 64)
    X, Y = np.meshgrid(x, y)
    # Simple terrain: gradient + some noise
    heightmap = (X * 50 + Y * 30 + np.random.random((64, 64)) * 5).astype(np.uint16)
    return heightmap
