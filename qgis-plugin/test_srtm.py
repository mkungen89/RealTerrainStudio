"""
Test script for SRTM data fetcher.

Run this from the qgis-plugin directory:
    python test_srtm.py
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from data_sources.srtm import fetch_srtm_elevation
import numpy as np


def progress_callback(message: str, percent: int):
    """Simple progress callback for testing."""
    print(f"[{percent:3d}%] {message}")


def test_san_francisco():
    """Test fetching elevation data for San Francisco area."""
    print("\n" + "="*60)
    print("Test: San Francisco Bay Area")
    print("="*60)

    # Small area in San Francisco
    bbox = (-122.5, 37.7, -122.4, 37.8)

    print(f"\nBounding Box: {bbox}")
    print(f"  Longitude: {bbox[0]:.4f} to {bbox[2]:.4f}")
    print(f"  Latitude:  {bbox[1]:.4f} to {bbox[3]:.4f}")

    try:
        elevation = fetch_srtm_elevation(
            bbox,
            resolution=30,
            progress_callback=progress_callback
        )

        print(f"\nResults:")
        print(f"  Shape: {elevation.shape}")
        print(f"  Data type: {elevation.dtype}")
        print(f"  Min elevation: {np.nanmin(elevation):.1f} m")
        print(f"  Max elevation: {np.nanmax(elevation):.1f} m")
        print(f"  Mean elevation: {np.nanmean(elevation):.1f} m")

        # Check for no-data
        nan_count = np.isnan(elevation).sum()
        total_pixels = elevation.size
        print(f"  No-data pixels: {nan_count} / {total_pixels} ({nan_count/total_pixels*100:.1f}%)")

        print("\n✅ Test passed!")
        return True

    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_mount_everest():
    """Test fetching elevation data for Mount Everest area."""
    print("\n" + "="*60)
    print("Test: Mount Everest Area")
    print("="*60)

    # Small area around Mount Everest
    bbox = (86.9, 27.9, 87.0, 28.0)

    print(f"\nBounding Box: {bbox}")
    print(f"  Longitude: {bbox[0]:.4f} to {bbox[2]:.4f}")
    print(f"  Latitude:  {bbox[1]:.4f} to {bbox[3]:.4f}")

    try:
        elevation = fetch_srtm_elevation(
            bbox,
            resolution=30,
            progress_callback=progress_callback
        )

        print(f"\nResults:")
        print(f"  Shape: {elevation.shape}")
        print(f"  Min elevation: {np.nanmin(elevation):.1f} m")
        print(f"  Max elevation: {np.nanmax(elevation):.1f} m")
        print(f"  Mean elevation: {np.nanmean(elevation):.1f} m")

        # Everest should be very high
        max_elev = np.nanmax(elevation)
        if max_elev > 8000:
            print(f"\n✅ Test passed! (Found peak elevation: {max_elev:.1f}m)")
            return True
        else:
            print(f"\n⚠️  Warning: Expected high elevation (>8000m), got {max_elev:.1f}m")
            return False

    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_grand_canyon():
    """Test fetching elevation data for Grand Canyon area."""
    print("\n" + "="*60)
    print("Test: Grand Canyon Area")
    print("="*60)

    # Small area in Grand Canyon
    bbox = (-112.2, 36.0, -112.0, 36.2)

    print(f"\nBounding Box: {bbox}")
    print(f"  Longitude: {bbox[0]:.4f} to {bbox[2]:.4f}")
    print(f"  Latitude:  {bbox[1]:.4f} to {bbox[3]:.4f}")

    try:
        elevation = fetch_srtm_elevation(
            bbox,
            resolution=30,
            progress_callback=progress_callback
        )

        print(f"\nResults:")
        print(f"  Shape: {elevation.shape}")
        print(f"  Min elevation: {np.nanmin(elevation):.1f} m")
        print(f"  Max elevation: {np.nanmax(elevation):.1f} m")
        print(f"  Elevation range: {np.nanmax(elevation) - np.nanmin(elevation):.1f} m")

        # Grand Canyon has significant elevation change
        elevation_range = np.nanmax(elevation) - np.nanmin(elevation)
        if elevation_range > 1000:
            print(f"\n✅ Test passed! (Found elevation range: {elevation_range:.1f}m)")
            return True
        else:
            print(f"\n⚠️  Warning: Expected large elevation range (>1000m), got {elevation_range:.1f}m")
            return False

    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_cache():
    """Test caching functionality."""
    print("\n" + "="*60)
    print("Test: Cache Functionality")
    print("="*60)

    from data_sources.srtm import SRTMFetcher

    bbox = (-122.5, 37.7, -122.4, 37.8)

    try:
        fetcher = SRTMFetcher()

        print("\nFirst fetch (should download):")
        elevation1 = fetcher.fetch_elevation(bbox, progress_callback=progress_callback)

        cache_size = fetcher.get_cache_size()
        print(f"\nCache size: {cache_size / 1024 / 1024:.2f} MB")

        print("\nSecond fetch (should use cache):")
        elevation2 = fetcher.fetch_elevation(bbox, progress_callback=progress_callback)

        # Should be identical
        if np.array_equal(elevation1, elevation2, equal_nan=True):
            print("\n✅ Test passed! Cache working correctly.")
            return True
        else:
            print("\n❌ Test failed: Cached data doesn't match original")
            return False

    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("SRTM Data Fetcher Test Suite")
    print("="*60)

    # Check GDAL
    try:
        from osgeo import gdal
        print(f"\n✅ GDAL version: {gdal.__version__}")
    except ImportError:
        print("\n❌ GDAL not available. Please install GDAL.")
        print("   QGIS includes GDAL, so this should work within QGIS Python console.")
        return

    results = []

    # Run tests
    results.append(("San Francisco", test_san_francisco()))
    results.append(("Cache", test_cache()))

    # Optional tests (may take longer)
    print("\n" + "="*60)
    print("Running optional tests (may take longer)...")
    print("="*60)

    results.append(("Mount Everest", test_mount_everest()))
    results.append(("Grand Canyon", test_grand_canyon()))

    # Summary
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)

    for name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"  {name:20s} {status}")

    total = len(results)
    passed = sum(1 for _, p in results if p)

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed!")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")


if __name__ == "__main__":
    main()
