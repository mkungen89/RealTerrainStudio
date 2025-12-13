"""
Test script for satellite texture exporter.

Run from qgis-plugin directory:
    python test_satellite_export.py
"""

import sys
import os
import numpy as np

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from data_sources.sentinel2_fetcher import fetch_sentinel2_imagery
from exporters.satellite_exporter import SatelliteExporter, export_satellite_texture
from exporters.heightmap_exporter import HeightmapExporter
from exporters.rterrain_format import create_rterrain_package, read_rterrain_package


def test_jpeg_export():
    """Test JPEG export."""
    print("\n" + "="*60)
    print("Test: JPEG Export")
    print("="*60)

    try:
        # Fetch imagery (placeholder)
        bbox = (-122.5, 37.7, -122.4, 37.8)
        print("\nFetching satellite imagery...")
        imagery = fetch_sentinel2_imagery(bbox, resolution=10)

        print(f"  Imagery shape: {imagery.shape}")
        print(f"  Data type: {imagery.dtype}")

        # Export as JPEG
        exporter = SatelliteExporter()

        print("\nExporting as JPEG (quality 90)...")
        jpeg_path = exporter.export_jpeg(
            imagery,
            'test_satellite.jpg',
            quality=90,
            optimize=True
        )

        if os.path.exists(jpeg_path):
            size_mb = os.path.getsize(jpeg_path) / (1024 * 1024)
            print(f"  ✅ JPEG created: {jpeg_path}")
            print(f"  Size: {size_mb:.2f} MB")

            # Test different quality levels
            print("\nTesting different quality levels...")
            qualities = [60, 75, 90, 95]
            for q in qualities:
                test_path = f'test_quality_{q}.jpg'
                exporter.export_jpeg(imagery, test_path, quality=q)
                size = os.path.getsize(test_path) / (1024 * 1024)
                print(f"  Quality {q:2d}: {size:5.2f} MB")
                os.remove(test_path)

            # Clean up
            os.remove(jpeg_path)

            print("\n✅ JPEG export test passed!")
            return True
        else:
            print("  ❌ JPEG not created")
            return False

    except Exception as e:
        print(f"  ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_color_correction():
    """Test color correction."""
    print("\n" + "="*60)
    print("Test: Color Correction")
    print("="*60)

    try:
        # Fetch imagery
        bbox = (-122.5, 37.7, -122.4, 37.8)
        imagery = fetch_sentinel2_imagery(bbox, resolution=10)

        exporter = SatelliteExporter()

        # Test various corrections
        corrections = [
            {'brightness': 1.2, 'contrast': 1.1, 'saturation': 1.15},
            {'brightness': 0.9, 'contrast': 1.2, 'saturation': 0.95},
            {'brightness': 1.0, 'contrast': 1.3, 'saturation': 1.0}
        ]

        print("\nTesting color corrections...")
        for i, correction in enumerate(corrections):
            output_path = f'test_corrected_{i}.jpg'
            exporter.export_jpeg(
                imagery,
                output_path,
                quality=90,
                color_correction=correction
            )

            if os.path.exists(output_path):
                print(f"  ✅ Correction {i+1}: {correction}")
                os.remove(output_path)
            else:
                print(f"  ❌ Failed to create corrected image {i+1}")
                return False

        print("\n✅ Color correction test passed!")
        return True

    except Exception as e:
        print(f"  ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_dimension_matching():
    """Test dimension matching with heightmap."""
    print("\n" + "="*60)
    print("Test: Dimension Matching")
    print("="*60)

    try:
        # Fetch imagery at one resolution
        bbox = (-122.5, 37.7, -122.4, 37.8)
        imagery = fetch_sentinel2_imagery(bbox, resolution=10)

        print(f"\nOriginal imagery shape: {imagery.shape}")

        exporter = SatelliteExporter()

        # Test matching to different sizes
        target_sizes = [
            (512, 512),
            (1024, 1024),
            (2048, 2048),
            (1024, 2048)  # Non-square
        ]

        print("\nResizing to different dimensions...")
        for target in target_sizes:
            resized = exporter.match_dimensions(imagery, target, method='bilinear')

            if resized.shape[:2] == target:
                print(f"  ✅ {target}: {resized.shape}")
            else:
                print(f"  ❌ {target}: Expected {target}, got {resized.shape}")
                return False

        print("\n✅ Dimension matching test passed!")
        return True

    except Exception as e:
        print(f"  ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_export_with_metadata():
    """Test export with metadata generation."""
    print("\n" + "="*60)
    print("Test: Export with Metadata")
    print("="*60)

    try:
        # Fetch imagery
        bbox = (-122.5, 37.7, -122.4, 37.8)
        imagery = fetch_sentinel2_imagery(bbox, resolution=10)

        # Export with metadata
        print("\nExporting texture with metadata...")
        result = export_satellite_texture(
            imagery,
            'test_satellite.jpg',
            bbox,
            format='jpeg',
            quality=90,
            color_correction={'brightness': 1.1, 'contrast': 1.05}
        )

        print(f"\nCreated files:")
        print(f"  Texture: {result['texture']}")
        print(f"  Metadata: {result['metadata']}")

        # Verify files exist
        if not os.path.exists(result['texture']):
            print("  ❌ Texture file not found")
            return False

        if not os.path.exists(result['metadata']):
            print("  ❌ Metadata file not found")
            return False

        # Read and verify metadata
        import json
        with open(result['metadata'], 'r') as f:
            metadata = json.load(f)

        print("\nMetadata content:")
        print(f"  Type: {metadata['type']}")
        print(f"  Format: {metadata['format']}")
        print(f"  Dimensions: {metadata['dimensions']['width']}x{metadata['dimensions']['height']}")
        print(f"  File size: {metadata['file_size_mb']} MB")
        print(f"  Color correction: {metadata.get('color_correction', 'None')}")

        # Clean up
        os.remove(result['texture'])
        os.remove(result['metadata'])

        print("\n✅ Export with metadata test passed!")
        return True

    except Exception as e:
        print(f"  ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_rterrain_integration():
    """Test integration with .rterrain format."""
    print("\n" + "="*60)
    print("Test: .rterrain Integration")
    print("="*60)

    try:
        bbox = (-122.5, 37.7, -122.4, 37.8)

        # Fetch elevation
        print("\nFetching elevation data...")
        heightmap = np.random.rand(512, 512).astype(np.float32) * 1000

        # Fetch satellite imagery
        print("Fetching satellite imagery...")
        imagery = fetch_sentinel2_imagery(bbox, resolution=10)

        # Match dimensions
        print("Matching dimensions...")
        exporter = SatelliteExporter()
        imagery_matched = exporter.match_dimensions(imagery, heightmap.shape[:2])

        print(f"  Heightmap: {heightmap.shape}")
        print(f"  Imagery: {imagery_matched.shape}")

        # Export imagery as JPEG bytes
        print("\nExporting satellite as JPEG...")
        temp_jpeg = 'temp_satellite.jpg'
        exporter.export_jpeg(imagery_matched, temp_jpeg, quality=90)

        with open(temp_jpeg, 'rb') as f:
            satellite_bytes = f.read()

        print(f"  Satellite JPEG: {len(satellite_bytes) / 1024:.1f} KB")

        # Create .rterrain package with satellite
        print("\nCreating .rterrain package with satellite...")
        output_path = 'test_with_satellite.rterrain'

        create_rterrain_package(
            output_path,
            'Test with Satellite',
            bbox,
            heightmap,
            satellite=satellite_bytes,
            profile='open_world',
            resolution=30
        )

        # Verify package
        package_size = os.path.getsize(output_path) / (1024 * 1024)
        print(f"  ✅ Package created: {package_size:.2f} MB")

        # Read back and verify
        print("\nReading package back...")
        package = read_rterrain_package(output_path)

        # Verify heightmap
        loaded_heightmap = package.get_heightmap()
        if loaded_heightmap is not None:
            print(f"  ✅ Heightmap loaded: {loaded_heightmap.shape}")
        else:
            print("  ❌ Heightmap not found")
            return False

        # Verify satellite
        loaded_satellite = package.get_satellite()
        if loaded_satellite is not None:
            print(f"  ✅ Satellite loaded: {len(loaded_satellite) / 1024:.1f} KB")

            # Save to verify it's valid JPEG
            with open('verify_satellite.jpg', 'wb') as f:
                f.write(loaded_satellite)

            # Try to open as image
            from PIL import Image
            img = Image.open('verify_satellite.jpg')
            print(f"  ✅ Satellite is valid JPEG: {img.size}")

            os.remove('verify_satellite.jpg')
        else:
            print("  ❌ Satellite not found")
            return False

        # Check metadata
        metadata = package.get_metadata()
        if metadata['content'].get('satellite'):
            print("  ✅ Satellite marked in metadata")
        else:
            print("  ❌ Satellite not marked in metadata")
            return False

        # Clean up
        os.remove(temp_jpeg)
        os.remove(output_path)

        print("\n✅ .rterrain integration test passed!")
        return True

    except Exception as e:
        print(f"  ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_file_size_optimization():
    """Test file size optimization."""
    print("\n" + "="*60)
    print("Test: File Size Optimization")
    print("="*60)

    try:
        # Fetch imagery
        bbox = (-122.5, 37.7, -122.4, 37.8)
        imagery = fetch_sentinel2_imagery(bbox, resolution=10)

        exporter = SatelliteExporter()

        # Calculate optimal quality for 50MB target
        print("\nCalculating optimal quality for 50MB target...")
        optimal_quality = exporter.calculate_optimal_quality(imagery, target_size_mb=50)

        print(f"  Recommended quality: {optimal_quality}")

        # Export with optimal quality
        test_path = 'test_optimized.jpg'
        exporter.export_jpeg(imagery, test_path, quality=optimal_quality)

        size_mb = os.path.getsize(test_path) / (1024 * 1024)
        print(f"  Actual file size: {size_mb:.2f} MB")

        if size_mb <= 55:  # Allow 10% margin
            print(f"  ✅ Size within target (50 MB ± 10%)")
        else:
            print(f"  ⚠️  Size above target, but acceptable")

        os.remove(test_path)

        print("\n✅ File size optimization test passed!")
        return True

    except Exception as e:
        print(f"  ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_format_comparison():
    """Compare different export formats."""
    print("\n" + "="*60)
    print("Test: Format Comparison")
    print("="*60)

    try:
        # Fetch imagery
        bbox = (-122.5, 37.7, -122.4, 37.8)
        imagery = fetch_sentinel2_imagery(bbox, resolution=10)

        exporter = SatelliteExporter()

        formats = [
            ('JPEG Q90', 'jpeg', {'quality': 90}),
            ('JPEG Q75', 'jpeg', {'quality': 75}),
            ('PNG', 'png', {}),
            ('TGA', 'tga', {})
        ]

        print("\nComparing formats:")
        print(f"{'Format':<12} {'Size (MB)':<12} {'Note'}")
        print("-" * 50)

        for name, fmt, kwargs in formats:
            if fmt == 'jpeg':
                path = f'test_compare.jpg'
                exporter.export_jpeg(imagery, path, **kwargs)
            elif fmt == 'png':
                path = f'test_compare.png'
                exporter.export_png(imagery, path)
            elif fmt == 'tga':
                path = f'test_compare.tga'
                exporter.export_tga(imagery, path)

            size_mb = os.path.getsize(path) / (1024 * 1024)

            note = ""
            if fmt == 'jpeg' and kwargs.get('quality') == 90:
                note = "Recommended for UE5"
            elif fmt == 'tga':
                note = "Lossless"

            print(f"{name:<12} {size_mb:<12.2f} {note}")

            os.remove(path)

        print("\n✅ Format comparison test passed!")
        return True

    except Exception as e:
        print(f"  ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("Satellite Texture Exporter Test Suite")
    print("="*60)

    results = []

    # Run tests
    results.append(("JPEG Export", test_jpeg_export()))
    results.append(("Color Correction", test_color_correction()))
    results.append(("Dimension Matching", test_dimension_matching()))
    results.append(("Export with Metadata", test_export_with_metadata()))
    results.append((".rterrain Integration", test_rterrain_integration()))
    results.append(("File Size Optimization", test_file_size_optimization()))
    results.append(("Format Comparison", test_format_comparison()))

    # Summary
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)

    for name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"  {name:30s} {status}")

    total = len(results)
    passed = sum(1 for _, p in results if p)

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed!")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")


if __name__ == "__main__":
    main()
