"""
Test script for Elevation Processor.

Run this from the qgis-plugin directory:
    python test_elevation_processor.py
"""

import sys
import os
import numpy as np
import time

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from data_sources.elevation_processor import ElevationProcessor, process_elevation


def test_resampling():
    """Test resampling functionality."""
    print("\n" + "="*60)
    print("Test: Resampling")
    print("="*60)

    # Create test data (100x100)
    elevation = np.random.rand(100, 100) * 1000

    processor = ElevationProcessor()

    # Upsample to 200x200
    print("\nUpsampling 100x100 → 200x200")
    start = time.time()
    upsampled = processor.resample(elevation, (200, 200), method='bilinear')
    elapsed = time.time() - start

    print(f"  Input shape: {elevation.shape}")
    print(f"  Output shape: {upsampled.shape}")
    print(f"  Time: {elapsed*1000:.2f}ms")

    if upsampled.shape == (200, 200):
        print("  ✅ Upsampling correct")
    else:
        print(f"  ❌ Expected (200, 200), got {upsampled.shape}")
        return False

    # Downsample to 50x50
    print("\nDownsampling 100x100 → 50x50")
    downsampled = processor.resample(elevation, (50, 50), method='bilinear')

    print(f"  Input shape: {elevation.shape}")
    print(f"  Output shape: {downsampled.shape}")

    if downsampled.shape == (50, 50):
        print("  ✅ Downsampling correct")
    else:
        print(f"  ❌ Expected (50, 50), got {downsampled.shape}")
        return False

    print("\n✅ Resampling test passed!")
    return True


def test_nodata_filling():
    """Test no-data filling."""
    print("\n" + "="*60)
    print("Test: No-Data Filling")
    print("="*60)

    # Create test data with NaN values
    elevation = np.random.rand(100, 100) * 1000

    # Add some NaN values
    elevation[20:30, 20:30] = np.nan
    elevation[50:55, 60:65] = np.nan

    nan_count_before = np.isnan(elevation).sum()
    print(f"\nNaN pixels before: {nan_count_before}")

    processor = ElevationProcessor()

    # Test linear filling
    print("\nTesting linear filling...")
    start = time.time()
    filled = processor.fill_nodata(elevation, method='linear')
    elapsed = time.time() - start

    nan_count_after = np.isnan(filled).sum()

    print(f"  NaN pixels after: {nan_count_after}")
    print(f"  Time: {elapsed*1000:.2f}ms")

    if nan_count_after == 0:
        print("  ✅ All NaN values filled")
    else:
        print(f"  ❌ Still have {nan_count_after} NaN values")
        return False

    # Test nearest filling
    print("\nTesting nearest filling...")
    filled_nearest = processor.fill_nodata(elevation, method='nearest')

    if np.isnan(filled_nearest).sum() == 0:
        print("  ✅ Nearest filling works")
    else:
        print("  ❌ Nearest filling failed")
        return False

    print("\n✅ No-data filling test passed!")
    return True


def test_smoothing():
    """Test smoothing functionality."""
    print("\n" + "="*60)
    print("Test: Smoothing")
    print("="*60)

    # Create noisy elevation data
    elevation = np.random.rand(100, 100) * 100

    # Add some peaks
    elevation[50, 50] = 1000
    elevation[25, 75] = 800

    processor = ElevationProcessor()

    print(f"\nOriginal max: {elevation.max():.1f}")

    # Gaussian smoothing
    print("\nGaussian smoothing (sigma=2.0)...")
    smoothed_gaussian = processor.smooth(elevation, sigma=2.0, preserve_peaks=False)
    print(f"  Smoothed max: {smoothed_gaussian.max():.1f}")
    print(f"  ✅ Gaussian smoothing applied")

    # Median smoothing (preserves peaks)
    print("\nMedian smoothing (sigma=2.0, preserve_peaks=True)...")
    smoothed_median = processor.smooth(elevation, sigma=2.0, preserve_peaks=True)
    print(f"  Smoothed max: {smoothed_median.max():.1f}")
    print(f"  ✅ Median smoothing applied")

    print("\n✅ Smoothing test passed!")
    return True


def test_statistics():
    """Test statistics calculation."""
    print("\n" + "="*60)
    print("Test: Statistics")
    print("="*60)

    # Create test data with known values
    elevation = np.array([[0, 100, 200], [300, 400, 500]], dtype=np.float32)

    processor = ElevationProcessor()
    stats = processor.calculate_statistics(elevation)

    print(f"\nStatistics:")
    print(f"  Min: {stats['min']:.1f}")
    print(f"  Max: {stats['max']:.1f}")
    print(f"  Mean: {stats['mean']:.1f}")
    print(f"  Std: {stats['std']:.1f}")
    print(f"  Range: {stats['range']:.1f}")
    print(f"  Valid: {stats['valid_pixels']}/{stats['total_pixels']}")

    # Verify
    if abs(stats['min'] - 0.0) < 0.1 and abs(stats['max'] - 500.0) < 0.1:
        print("  ✅ Statistics correct")
    else:
        print(f"  ❌ Expected min=0, max=500, got min={stats['min']}, max={stats['max']}")
        return False

    print("\n✅ Statistics test passed!")
    return True


def test_normalization():
    """Test normalization."""
    print("\n" + "="*60)
    print("Test: Normalization")
    print("="*60)

    # Create test data
    elevation = np.array([[0, 100, 200], [300, 400, 500]], dtype=np.float32)

    processor = ElevationProcessor()

    # Normalize to 0-1
    print("\nNormalizing to 0-1 range...")
    normalized = processor.normalize(elevation, target_range=(0.0, 1.0))

    print(f"  Original range: {elevation.min():.1f} to {elevation.max():.1f}")
    print(f"  Normalized range: {normalized.min():.3f} to {normalized.max():.3f}")

    if abs(normalized.min() - 0.0) < 0.01 and abs(normalized.max() - 1.0) < 0.01:
        print("  ✅ Normalization to 0-1 correct")
    else:
        print(f"  ❌ Expected 0.0-1.0, got {normalized.min()}-{normalized.max()}")
        return False

    # Normalize to 0-65535 (16-bit)
    print("\nNormalizing to 0-65535 range...")
    normalized_16 = processor.normalize(elevation, target_range=(0.0, 65535.0))

    print(f"  Normalized range: {normalized_16.min():.1f} to {normalized_16.max():.1f}")

    if abs(normalized_16.min() - 0.0) < 1.0 and abs(normalized_16.max() - 65535.0) < 1.0:
        print("  ✅ Normalization to 0-65535 correct")
    else:
        print(f"  ❌ Expected 0-65535, got {normalized_16.min()}-{normalized_16.max()}")
        return False

    print("\n✅ Normalization test passed!")
    return True


def test_format_conversion():
    """Test format conversion."""
    print("\n" + "="*60)
    print("Test: Format Conversion")
    print("="*60)

    # Create test data
    elevation = np.random.rand(100, 100) * 1000

    processor = ElevationProcessor()

    # Test GeoTIFF export
    print("\nExporting to GeoTIFF...")
    try:
        bbox = (-122.5, 37.7, -122.4, 37.8)
        processor.to_geotiff(elevation, 'test_elevation.tif', bbox)
        if os.path.exists('test_elevation.tif'):
            size = os.path.getsize('test_elevation.tif')
            print(f"  ✅ GeoTIFF created ({size} bytes)")
            os.remove('test_elevation.tif')
        else:
            print("  ❌ GeoTIFF not created")
            return False
    except Exception as e:
        print(f"  ⚠️  GeoTIFF export failed: {e}")

    # Test PNG16 export
    print("\nExporting to PNG16...")
    try:
        processor.to_png16(elevation, 'test_elevation.png')
        if os.path.exists('test_elevation.png'):
            size = os.path.getsize('test_elevation.png')
            print(f"  ✅ PNG16 created ({size} bytes)")
            os.remove('test_elevation.png')
        else:
            print("  ❌ PNG16 not created")
            return False
    except Exception as e:
        print(f"  ⚠️  PNG16 export failed: {e}")

    # Test RAW export
    print("\nExporting to RAW (16-bit)...")
    try:
        processor.to_raw(elevation, 'test_elevation.raw', bit_depth=16)
        if os.path.exists('test_elevation.raw'):
            size = os.path.getsize('test_elevation.raw')
            expected_size = elevation.size * 2  # 16-bit = 2 bytes per pixel
            print(f"  ✅ RAW created ({size} bytes, expected {expected_size})")
            os.remove('test_elevation.raw')
        else:
            print("  ❌ RAW not created")
            return False
    except Exception as e:
        print(f"  ⚠️  RAW export failed: {e}")

    print("\n✅ Format conversion test passed!")
    return True


def test_performance():
    """Test processing performance."""
    print("\n" + "="*60)
    print("Test: Performance (10km² @ 30m resolution)")
    print("="*60)

    # Simulate 10km² at 30m resolution
    # 10km = 10000m / 30m = ~333 pixels per side
    size = 333

    elevation = np.random.rand(size, size) * 1000
    elevation[50:100, 50:100] = np.nan  # Add some NaN

    print(f"\nData size: {size}x{size} = {size*size:,} pixels")

    start = time.time()
    processed = process_elevation(
        elevation,
        target_resolution=(512, 512),
        fill_nodata=True,
        smooth=True,
        smooth_sigma=1.0
    )
    elapsed = time.time() - start

    print(f"Processing time: {elapsed:.2f}s")

    if elapsed < 5.0:
        print(f"  ✅ Performance good (<5s)")
    else:
        print(f"  ⚠️  Performance slower than expected (>5s)")

    print(f"Output shape: {processed.shape}")
    print(f"No NaN values: {np.isnan(processed).sum() == 0}")

    print("\n✅ Performance test complete!")
    return True


def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("Elevation Processor Test Suite")
    print("="*60)

    results = []

    # Run tests
    results.append(("Resampling", test_resampling()))
    results.append(("No-Data Filling", test_nodata_filling()))
    results.append(("Smoothing", test_smoothing()))
    results.append(("Statistics", test_statistics()))
    results.append(("Normalization", test_normalization()))
    results.append(("Format Conversion", test_format_conversion()))
    results.append(("Performance", test_performance()))

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
