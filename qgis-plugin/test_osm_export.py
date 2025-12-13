"""
Test script for OSM objects exporter.

Run from qgis-plugin directory:
    python test_osm_export.py
"""

import sys
import os
import json
import csv
import numpy as np

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from exporters.osm_exporter import OSMExporter, export_osm_objects
from exporters.rterrain_format import create_rterrain_package, read_rterrain_package


def create_mock_ue5_data():
    """Create mock UE5-formatted OSM data for testing."""
    return {
        'buildings': [
            {
                'type': 'building',
                'osm_id': 123456,
                'position': (100000, 200000, 1500),
                'rotation': 45.0,
                'footprint': [
                    (100000, 200000, 1500),
                    (100000, 201000, 1500),
                    (101000, 201000, 1500),
                    (101000, 200000, 1500),
                    (100000, 200000, 1500),
                ],
                'height': 900,  # 9m
                'levels': 3,
                'building_type': 'residential',
                'tags': {'name': 'Test Building', 'building': 'residential'}
            },
            {
                'type': 'building',
                'osm_id': 123457,
                'position': (110000, 210000, 1600),
                'rotation': 90.0,
                'footprint': [
                    (110000, 210000, 1600),
                    (110000, 215000, 1600),
                    (115000, 215000, 1600),
                    (115000, 210000, 1600),
                    (110000, 210000, 1600),
                ],
                'height': 1200,  # 12m
                'levels': 4,
                'building_type': 'commercial',
                'tags': {'name': 'Office Building', 'building': 'commercial'}
            }
        ],
        'roads': [
            {
                'type': 'road',
                'osm_id': 789012,
                'highway_type': 'residential',
                'spline_points': [
                    (100000, 200000, 1500),
                    (101000, 201000, 1520),
                    (102000, 202000, 1540),
                ],
                'width': 500,  # 5m
                'lanes': 2,
                'name': 'Main Street',
                'tags': {'highway': 'residential', 'name': 'Main Street'}
            },
            {
                'type': 'road',
                'osm_id': 789013,
                'highway_type': 'primary',
                'spline_points': [
                    (105000, 205000, 1550),
                    (106000, 206000, 1560),
                    (107000, 207000, 1570),
                    (108000, 208000, 1580),
                ],
                'width': 800,  # 8m
                'lanes': 4,
                'name': 'Highway 101',
                'tags': {'highway': 'primary', 'name': 'Highway 101', 'ref': '101'}
            }
        ],
        'pois': [
            {
                'type': 'poi',
                'osm_id': 345678,
                'position': (103000, 203000, 1530),
                'amenity': 'cafe',
                'name': 'Blue Bottle Coffee',
                'tags': {'amenity': 'cafe', 'name': 'Blue Bottle Coffee'}
            },
            {
                'type': 'poi',
                'osm_id': 345679,
                'position': (104000, 204000, 1540),
                'amenity': 'restaurant',
                'name': 'Pizza Place',
                'tags': {'amenity': 'restaurant', 'name': 'Pizza Place', 'cuisine': 'pizza'}
            },
            {
                'type': 'poi',
                'osm_id': 345680,
                'position': (105000, 205000, 1545),
                'amenity': 'bank',
                'name': 'City Bank',
                'tags': {'amenity': 'bank', 'name': 'City Bank'}
            }
        ],
        'other': []
    }


def test_json_export():
    """Test JSON export."""
    print("\n" + "="*60)
    print("Test: JSON Export")
    print("="*60)

    try:
        # Create mock data
        ue5_data = create_mock_ue5_data()
        bbox = (-122.5, 37.7, -122.4, 37.8)

        # Export
        exporter = OSMExporter()
        json_path = 'test_osm_objects.json'

        print("\nExporting to JSON...")
        exporter.export_json(ue5_data, json_path, bbox)

        # Verify file exists
        if not os.path.exists(json_path):
            print("  ❌ JSON file not created")
            return False

        # Read and verify content
        with open(json_path, 'r') as f:
            data = json.load(f)

        print(f"\n✅ JSON file created: {json_path}")
        print(f"\nContents:")
        print(f"  Metadata: ✓")
        print(f"  Buildings: {len(data['buildings'])}")
        print(f"  Roads: {len(data['roads'])}")
        print(f"  POIs: {len(data['pois'])}")

        # Verify structure
        assert 'metadata' in data
        assert 'buildings' in data
        assert 'roads' in data
        assert 'pois' in data

        assert data['metadata']['counts']['buildings'] == 2
        assert data['metadata']['counts']['roads'] == 2
        assert data['metadata']['counts']['pois'] == 3

        # Check building data
        building = data['buildings'][0]
        print(f"\n  Sample building:")
        print(f"    ID: {building['id']}")
        print(f"    Type: {building['type']}")
        print(f"    Position: ({building['position'][0]/100:.1f}m, {building['position'][1]/100:.1f}m, {building['position'][2]/100:.1f}m)")
        print(f"    Height: {building['height']/100:.1f}m")
        print(f"    Rotation: {building['rotation']}°")

        # Clean up
        os.remove(json_path)

        print("\n✅ JSON export test passed!")
        return True

    except Exception as e:
        print(f"  ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_csv_export():
    """Test CSV export."""
    print("\n" + "="*60)
    print("Test: CSV Export")
    print("="*60)

    try:
        # Create mock data
        ue5_data = create_mock_ue5_data()
        bbox = (-122.5, 37.7, -122.4, 37.8)

        # Export
        exporter = OSMExporter()
        output_dir = 'test_csv_output'

        print("\nExporting to CSV...")
        csv_files = exporter.export_csv(ue5_data, output_dir, bbox)

        print(f"\n✅ CSV files created:")
        for category, path in csv_files.items():
            print(f"  {category}: {path}")

            # Verify file exists
            if not os.path.exists(path):
                print(f"    ❌ File not found")
                return False

            # Count rows
            with open(path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                rows = list(reader)
                print(f"    Rows: {len(rows)} (including header)")

        # Verify buildings.csv
        buildings_path = csv_files.get('buildings')
        if buildings_path:
            with open(buildings_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                buildings = list(reader)

                print(f"\n  Sample building from CSV:")
                building = buildings[0]
                print(f"    ID: {building['ID']}")
                print(f"    Type: {building['Type']}")
                print(f"    Height: {int(building['Height (cm)'])/100:.1f}m")

        # Clean up
        import shutil
        if os.path.exists(output_dir):
            shutil.rmtree(output_dir)

        print("\n✅ CSV export test passed!")
        return True

    except Exception as e:
        print(f"  ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_complete_export():
    """Test complete export (both JSON and CSV)."""
    print("\n" + "="*60)
    print("Test: Complete Export (JSON + CSV)")
    print("="*60)

    try:
        # Create mock data
        ue5_data = create_mock_ue5_data()
        bbox = (-122.5, 37.7, -122.4, 37.8)

        # Export
        exporter = OSMExporter()
        output_dir = 'test_complete_output'

        print("\nExporting both formats...")
        files = exporter.export_complete(
            ue5_data,
            output_dir,
            bbox,
            format='both'
        )

        print(f"\n✅ Files created:")
        for key, path in files.items():
            print(f"  {key}: {path}")

            if not os.path.exists(path):
                print(f"    ❌ File not found")
                return False

        # Verify we have both formats
        assert 'json' in files
        assert 'buildings_csv' in files
        assert 'roads_csv' in files
        assert 'pois_csv' in files

        # Clean up
        import shutil
        if os.path.exists(output_dir):
            shutil.rmtree(output_dir)

        print("\n✅ Complete export test passed!")
        return True

    except Exception as e:
        print(f"  ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_summary_generation():
    """Test summary statistics generation."""
    print("\n" + "="*60)
    print("Test: Summary Generation")
    print("="*60)

    try:
        # Create mock data
        ue5_data = create_mock_ue5_data()

        # Generate summary
        exporter = OSMExporter()
        summary_path = 'test_summary.txt'

        print("\nGenerating summary...")
        exporter.create_summary(ue5_data, summary_path)

        # Verify file exists
        if not os.path.exists(summary_path):
            print("  ❌ Summary file not created")
            return False

        # Read and display
        with open(summary_path, 'r', encoding='utf-8') as f:
            content = f.read()

        print(f"\n✅ Summary created:")
        print("─" * 60)
        print(content)
        print("─" * 60)

        # Clean up
        os.remove(summary_path)

        print("\n✅ Summary generation test passed!")
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
        # Create mock data
        ue5_data = create_mock_ue5_data()
        bbox = (-122.5, 37.7, -122.4, 37.8)
        heightmap = np.random.rand(512, 512).astype(np.float32) * 100

        # Export OSM to JSON first
        exporter = OSMExporter()
        json_path = 'temp_osm.json'
        exporter.export_json(ue5_data, json_path, bbox)

        # Read JSON back
        with open(json_path, 'r') as f:
            osm_json = json.load(f)

        print("\nCreating .rterrain package with OSM data...")

        # Create .rterrain package with OSM data
        output_path = 'test_with_osm.rterrain'

        create_rterrain_package(
            output_path,
            'Test with OSM',
            bbox,
            heightmap,
            osm_data=osm_json,
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

        # Verify OSM data
        loaded_osm = package.get_osm_data()
        if loaded_osm is not None:
            print(f"  ✅ OSM data loaded")
            print(f"    Buildings: {len(loaded_osm.get('buildings', []))}")
            print(f"    Roads: {len(loaded_osm.get('roads', []))}")
            print(f"    POIs: {len(loaded_osm.get('pois', []))}")

            # Verify data integrity
            assert len(loaded_osm['buildings']) == 2
            assert len(loaded_osm['roads']) == 2
            assert len(loaded_osm['pois']) == 3

            # Check a building
            building = loaded_osm['buildings'][0]
            print(f"\n  Sample building from package:")
            print(f"    ID: {building['id']}")
            print(f"    Type: {building['type']}")
            print(f"    Height: {building['height']/100:.1f}m")
        else:
            print("  ❌ OSM data not found")
            return False

        # Check metadata
        metadata = package.get_metadata()
        if metadata['content'].get('osm_objects'):
            print(f"  ✅ OSM objects count in metadata: {metadata['content']['osm_objects']}")
        else:
            print("  ⚠️  OSM objects not marked in metadata")

        # Clean up
        os.remove(json_path)
        os.remove(output_path)

        print("\n✅ .rterrain integration test passed!")
        return True

    except Exception as e:
        print(f"  ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_convenience_function():
    """Test convenience function."""
    print("\n" + "="*60)
    print("Test: Convenience Function")
    print("="*60)

    try:
        # Create mock data
        ue5_data = create_mock_ue5_data()
        bbox = (-122.5, 37.7, -122.4, 37.8)

        # Use convenience function
        print("\nUsing convenience function...")
        json_path = export_osm_objects(
            ue5_data,
            'test_convenience.json',
            bbox,
            format='json'
        )

        if os.path.exists(json_path):
            print(f"  ✅ File created: {json_path}")

            # Verify content
            with open(json_path, 'r') as f:
                data = json.load(f)

            assert len(data['buildings']) == 2
            assert len(data['roads']) == 2

            os.remove(json_path)

            print("\n✅ Convenience function test passed!")
            return True
        else:
            print("  ❌ File not created")
            return False

    except Exception as e:
        print(f"  ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("OSM Objects Exporter Test Suite")
    print("="*60)

    results = []

    # Run tests
    results.append(("JSON Export", test_json_export()))
    results.append(("CSV Export", test_csv_export()))
    results.append(("Complete Export", test_complete_export()))
    results.append(("Summary Generation", test_summary_generation()))
    results.append((".rterrain Integration", test_rterrain_integration()))
    results.append(("Convenience Function", test_convenience_function()))

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
