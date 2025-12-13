"""
Test script for material classifier.

Run from qgis-plugin directory:
    python test_material_classifier.py
"""

import sys
import os
import numpy as np

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from data_sources.material_classifier import MaterialClassifier, classify_materials


def create_test_heightmap(size=512):
    """Create test heightmap with varied terrain."""
    # Create base terrain
    x = np.linspace(0, 10, size)
    y = np.linspace(0, 10, size)
    X, Y = np.meshgrid(x, y)

    # Create varied terrain
    # - Flat area (bottom left)
    # - Hills (middle)
    # - Mountains (top right)
    heightmap = np.zeros((size, size), dtype=np.float32)

    # Flat plains (0-50m)
    heightmap[:size//3, :size//3] = np.random.rand(size//3, size//3) * 10 + 20

    # Rolling hills (50-200m)
    hills_x = X[size//3:2*size//3, size//3:2*size//3]
    hills_y = Y[size//3:2*size//3, size//3:2*size//3]
    heightmap[size//3:2*size//3, size//3:2*size//3] = \
        50 + 50 * np.sin(hills_x) * np.cos(hills_y) + np.random.rand(size//3, size//3) * 20

    # Mountains (200-1000m)
    mountains_x = X[2*size//3:, 2*size//3:]
    mountains_y = Y[2*size//3:, 2*size//3:]
    heightmap[2*size//3:, 2*size//3:] = \
        500 + 300 * np.sin(mountains_x * 2) + 200 * np.cos(mountains_y * 2) + \
        np.random.rand(size - 2*size//3, size - 2*size//3) * 100

    # Smooth transitions
    from scipy import ndimage
    heightmap = ndimage.gaussian_filter(heightmap, sigma=3)

    return heightmap


def create_test_satellite(size=512):
    """Create test satellite imagery with varied colors."""
    satellite = np.zeros((size, size, 3), dtype=np.uint8)

    # Green vegetation (bottom left)
    satellite[:size//3, :size//3, 0] = 60  # R
    satellite[:size//3, :size//3, 1] = 120  # G
    satellite[:size//3, :size//3, 2] = 50  # B

    # Brown dirt (middle)
    satellite[size//3:2*size//3, size//3:2*size//3, 0] = 140  # R
    satellite[size//3:2*size//3, size//3:2*size//3, 1] = 100  # G
    satellite[size//3:2*size//3, size//3:2*size//3, 2] = 70   # B

    # Gray rock (top right)
    satellite[2*size//3:, 2*size//3:, 0] = 100  # R
    satellite[2*size//3:, 2*size//3:, 1] = 100  # G
    satellite[2*size//3:, 2*size//3:, 2] = 100  # B

    # Blue water (bottom right corner)
    satellite[2*size//3:, :size//4, 0] = 50   # R
    satellite[2*size//3:, :size//4, 1] = 80   # G
    satellite[2*size//3:, :size//4, 2] = 150  # B

    # Add noise
    noise = np.random.randint(-20, 20, (size, size, 3), dtype=np.int16)
    satellite = np.clip(satellite.astype(np.int16) + noise, 0, 255).astype(np.uint8)

    # Smooth
    from scipy import ndimage
    for i in range(3):
        satellite[:, :, i] = ndimage.gaussian_filter(satellite[:, :, i], sigma=2)

    return satellite


def test_slope_calculation():
    """Test slope calculation."""
    print("\n" + "="*60)
    print("Test: Slope Calculation")
    print("="*60)

    try:
        # Create simple heightmap
        heightmap = np.array([
            [0, 0, 0, 0],
            [0, 10, 20, 30],
            [0, 20, 40, 60],
            [0, 30, 60, 90]
        ], dtype=np.float32)

        classifier = MaterialClassifier()
        slope = classifier._calculate_slope(heightmap, resolution=10.0)

        print(f"\nHeightmap shape: {heightmap.shape}")
        print(f"Slope shape: {slope.shape}")
        print(f"Slope range: {slope.min():.1f}° - {slope.max():.1f}°")

        print("\n✅ Slope calculation test passed!")
        return True

    except Exception as e:
        print(f"  ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_classification_without_satellite():
    """Test classification using only heightmap."""
    print("\n" + "="*60)
    print("Test: Classification (Heightmap Only)")
    print("="*60)

    try:
        # Create test data
        print("\nCreating test heightmap...")
        heightmap = create_test_heightmap(256)

        print(f"  Shape: {heightmap.shape}")
        print(f"  Elevation: {heightmap.min():.1f}m - {heightmap.max():.1f}m")

        # Classify
        print("\nClassifying materials...")
        classifier = MaterialClassifier()
        masks = classifier.classify(heightmap, satellite=None, resolution=30.0)

        print(f"\n✅ Generated {len(masks)} material masks:")
        for name, mask in masks.items():
            coverage = mask.mean() * 100
            print(f"  {name:10s}: {coverage:5.1f}% coverage")

        # Verify masks
        assert len(masks) == 7  # grass, rock, dirt, sand, snow, forest, water
        for name, mask in masks.items():
            assert mask.shape == heightmap.shape
            assert mask.min() >= 0.0
            assert mask.max() <= 1.0

        print("\n✅ Classification without satellite test passed!")
        return True

    except Exception as e:
        print(f"  ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_classification_with_satellite():
    """Test classification using heightmap + satellite."""
    print("\n" + "="*60)
    print("Test: Classification (Heightmap + Satellite)")
    print("="*60)

    try:
        # Create test data
        print("\nCreating test data...")
        heightmap = create_test_heightmap(256)
        satellite = create_test_satellite(256)

        print(f"  Heightmap: {heightmap.shape}, {heightmap.min():.1f}m - {heightmap.max():.1f}m")
        print(f"  Satellite: {satellite.shape}, dtype={satellite.dtype}")

        # Classify
        print("\nClassifying materials with satellite...")
        masks = classify_materials(heightmap, satellite, resolution=30.0)

        print(f"\n✅ Generated {len(masks)} material masks:")
        for name, mask in masks.items():
            coverage = mask.mean() * 100
            print(f"  {name:10s}: {coverage:5.1f}% coverage (min={mask.min():.2f}, max={mask.max():.2f})")

        # Verify forest and water detected (should be > 0 with satellite)
        assert masks['forest'].max() > 0.0 or masks['grass'].max() > 0.0
        assert masks['water'].max() > 0.0

        print("\n✅ Classification with satellite test passed!")
        return True

    except Exception as e:
        print(f"  ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_mask_normalization():
    """Test that masks sum to ~1.0."""
    print("\n" + "="*60)
    print("Test: Mask Normalization")
    print("="*60)

    try:
        # Create test data
        heightmap = create_test_heightmap(128)
        satellite = create_test_satellite(128)

        # Classify
        print("\nClassifying...")
        masks = classify_materials(heightmap, satellite)

        # Stack masks
        mask_stack = np.stack(list(masks.values()), axis=0)

        # Sum across materials at each pixel
        total = mask_stack.sum(axis=0)

        print(f"\nMask sum statistics:")
        print(f"  Min: {total.min():.3f}")
        print(f"  Max: {total.max():.3f}")
        print(f"  Mean: {total.mean():.3f}")
        print(f"  Std: {total.std():.3f}")

        # Should sum to ~1.0 (allow some tolerance)
        assert total.min() > 0.9
        assert total.max() < 1.1
        assert abs(total.mean() - 1.0) < 0.05

        print("\n✅ Mask normalization test passed!")
        return True

    except Exception as e:
        print(f"  ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_png_export():
    """Test PNG export."""
    print("\n" + "="*60)
    print("Test: PNG Export")
    print("="*60)

    try:
        # Create test data
        heightmap = create_test_heightmap(128)
        satellite = create_test_satellite(128)

        # Classify
        print("\nClassifying...")
        classifier = MaterialClassifier()
        masks = classifier.classify(heightmap, satellite)

        # Export
        print("\nExporting masks to PNG...")
        output_dir = 'test_masks'
        created_files = classifier.export_masks_png(masks, output_dir)

        print(f"\n✅ Exported {len(created_files)} mask files:")
        for name, path in created_files.items():
            if os.path.exists(path):
                size = os.path.getsize(path) / 1024
                print(f"  {name:10s}: {path} ({size:.1f} KB)")
            else:
                print(f"  ❌ {name}: File not created")
                return False

        # Verify files are valid PNGs
        from PIL import Image
        for name, path in created_files.items():
            img = Image.open(path)
            assert img.mode == 'L'  # Grayscale
            assert img.size == (128, 128)

        # Clean up
        import shutil
        if os.path.exists(output_dir):
            shutil.rmtree(output_dir)

        print("\n✅ PNG export test passed!")
        return True

    except Exception as e:
        print(f"  ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_statistics():
    """Test statistics generation."""
    print("\n" + "="*60)
    print("Test: Statistics")
    print("="*60)

    try:
        # Create test data
        heightmap = create_test_heightmap(128)
        satellite = create_test_satellite(128)

        # Classify
        classifier = MaterialClassifier()
        masks = classifier.classify(heightmap, satellite)

        # Get statistics
        print("\nGenerating statistics...")
        stats = classifier.get_statistics(masks)

        print(f"\nMaterial statistics:")
        for name, stat in stats.items():
            print(f"\n  {name.upper()}:")
            print(f"    Coverage: {stat['coverage_percent']:.1f}%")
            print(f"    Range: {stat['min']:.2f} - {stat['max']:.2f}")
            print(f"    Mean: {stat['mean']:.3f}")
            print(f"    Std: {stat['std']:.3f}")

        # Verify statistics
        assert len(stats) == 7
        for name, stat in stats.items():
            assert 'coverage_percent' in stat
            assert 0 <= stat['coverage_percent'] <= 100

        print("\n✅ Statistics test passed!")
        return True

    except Exception as e:
        print(f"  ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_visual_output():
    """Test visual output (creates test PNG files for manual inspection)."""
    print("\n" + "="*60)
    print("Test: Visual Output")
    print("="*60)

    try:
        # Create test data
        print("\nCreating test terrain...")
        heightmap = create_test_heightmap(512)
        satellite = create_test_satellite(512)

        # Classify
        print("Classifying materials...")
        classifier = MaterialClassifier()
        masks = classifier.classify(heightmap, satellite, resolution=30.0)

        # Export masks
        print("Exporting masks...")
        output_dir = 'test_visual_output'
        classifier.export_masks_png(masks, output_dir)

        # Save heightmap visualization
        print("Saving heightmap visualization...")
        from PIL import Image
        heightmap_normalized = ((heightmap - heightmap.min()) / (heightmap.max() - heightmap.min()) * 255).astype(np.uint8)
        Image.fromarray(heightmap_normalized, mode='L').save(f'{output_dir}/heightmap.png')

        # Save satellite
        print("Saving satellite...")
        Image.fromarray(satellite, mode='RGB').save(f'{output_dir}/satellite.png')

        # Create composite
        print("Creating composite visualization...")
        composite = np.zeros((512, 512, 3), dtype=np.uint8)
        composite[:, :, 0] = (masks['rock'] * 100 + masks['dirt'] * 80).astype(np.uint8)
        composite[:, :, 1] = (masks['grass'] * 150 + masks['forest'] * 100).astype(np.uint8)
        composite[:, :, 2] = (masks['water'] * 200 + masks['snow'] * 255).astype(np.uint8)
        Image.fromarray(composite, mode='RGB').save(f'{output_dir}/composite.png')

        print(f"\n✅ Visual output created in {output_dir}/")
        print("  Files for manual inspection:")
        print("    - heightmap.png (elevation visualization)")
        print("    - satellite.png (input satellite)")
        print("    - grass_mask.png, rock_mask.png, etc. (individual masks)")
        print("    - composite.png (RGB composite of masks)")

        print("\n✅ Visual output test passed!")
        print(f"\n  📁 Check {output_dir}/ folder for results")
        return True

    except Exception as e:
        print(f"  ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("Material Classifier Test Suite")
    print("="*60)

    results = []

    # Run tests
    results.append(("Slope Calculation", test_slope_calculation()))
    results.append(("Classification (Heightmap Only)", test_classification_without_satellite()))
    results.append(("Classification (With Satellite)", test_classification_with_satellite()))
    results.append(("Mask Normalization", test_mask_normalization()))
    results.append(("PNG Export", test_png_export()))
    results.append(("Statistics", test_statistics()))
    results.append(("Visual Output", test_visual_output()))

    # Summary
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)

    for name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"  {name:40s} {status}")

    total = len(results)
    passed = sum(1 for _, p in results if p)

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed!")
        print("\nNote: Check test_visual_output/ folder for visual inspection of masks")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")


if __name__ == "__main__":
    main()
