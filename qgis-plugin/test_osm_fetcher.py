"""
Test script for OSM data fetcher and coordinate converter.

Run from qgis-plugin directory:
    python test_osm_fetcher.py
"""

import sys
import os
import json
import numpy as np

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from data_sources.osm_fetcher import OSMFetcher, fetch_osm_data
from data_sources.osm_to_ue5_converter import OSMToUE5Converter, convert_osm_to_ue5


def test_area_calculation():
    """Test bounding box area calculation."""
    print("\n" + "="*60)
    print("Test: Area Calculation")
    print("="*60)

    try:
        fetcher = OSMFetcher()

        # Test different sized areas
        test_cases = [
            ("Small (1km²)", (-122.45, 37.75, -122.44, 37.76)),
            ("Medium (10km²)", (-122.5, 37.7, -122.4, 37.8)),
            ("Large (100km²)", (-122.6, 37.6, -122.4, 37.9)),
        ]

        print("\nArea calculations:")
        for name, bbox in test_cases:
            area = fetcher.calculate_area(bbox)
            print(f"  {name:20s}: {area:8.2f} km²")

        print("\n✅ Area calculation test passed!")
        return True

    except Exception as e:
        print(f"  ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_chunking_logic():
    """Test automatic chunking for large areas."""
    print("\n" + "="*60)
    print("Test: Chunking Logic")
    print("="*60)

    try:
        fetcher = OSMFetcher()

        # Test chunking for different scenarios
        test_cases = [
            ("Small area (no chunking)", (-122.45, 37.75, -122.44, 37.76), {'roads': True}),
            ("Medium area (might chunk)", (-122.5, 37.7, -122.4, 37.8), {'roads': True, 'buildings': True}),
            ("Large area (will chunk)", (-122.6, 37.6, -122.4, 37.9), {'roads': True, 'buildings': True}),
        ]

        print("\nChunking decisions:")
        for name, bbox, filters in test_cases:
            estimated = fetcher.estimate_node_count(bbox, filters)

            if estimated > fetcher.MAX_NODES:
                chunks = fetcher.create_chunks(bbox, estimated)
                print(f"  {name}:")
                print(f"    Estimated: {estimated:,} nodes")
                print(f"    Chunks: {len(chunks)} ({int(np.sqrt(len(chunks)))}×{int(np.sqrt(len(chunks)))} grid)")
            else:
                print(f"  {name}:")
                print(f"    Estimated: {estimated:,} nodes")
                print(f"    Chunks: 1 (no chunking needed)")

        print("\n✅ Chunking logic test passed!")
        return True

    except Exception as e:
        print(f"  ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_query_building():
    """Test Overpass QL query building."""
    print("\n" + "="*60)
    print("Test: Query Building")
    print("="*60)

    try:
        fetcher = OSMFetcher()

        bbox = (-122.45, 37.75, -122.44, 37.76)

        # Test different filter combinations
        filter_tests = [
            {'roads': True},
            {'buildings': True},
            {'roads': True, 'buildings': True},
            {'roads': True, 'buildings': True, 'poi': True, 'water': True},
        ]

        print("\nGenerated queries:")
        for i, filters in enumerate(filter_tests):
            query = fetcher.build_overpass_query(bbox, filters)

            enabled_features = [k for k, v in filters.items() if v]
            print(f"\n  Test {i+1}: {', '.join(enabled_features)}")
            print(f"  Query length: {len(query)} chars")

            # Show first few lines
            lines = query.split('\n')[:5]
            for line in lines:
                print(f"    {line}")
            print("    ...")

        print("\n✅ Query building test passed!")
        return True

    except Exception as e:
        print(f"  ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_coordinate_transform():
    """Test WGS84 to UE5 coordinate transformation."""
    print("\n" + "="*60)
    print("Test: Coordinate Transform")
    print("="*60)

    try:
        # Create test data
        bbox = (-122.45, 37.75, -122.44, 37.76)
        heightmap = np.random.rand(512, 512).astype(np.float32) * 100  # 0-100m elevation

        converter = OSMToUE5Converter(bbox, heightmap)

        # Test coordinate transformation
        test_points = [
            ("SW corner", 37.75, -122.45),
            ("NE corner", 37.76, -122.44),
            ("Center", 37.755, -122.445),
        ]

        print("\nCoordinate transformations:")
        for name, lat, lon in test_points:
            x, y, z = converter.latlon_to_ue5(lat, lon)
            print(f"  {name}:")
            print(f"    Lat/Lon: ({lat:.4f}, {lon:.4f})")
            print(f"    UE5: X={x:,.0f} cm, Y={y:,.0f} cm, Z={z:,.0f} cm")
            print(f"         ({x/100:.0f} m, {y/100:.0f} m, {z/100:.0f} m)")

        print("\n✅ Coordinate transform test passed!")
        return True

    except Exception as e:
        print(f"  ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_building_conversion():
    """Test building conversion to UE5 format."""
    print("\n" + "="*60)
    print("Test: Building Conversion")
    print("="*60)

    try:
        bbox = (-122.45, 37.75, -122.44, 37.76)
        heightmap = np.random.rand(512, 512).astype(np.float32) * 100

        converter = OSMToUE5Converter(bbox, heightmap)

        # Create test building
        test_building = {
            'id': 123456,
            'geometry': [
                {'lat': 37.755, 'lon': -122.445},
                {'lat': 37.755, 'lon': -122.444},
                {'lat': 37.754, 'lon': -122.444},
                {'lat': 37.754, 'lon': -122.445},
                {'lat': 37.755, 'lon': -122.445},  # Close polygon
            ],
            'tags': {
                'building': 'residential',
                'building:levels': '3',
                'name': 'Test Building'
            }
        }

        # Convert
        print("\nConverting test building...")
        ue5_building = converter.convert_building(test_building)

        if ue5_building:
            print(f"  ✅ Building converted successfully")
            print(f"    OSM ID: {ue5_building['osm_id']}")
            print(f"    Position: ({ue5_building['position'][0]/100:.1f}m, "
                  f"{ue5_building['position'][1]/100:.1f}m, "
                  f"{ue5_building['position'][2]/100:.1f}m)")
            print(f"    Rotation: {ue5_building['rotation']:.1f}°")
            print(f"    Height: {ue5_building['height']/100:.1f} m")
            print(f"    Levels: {ue5_building['levels']}")
            print(f"    Type: {ue5_building['building_type']}")
            print(f"    Footprint points: {len(ue5_building['footprint'])}")

            print("\n✅ Building conversion test passed!")
            return True
        else:
            print("  ❌ Building conversion returned None")
            return False

    except Exception as e:
        print(f"  ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_road_conversion():
    """Test road conversion to UE5 spline format."""
    print("\n" + "="*60)
    print("Test: Road Conversion")
    print("="*60)

    try:
        bbox = (-122.45, 37.75, -122.44, 37.76)
        heightmap = np.random.rand(512, 512).astype(np.float32) * 100

        converter = OSMToUE5Converter(bbox, heightmap)

        # Create test road
        test_road = {
            'id': 789012,
            'geometry': [
                {'lat': 37.755, 'lon': -122.445},
                {'lat': 37.756, 'lon': -122.444},
                {'lat': 37.757, 'lon': -122.443},
            ],
            'tags': {
                'highway': 'residential',
                'name': 'Test Street',
                'lanes': '2'
            }
        }

        # Convert
        print("\nConverting test road...")
        ue5_road = converter.convert_road(test_road)

        if ue5_road:
            print(f"  ✅ Road converted successfully")
            print(f"    OSM ID: {ue5_road['osm_id']}")
            print(f"    Name: {ue5_road['name']}")
            print(f"    Highway type: {ue5_road['highway_type']}")
            print(f"    Width: {ue5_road['width']/100:.1f} m")
            print(f"    Lanes: {ue5_road['lanes']}")
            print(f"    Spline points: {len(ue5_road['spline_points'])}")

            # Show first point
            first_point = ue5_road['spline_points'][0]
            print(f"    First point: ({first_point[0]/100:.1f}m, "
                  f"{first_point[1]/100:.1f}m, {first_point[2]/100:.1f}m)")

            print("\n✅ Road conversion test passed!")
            return True
        else:
            print("  ❌ Road conversion returned None")
            return False

    except Exception as e:
        print(f"  ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_deduplication():
    """Test deduplication of overlapping chunks."""
    print("\n" + "="*60)
    print("Test: Deduplication")
    print("="*60)

    try:
        fetcher = OSMFetcher()

        # Create test data with duplicates
        test_data = {
            'nodes': [
                {'id': 1, 'lat': 37.75, 'lon': -122.45, 'tags': {}},
                {'id': 2, 'lat': 37.76, 'lon': -122.44, 'tags': {}},
                {'id': 1, 'lat': 37.75, 'lon': -122.45, 'tags': {}},  # Duplicate
                {'id': 3, 'lat': 37.77, 'lon': -122.43, 'tags': {}},
            ],
            'ways': [
                {'id': 100, 'nodes': [1, 2], 'tags': {}},
                {'id': 101, 'nodes': [2, 3], 'tags': {}},
                {'id': 100, 'nodes': [1, 2], 'tags': {}},  # Duplicate
            ],
            'relations': []
        }

        print(f"\nBefore deduplication:")
        print(f"  Nodes: {len(test_data['nodes'])}")
        print(f"  Ways: {len(test_data['ways'])}")

        # Deduplicate
        unique_data = fetcher.remove_duplicates(test_data)

        print(f"\nAfter deduplication:")
        print(f"  Nodes: {len(unique_data['nodes'])} (removed {len(test_data['nodes']) - len(unique_data['nodes'])})")
        print(f"  Ways: {len(unique_data['ways'])} (removed {len(test_data['ways']) - len(unique_data['ways'])})")

        if len(unique_data['nodes']) == 3 and len(unique_data['ways']) == 2:
            print("\n✅ Deduplication test passed!")
            return True
        else:
            print("\n❌ Unexpected deduplication results")
            return False

    except Exception as e:
        print(f"  ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_full_conversion_pipeline():
    """Test full OSM to UE5 conversion pipeline."""
    print("\n" + "="*60)
    print("Test: Full Conversion Pipeline")
    print("="*60)

    try:
        bbox = (-122.45, 37.75, -122.44, 37.76)
        heightmap = np.random.rand(512, 512).astype(np.float32) * 100

        # Create mock OSM data
        mock_osm_data = {
            'nodes': [
                {'id': 1, 'lat': 37.755, 'lon': -122.445, 'tags': {'amenity': 'cafe', 'name': 'Test Cafe'}},
                {'id': 2, 'lat': 37.756, 'lon': -122.444, 'tags': {'amenity': 'restaurant'}},
            ],
            'ways': [
                {
                    'id': 100,
                    'geometry': [
                        {'lat': 37.755, 'lon': -122.445},
                        {'lat': 37.755, 'lon': -122.444},
                        {'lat': 37.754, 'lon': -122.444},
                        {'lat': 37.754, 'lon': -122.445},
                        {'lat': 37.755, 'lon': -122.445},
                    ],
                    'tags': {'building': 'residential', 'building:levels': '2'}
                },
                {
                    'id': 101,
                    'geometry': [
                        {'lat': 37.755, 'lon': -122.445},
                        {'lat': 37.756, 'lon': -122.444},
                    ],
                    'tags': {'highway': 'residential', 'name': 'Test Street'}
                }
            ],
            'relations': []
        }

        print("\nConverting mock OSM data to UE5 format...")
        ue5_data = convert_osm_to_ue5(mock_osm_data, bbox, heightmap)

        print(f"\nConversion results:")
        print(f"  Buildings: {len(ue5_data['buildings'])}")
        print(f"  Roads: {len(ue5_data['roads'])}")
        print(f"  POIs: {len(ue5_data['pois'])}")

        # Verify results
        if len(ue5_data['buildings']) == 1:
            building = ue5_data['buildings'][0]
            print(f"\n  Sample building:")
            print(f"    Height: {building['height']/100:.1f} m")
            print(f"    Levels: {building['levels']}")

        if len(ue5_data['roads']) == 1:
            road = ue5_data['roads'][0]
            print(f"\n  Sample road:")
            print(f"    Name: {road['name']}")
            print(f"    Points: {len(road['spline_points'])}")

        if len(ue5_data['pois']) == 2:
            print(f"\n  POIs found: {len(ue5_data['pois'])}")

        print("\n✅ Full conversion pipeline test passed!")
        return True

    except Exception as e:
        print(f"  ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_statistics():
    """Test OSM data statistics."""
    print("\n" + "="*60)
    print("Test: Statistics")
    print("="*60)

    try:
        fetcher = OSMFetcher()

        # Create test data
        test_data = {
            'nodes': [
                {'id': 1, 'lat': 37.75, 'lon': -122.45, 'tags': {'amenity': 'cafe'}},
                {'id': 2, 'lat': 37.76, 'lon': -122.44, 'tags': {'amenity': 'restaurant'}},
            ],
            'ways': [
                {'id': 100, 'tags': {'highway': 'residential'}},
                {'id': 101, 'tags': {'highway': 'primary'}},
                {'id': 102, 'tags': {'building': 'residential'}},
                {'id': 103, 'tags': {'building': 'commercial'}},
                {'id': 104, 'tags': {'waterway': 'river'}},
            ],
            'relations': []
        }

        print("\nCalculating statistics...")
        stats = fetcher.get_statistics(test_data)

        print(f"\nStatistics:")
        print(f"  Total nodes: {stats['total_nodes']}")
        print(f"  Total ways: {stats['total_ways']}")
        print(f"  Total relations: {stats['total_relations']}")

        print(f"\n  Feature counts:")
        for feature, count in stats['feature_counts'].items():
            print(f"    {feature}: {count}")

        print("\n✅ Statistics test passed!")
        return True

    except Exception as e:
        print(f"  ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("OSM Fetcher & Converter Test Suite")
    print("="*60)

    results = []

    # Run tests
    results.append(("Area Calculation", test_area_calculation()))
    results.append(("Chunking Logic", test_chunking_logic()))
    results.append(("Query Building", test_query_building()))
    results.append(("Coordinate Transform", test_coordinate_transform()))
    results.append(("Building Conversion", test_building_conversion()))
    results.append(("Road Conversion", test_road_conversion()))
    results.append(("Deduplication", test_deduplication()))
    results.append(("Full Conversion Pipeline", test_full_conversion_pipeline()))
    results.append(("Statistics", test_statistics()))

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
        print("\nNote: These tests use mock data. To test with real OSM data:")
        print("  1. Ensure internet connection")
        print("  2. Use small bounding box (< 1 km²)")
        print("  3. Be respectful of Overpass API rate limits")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")


if __name__ == "__main__":
    main()
