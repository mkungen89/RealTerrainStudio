"""
Test script for .rterrain export and heightmap exporter.

Run from qgis-plugin directory:
    python test_rterrain_export.py
"""

import sys
import os
import numpy as np

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from exporters.rterrain_format import RTerrainFormat, create_rterrain_package, read_rterrain_package
from exporters.heightmap_exporter import HeightmapExporter, export_heightmap


def test_rterrain_creation():
    """Test creating a .rterrain package."""
    print("\n" + "="*60)
    print("Test: .rterrain Package Creation")
    print("="*60)

    # Create test data
    heightmap = np.random.rand(512, 512).astype(np.float32) * 1000
    bbox = (-122.5, 37.7, -122.4, 37.8)

    # Create package
    output_path = 'test_terrain.rterrain'

    try:
        result_path = create_rterrain_package(
            output_path,
            'Test Terrain',
            bbox,
            heightmap,
            profile='military_simulation',
            location='San Francisco',
            resolution=30
        )

        if os.path.exists(result_path):
            size = os.path.getsize(result_path)
            print(f"  ✅ Package created: {result_path}")
            print(f"  Size: {size / 1024:.2f} KB")

            # Clean up
            os.remove(result_path)
            return True
        else:
            print("  ❌ Package not created")
            return False

    except Exception as e:
        print(f"  ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_rterrain_read_write():
    """Test writing and reading back a .rterrain package."""
    print("\n" + "="*60)
    print("Test: .rterrain Read/Write")
    print("="*60)

    # Create test data
    heightmap = np.random.rand(256, 256).astype(np.float32) * 1000
    bbox = (-122.5, 37.7, -122.4, 37.8)

    # Create some material masks
    materials = {
        'grass': (np.random.rand(256, 256) > 0.5).astype(np.uint8) * 255,
        'rock': (np.random.rand(256, 256) > 0.7).astype(np.uint8) * 255,
        'dirt': (np.random.rand(256, 256) > 0.6).astype(np.uint8) * 255
    }

    # Create OSM data
    osm_data = {
        'objects': [
            {'type': 'road', 'coords': [[0, 0], [1, 1]]},
            {'type': 'building', 'coords': [[2, 2], [3, 3]]}
        ]
    }

    output_path = 'test_full.rterrain'

    try:
        # Write package
        print("\nWriting package...")
        create_rterrain_package(
            output_path,
            'Full Test',
            bbox,
            heightmap,
            materials=materials,
            osm_data=osm_data,
            profile='open_world'
        )

        size_written = os.path.getsize(output_path)
        print(f"  Written: {size_written / 1024:.2f} KB")

        # Read package back
        print("\nReading package...")
        package = read_rterrain_package(output_path)

        # Verify data
        print("\nVerifying data...")

        # Check heightmap
        loaded_heightmap = package.get_heightmap()
        if loaded_heightmap is not None and np.allclose(heightmap, loaded_heightmap):
            print("  ✅ Heightmap matches")
        else:
            print("  ❌ Heightmap mismatch")
            return False

        # Check materials
        loaded_materials = package.get_all_materials()
        if len(loaded_materials) == len(materials):
            print(f"  ✅ Materials count matches ({len(materials)})")
        else:
            print(f"  ❌ Materials count mismatch: {len(loaded_materials)} vs {len(materials)}")
            return False

        # Check OSM data
        loaded_osm = package.get_osm_data()
        if loaded_osm is not None and len(loaded_osm['objects']) == 2:
            print("  ✅ OSM data matches")
        else:
            print("  ❌ OSM data mismatch")
            return False

        # Check metadata
        metadata = package.get_metadata()
        print(f"\nMetadata:")
        print(f"  Project: {metadata['project']['name']}")
        print(f"  Profile: {metadata['project']['profile']}")
        print(f"  Blocks: {len(package.list_data_blocks())}")

        # Clean up
        os.remove(output_path)

        print("\n✅ Read/Write test passed!")
        return True

    except Exception as e:
        print(f"  ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        if os.path.exists(output_path):
            os.remove(output_path)
        return False


def test_heightmap_exporter():
    """Test heightmap exporter."""
    print("\n" + "="*60)
    print("Test: Heightmap Exporter")
    print("="*60)

    exporter = HeightmapExporter()

    # Create test elevation
    elevation = np.random.rand(200, 200).astype(np.float32) * 1000
    elevation[50:60, 50:60] = np.nan  # Add some NaN

    bbox = (-122.5, 37.7, -122.4, 37.8)

    try:
        # Test .rterrain export
        print("\nExporting to .rterrain...")
        rterrain_path = exporter.export_rterrain(
            elevation,
            'test_export.rterrain',
            'Test Export',
            bbox,
            target_size=(512, 512),
            fill_nodata=True,
            smooth=True
        )

        if os.path.exists(rterrain_path):
            size = os.path.getsize(rterrain_path)
            print(f"  ✅ .rterrain exported ({size / 1024:.2f} KB)")
            os.remove(rterrain_path)
        else:
            print("  ❌ .rterrain not created")
            return False

        # Test PNG16 export
        print("\nExporting to PNG16...")
        png_path = exporter.export_png16(
            elevation,
            'test_heightmap.png',
            target_size=(512, 512),
            fill_nodata=True
        )

        if os.path.exists(png_path):
            size = os.path.getsize(png_path)
            print(f"  ✅ PNG16 exported ({size / 1024:.2f} KB)")
            os.remove(png_path)
        else:
            print("  ❌ PNG16 not created")
            return False

        # Test statistics
        print("\nGetting statistics...")
        stats = exporter.get_statistics(elevation)
        print(f"  Min: {stats['min']:.1f}m")
        print(f"  Max: {stats['max']:.1f}m")
        print(f"  Range: {stats['range']:.1f}m")
        print(f"  Valid: {stats['valid_percentage']:.1f}%")

        print("\n✅ Heightmap exporter test passed!")
        return True

    except Exception as e:
        print(f"  ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_compression():
    """Test compression efficiency."""
    print("\n" + "="*60)
    print("Test: Compression Efficiency")
    print("="*60)

    # Create realistic terrain data
    size = 1024
    x = np.linspace(-5, 5, size)
    y = np.linspace(-5, 5, size)
    X, Y = np.meshgrid(x, y)
    heightmap = (np.sin(X) * np.cos(Y) * 500 + 1000).astype(np.float32)

    bbox = (-122.5, 37.7, -122.4, 37.8)

    try:
        # Calculate uncompressed size
        uncompressed_size = heightmap.nbytes
        print(f"\nUncompressed heightmap: {uncompressed_size / 1024:.2f} KB")

        # Create .rterrain package
        output_path = 'test_compression.rterrain'
        create_rterrain_package(
            output_path,
            'Compression Test',
            bbox,
            heightmap
        )

        compressed_size = os.path.getsize(output_path)
        compression_ratio = uncompressed_size / compressed_size

        print(f"Compressed package: {compressed_size / 1024:.2f} KB")
        print(f"Compression ratio: {compression_ratio:.2f}x")

        if compression_ratio > 2:
            print(f"  ✅ Good compression (>{compression_ratio:.1f}x)")
        else:
            print(f"  ⚠️  Low compression ({compression_ratio:.1f}x)")

        # Clean up
        os.remove(output_path)

        print("\n✅ Compression test passed!")
        return True

    except Exception as e:
        print(f"  ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_end_to_end():
    """Test complete export pipeline."""
    print("\n" + "="*60)
    print("Test: End-to-End Pipeline")
    print("="*60)

    try:
        # Simulate fetching SRTM data
        print("\nSimulating SRTM fetch...")
        elevation = np.random.rand(333, 333).astype(np.float32) * 1000

        # Export using convenience function
        print("\nExporting with convenience function...")
        bbox = (-122.5, 37.7, -122.4, 37.8)

        result_path = export_heightmap(
            elevation,
            'test_pipeline.rterrain',
            bbox,
            project_name='Pipeline Test',
            format='rterrain',
            target_size=(1024, 1024),
            fill_nodata=True,
            smooth=True,
            profile='military_simulation'
        )

        if os.path.exists(result_path):
            size = os.path.getsize(result_path)
            print(f"  ✅ Export successful ({size / 1024:.2f} KB)")

            # Read back and verify
            package = read_rterrain_package(result_path)
            metadata = package.get_metadata()

            print(f"\nPackage info:")
            print(f"  Project: {metadata['project']['name']}")
            print(f"  Size: {metadata['terrain']['heightmap_size']}")
            print(f"  Elevation range: {metadata['terrain']['min_elevation']:.1f}m - {metadata['terrain']['max_elevation']:.1f}m")

            os.remove(result_path)

            print("\n✅ End-to-end test passed!")
            return True
        else:
            print("  ❌ Export failed")
            return False

    except Exception as e:
        print(f"  ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("\n" + "="*60)
    print(".rterrain Export Test Suite")
    print("="*60)

    results = []

    # Run tests
    results.append(("Package Creation", test_rterrain_creation()))
    results.append(("Read/Write", test_rterrain_read_write()))
    results.append(("Heightmap Exporter", test_heightmap_exporter()))
    results.append(("Compression", test_compression()))
    results.append(("End-to-End", test_end_to_end()))

    # Summary
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)

    for name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"  {name:25s} {status}")

    total = len(results)
    passed = sum(1 for _, p in results if p)

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed!")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")


if __name__ == "__main__":
    main()
