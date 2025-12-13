#### TASK-1106: Road Details & Infrastructure ⭐ NEW
**Status:** `[ ]` TODO  
**Priority:** MEDIUM  
**Estimated Time:** 4 hours  
**Agent Model:** Opus 4

**Description:**
Generate detailed road infrastructure: sidewalks, curbs, road signs, guard rails, and all street furniture.

**COMPLETE ROAD SYSTEM:**

```python
class RoadDetailsGenerator:
    """
    Generate all road details automatically based on road type
    """
    
    def generate_complete_road(self, road_spline_data):
        """
        Generate everything needed for a realistic road
        """
        return {
            'base_spline': road_spline_data,
            
            # Road surface layers
            'surface': self.generate_road_surface(road_spline_data),
            
            # Sidewalks (Trottoarer)
            'sidewalks': self.generate_sidewalks(road_spline_data),
            
            # Curbs (Kantsten/Kantkäppar)
            'curbs': self.generate_curbs(road_spline_data),
            
            # Road markings (Lane lines, arrows, crosswalks)
            'markings': self.generate_road_markings(road_spline_data),
            
            # Guard rails (Vägräcken)
            'guard_rails': self.generate_guard_rails(road_spline_data),
            
            # Road signs (Skyltar)
            'signs': self.generate_road_signs(road_spline_data),
            
            # Street lights
            'street_lights': self.generate_street_lights(road_spline_data),
            
            # Traffic signals
            'traffic_signals': self.generate_traffic_signals(road_spline_data),
            
            # Utility poles
            'utility_poles': self.generate_utility_poles(road_spline_data),
            
            # Street furniture
            'furniture': self.generate_street_furniture(road_spline_data),
            
            # Drainage
            'drainage': self.generate_drainage(road_spline_data)
        }
    
    def generate_sidewalks(self, road_data):
        """
        Generate sidewalks (trottoarer) along road
        
        Swedish standard sidewalk: 1.5-2.5m wide
        """
        sidewalks = []
        
        # Check if road should have sidewalks
        road_type = road_data['highway']
        
        SIDEWALK_RULES = {
            'motorway': None,           # No sidewalks on highways
            'trunk': None,
            'primary': 'both',          # Both sides
            'secondary': 'both',
            'tertiary': 'both',
            'residential': 'both',
            'service': None,
            'track': None,
            'path': None
        }
        
        sidewalk_config = SIDEWALK_RULES.get(road_type)
        
        # Check OSM tags (override defaults)
        if 'sidewalk' in road_data.get('tags', {}):
            sidewalk_config = road_data['tags']['sidewalk']
            # Values: 'both', 'left', 'right', 'no', 'separate'
        
        if not sidewalk_config or sidewalk_config == 'no':
            return []
        
        # Get sidewalk width
        sidewalk_width = float(road_data.get('tags', {}).get('sidewalk:width', 200))  # cm
        
        # Standard Swedish sidewalk: 2m (200cm)
        if sidewalk_width < 100:
            sidewalk_width = 200
        
        # Generate left sidewalk
        if sidewalk_config in ['both', 'left']:
            left_sidewalk = self.create_sidewalk_spline(
                road_data['points'],
                side='left',
                width=sidewalk_width,
                offset=road_data['width'] / 2 + 15  # 15cm curb
            )
            sidewalks.append(left_sidewalk)
        
        # Generate right sidewalk
        if sidewalk_config in ['both', 'right']:
            right_sidewalk = self.create_sidewalk_spline(
                road_data['points'],
                side='right',
                width=sidewalk_width,
                offset=road_data['width'] / 2 + 15
            )
            sidewalks.append(right_sidewalk)
        
        return sidewalks
    
    def create_sidewalk_spline(self, road_points, side, width, offset):
        """
        Create parallel spline for sidewalk
        """
        sidewalk_points = []
        
        for i, point in enumerate(road_points):
            # Get tangent (direction along road)
            if i < len(road_points) - 1:
                tangent = normalize(subtract(road_points[i+1], point))
            else:
                tangent = normalize(subtract(point, road_points[i-1]))
            
            # Get perpendicular (sideways)
            perpendicular = get_perpendicular(tangent)
            
            # Offset to side
            side_multiplier = 1 if side == 'right' else -1
            sidewalk_center = add(point, multiply(perpendicular, offset * side_multiplier))
            
            sidewalk_points.append(sidewalk_center)
        
        return {
            'type': 'sidewalk',
            'side': side,
            'points': sidewalk_points,
            'width': width,
            'material': 'concrete_sidewalk',  # Or 'brick_pavers', 'asphalt'
            'texture': 'T_Sidewalk_Concrete',
            
            # Details
            'has_tactile_paving': True,  # At crossings
            'tree_pits': self.calculate_tree_pit_positions(sidewalk_points),
            'benches': self.calculate_bench_positions(sidewalk_points),
            'trash_bins': self.calculate_trash_bin_positions(sidewalk_points)
        }
    
    def generate_curbs(self, road_data):
        """
        Generate curbs (kantsten) - Swedish standard: 15cm high
        
        Curbs separate road from sidewalk
        """
        curbs = []
        
        # Only roads with sidewalks have curbs
        if not road_data.get('has_sidewalk'):
            return []
        
        # Swedish standard curb
        CURB_HEIGHT = 15  # cm
        CURB_WIDTH = 20   # cm
        
        # Get curb style from tags
        curb_style = road_data.get('tags', {}).get('curb', 'standard')
        # Types: 'standard', 'lowered', 'flush', 'raised'
        
        if curb_style == 'lowered':
            CURB_HEIGHT = 3  # Wheelchair accessible
        elif curb_style == 'flush':
            CURB_HEIGHT = 0  # Shared space
        elif curb_style == 'raised':
            CURB_HEIGHT = 20  # Higher for drainage
        
        # Generate curb on both sides
        for side in ['left', 'right']:
            curb_points = []
            
            for i, point in enumerate(road_data['points']):
                # Get perpendicular direction
                if i < len(road_data['points']) - 1:
                    tangent = normalize(subtract(road_data['points'][i+1], point))
                else:
                    tangent = normalize(subtract(point, road_data['points'][i-1]))
                
                perpendicular = get_perpendicular(tangent)
                
                # Offset to edge of road
                side_multiplier = 1 if side == 'right' else -1
                edge_offset = road_data['width'] / 2
                
                curb_position = add(point, multiply(perpendicular, edge_offset * side_multiplier))
                
                # Raise curb above road surface
                curb_position[2] += CURB_HEIGHT
                
                curb_points.append(curb_position)
            
            # Lower curbs at crossings
            crossing_positions = self.find_crossing_positions(road_data)
            curb_points = self.lower_curbs_at_crossings(curb_points, crossing_positions)
            
            curbs.append({
                'side': side,
                'points': curb_points,
                'height': CURB_HEIGHT,
                'width': CURB_WIDTH,
                'style': curb_style,
                'material': 'granite',  # Swedish standard
                'color': 'gray',
                
                # Drainage
                'has_drainage_slots': True,
                'drainage_interval': 500  # Every 5m
            })
        
        return curbs
    
    def generate_guard_rails(self, road_data):
        """
        Generate guard rails (vägräcken) - Swedish standard: W-beam barriers
        
        Guard rails needed on:
        - Curves with speed >70 km/h
        - Embankments >3m drop
        - Bridge approaches
        - Near obstacles (trees, poles)
        """
        guard_rails = []
        
        road_type = road_data['highway']
        max_speed = int(road_data.get('maxspeed', '50'))
        
        # Determine if guard rails needed
        needs_guard_rail = (
            road_type in ['motorway', 'trunk', 'primary'] or
            max_speed >= 70 or
            road_data.get('tags', {}).get('barrier') == 'guard_rail'
        )
        
        if not needs_guard_rail:
            return []
        
        # Analyze road for dangerous sections
        dangerous_sections = []
        
        for i in range(len(road_data['points']) - 2):
            # Check curve radius
            radius = calculate_curve_radius(
                road_data['points'][i],
                road_data['points'][i+1],
                road_data['points'][i+2]
            )
            
            # Sharp curve at high speed = dangerous
            if radius < 200 and max_speed >= 70:
                dangerous_sections.append({
                    'start': i,
                    'end': i+2,
                    'reason': 'sharp_curve',
                    'side': 'outside'  # Outside of curve
                })
            
            # Check elevation drop (embankment)
            if i > 0:
                elevation_change = road_data['points'][i][2] - road_data['points'][i-1][2]
                if abs(elevation_change) > 300:  # 3m drop
                    dangerous_sections.append({
                        'start': i-1,
                        'end': i+1,
                        'reason': 'embankment',
                        'side': 'drop_side'
                    })
        
        # Merge overlapping sections
        merged_sections = self.merge_overlapping_sections(dangerous_sections)
        
        # Generate guard rail for each section
        for section in merged_sections:
            start_idx = section['start']
            end_idx = section['end']
            
            # Extend section by 20m on each side (safety margin)
            start_idx = max(0, start_idx - 5)
            end_idx = min(len(road_data['points']) - 1, end_idx + 5)
            
            section_points = road_data['points'][start_idx:end_idx+1]
            
            # Offset to side of road
            side_multiplier = 1 if section['side'] == 'right' else -1
            offset = road_data['width'] / 2 + 100  # 1m from road edge
            
            rail_points = []
            for i, point in enumerate(section_points):
                tangent = normalize(subtract(section_points[min(i+1, len(section_points)-1)], point))
                perpendicular = get_perpendicular(tangent)
                
                rail_position = add(point, multiply(perpendicular, offset * side_multiplier))
                
                # Guard rail height: 70cm (Swedish standard)
                rail_position[2] += 70
                
                rail_points.append(rail_position)
            
            guard_rails.append({
                'type': 'guard_rail',
                'style': 'w_beam',  # Swedish standard: W-beam
                'points': rail_points,
                'height': 70,  # cm
                'reason': section['reason'],
                
                # W-beam specific
                'beam_sections': len(rail_points) - 1,
                'post_spacing': 400,  # Posts every 4m
                'post_type': 'steel_i_beam',
                'reflectors': True,  # Reflective strips
                'end_treatment': 'crashworthy',  # Safety ends
                
                # Visual
                'material': 'galvanized_steel',
                'color': 'silver',
                'weathering': 0.3  # Some rust/wear
            })
        
        return guard_rails
    
    def generate_road_signs(self, road_data):
        """
        Generate road signs (vägskyltar) based on Swedish standards
        
        Types:
        - Speed limits (Hastighet)
        - Warning signs (Varning)
        - Mandatory signs (Påbud)
        - Information signs (Information)
        """
        signs = []
        
        road_type = road_data['highway']
        road_name = road_data.get('name', '')
        max_speed = road_data.get('maxspeed', '')
        
        # 1. Speed limit signs
        if max_speed:
            # Place speed limit sign at start of road
            sign_position = road_data['points'][0]
            
            # Offset to right side
            tangent = normalize(subtract(road_data['points'][1], road_data['points'][0]))
            perpendicular = get_perpendicular(tangent)
            sign_position = add(sign_position, multiply(perpendicular, road_data['width']/2 + 250))
            
            signs.append({
                'type': 'speed_limit',
                'position': sign_position,
                'rotation': calculate_sign_rotation(tangent),
                'speed': max_speed,
                'sign_id': 'C31',  # Swedish traffic sign code
                'size': 'standard',  # 60cm diameter
                'height': 200,  # 2m pole height
                'reflective': True
            })
            
            # Repeat speed limit sign every 2km
            road_length = calculate_spline_length(road_data['points'])
            for distance in range(2000, int(road_length), 2000):
                pos, tangent = get_point_at_distance(road_data['points'], distance)
                perp = get_perpendicular(tangent)
                sign_pos = add(pos, multiply(perp, road_data['width']/2 + 250))
                
                signs.append({
                    'type': 'speed_limit',
                    'position': sign_pos,
                    'rotation': calculate_sign_rotation(tangent),
                    'speed': max_speed,
                    'sign_id': 'C31',
                    'size': 'standard',
                    'height': 200
                })
        
        # 2. Street name signs
        if road_name:
            # Place at intersections (found separately)
            for intersection in road_data.get('intersections', []):
                signs.append({
                    'type': 'street_name',
                    'position': intersection['position'],
                    'text': road_name,
                    'style': 'blue_white',  # Swedish standard
                    'size': [100, 20],  # 1m x 0.2m
                    'height': 250  # 2.5m
                })
        
        # 3. Warning signs on curves
        for i in range(len(road_data['points']) - 2):
            radius = calculate_curve_radius(
                road_data['points'][i],
                road_data['points'][i+1],
                road_data['points'][i+2]
            )
            
            # Sharp curve warning (Swedish sign A5)
            if radius < 300:  # Tight curve
                # Place sign 100m before curve
                if i >= 10:
                    sign_pos = road_data['points'][i-10]
                    tangent = normalize(subtract(road_data['points'][i-9], sign_pos))
                    perp = get_perpendicular(tangent)
                    sign_pos = add(sign_pos, multiply(perp, road_data['width']/2 + 250))
                    
                    # Determine curve direction
                    curve_direction = 'right' if radius > 0 else 'left'
                    
                    signs.append({
                        'type': 'warning_curve',
                        'position': sign_pos,
                        'rotation': calculate_sign_rotation(tangent),
                        'direction': curve_direction,
                        'sign_id': 'A5-1' if curve_direction == 'right' else 'A5-2',
                        'size': 'large',  # 90cm triangle
                        'height': 200
                    })
        
        # 4. Stop signs at intersections
        for intersection in road_data.get('intersections', []):
            if intersection.get('traffic_control') == 'stop':
                signs.append({
                    'type': 'stop',
                    'position': intersection['position'],
                    'sign_id': 'B2',  # Swedish STOP sign
                    'size': 'standard',  # 60cm octagon
                    'height': 200,
                    'stop_line_distance': 300  # 3m before intersection
                })
        
        # 5. Yield signs
        for intersection in road_data.get('intersections', []):
            if intersection.get('traffic_control') == 'yield':
                signs.append({
                    'type': 'yield',
                    'position': intersection['position'],
                    'sign_id': 'B3',  # Swedish yield sign
                    'size': 'standard',  # 90cm inverted triangle
                    'height': 200
                })
        
        # 6. Pedestrian crossing signs
        crossings = self.find_crossing_positions(road_data)
        for crossing in crossings:
            # Warning sign 50m before crossing
            sign_pos = get_point_at_distance(road_data['points'], crossing['distance'] - 50)[0]
            tangent = get_point_at_distance(road_data['points'], crossing['distance'] - 50)[1]
            perp = get_perpendicular(tangent)
            sign_pos = add(sign_pos, multiply(perp, road_data['width']/2 + 250))
            
            signs.append({
                'type': 'pedestrian_crossing',
                'position': sign_pos,
                'sign_id': 'A7',  # Swedish pedestrian warning
                'size': 'standard',
                'height': 200
            })
        
        # 7. No parking signs (if tagged)
        if road_data.get('tags', {}).get('parking:lane:both') == 'no_stopping':
            # Place every 50m
            road_length = calculate_spline_length(road_data['points'])
            for distance in range(0, int(road_length), 5000):
                pos, tangent = get_point_at_distance(road_data['points'], distance)
                perp = get_perpendicular(tangent)
                sign_pos = add(pos, multiply(perp, road_data['width']/2 + 250))
                
                signs.append({
                    'type': 'no_stopping',
                    'position': sign_pos,
                    'sign_id': 'C38',  # Swedish no stopping sign
                    'size': 'small',  # 40cm diameter
                    'height': 200
                })
        
        return signs
    
    def generate_road_markings(self, road_data):
        """
        Generate road markings (vägmarkeringar)
        
        Swedish standards:
        - Center line: Dashed white (3m dash, 6m gap)
        - Edge line: Solid white
        - Lane dividers: Dashed white
        - No passing: Solid yellow
        - Crosswalks: White zebra stripes
        """
        markings = {
            'center_line': [],
            'edge_lines': [],
            'lane_dividers': [],
            'arrows': [],
            'crosswalks': [],
            'stop_lines': []
        }
        
        lanes = road_data.get('lanes', 2)
        width = road_data['width']
        oneway = road_data.get('oneway', False)
        
        # 1. Center line (if two-way road)
        if not oneway and lanes >= 2:
            markings['center_line'] = self.generate_center_line(
                road_data['points'],
                style='dashed',  # Dashed = passing allowed
                color='white',
                width=10,  # 10cm wide
                dash_length=300,  # 3m
                gap_length=600   # 6m
            )
        
        # 2. Edge lines (both sides)
        for side in ['left', 'right']:
            side_mult = 1 if side == 'right' else -1
            edge_offset = width / 2 - 15  # 15cm from edge
            
            markings['edge_lines'].append(
                self.generate_edge_line(
                    road_data['points'],
                    side=side,
                    offset=edge_offset * side_mult,
                    style='solid',
                    color='white',
                    width=10
                )
            )
        
        # 3. Lane dividers (if more than 2 lanes)
        if lanes > 2:
            lanes_per_direction = lanes // 2 if not oneway else lanes
            lane_width = width / lanes
            
            for lane_num in range(1, lanes_per_direction):
                offset = -width/2 + lane_num * lane_width
                
                markings['lane_dividers'].append(
                    self.generate_lane_divider(
                        road_data['points'],
                        offset=offset,
                        style='dashed_short',  # 1.5m dash, 1.5m gap
                        color='white',
                        width=10
                    )
                )
        
        # 4. Arrows (at intersections)
        for intersection in road_data.get('intersections', []):
            # Place arrow 20m before intersection
            arrow_pos = get_point_at_distance(
                road_data['points'],
                intersection['distance'] - 2000
            )[0]
            
            # Determine arrow type based on intersection
            arrow_types = self.determine_arrow_types(intersection, road_data)
            
            for arrow_type in arrow_types:
                markings['arrows'].append({
                    'type': arrow_type,  # 'straight', 'left', 'right', 'straight_left', etc
                    'position': arrow_pos,
                    'rotation': intersection['entry_angle'],
                    'size': [150, 400],  # 1.5m x 4m
                    'color': 'white'
                })
        
        # 5. Crosswalks (zebra crossings)
        crossings = self.find_crossing_positions(road_data)
        for crossing in crossings:
            crossing_pos = crossing['position']
            
            markings['crosswalks'].append({
                'position': crossing_pos,
                'width': width,  # Full road width
                'stripe_width': 50,  # 50cm white stripes
                'stripe_gap': 50,    # 50cm gaps
                'num_stripes': int(width / 100),  # One per meter
                'style': 'zebra',
                'color': 'white',
                'reflective': True  # Better visibility at night
            })
        
        # 6. Stop lines (at intersections with stop signs)
        for intersection in road_data.get('intersections', []):
            if intersection.get('traffic_control') == 'stop':
                stop_line_pos = get_point_at_distance(
                    road_data['points'],
                    intersection['distance'] - 300  # 3m before intersection
                )[0]
                
                markings['stop_lines'].append({
                    'position': stop_line_pos,
                    'width': width,
                    'line_width': 30,  # 30cm thick line
                    'color': 'white',
                    'style': 'solid'
                })
        
        return markings
    
    def generate_street_furniture(self, road_data):
        """
        Generate street furniture along sidewalks
        
        Swedish urban furniture:
        - Benches (Bänkar)
        - Trash bins (Papperskorgar)
        - Bicycle racks (Cykelställ)
        - Bus stops (Busshållplatser)
        - Phone booths (rare now)
        - Bollards (Pollare)
        """
        furniture = {
            'benches': [],
            'trash_bins': [],
            'bike_racks': [],
            'bus_stops': [],
            'bollards': []
        }
        
        road_type = road_data['highway']
        
        # Only urban roads get street furniture
        if road_type not in ['residential', 'tertiary', 'secondary', 'primary']:
            return furniture
        
        # Benches every 50-100m on residential streets
        if road_type == 'residential':
            road_length = calculate_spline_length(road_data['points'])
            
            for distance in range(5000, int(road_length), random.randint(5000, 10000)):
                pos, tangent = get_point_at_distance(road_data['points'], distance)
                perp = get_perpendicular(tangent)
                
                # Place on sidewalk
                bench_pos = add(pos, multiply(perp, road_data['width']/2 + 200))
                
                furniture['benches'].append({
                    'position': bench_pos,
                    'rotation': calculate_furniture_rotation(tangent),
                    'type': 'swedish_park_bench',  # Typical Swedish design
                    'material': 'wood',
                    'length': 150,  # 1.5m
                    'has_backrest': True,
                    'weathering': 0.4
                })
        
        # Trash bins every 30-50m
        road_length = calculate_spline_length(road_data['points'])
        for distance in range(3000, int(road_length), random.randint(3000, 5000)):
            pos, tangent = get_point_at_distance(road_data['points'], distance)
            perp = get_perpendicular(tangent)
            
            bin_pos = add(pos, multiply(perp, road_data['width']/2 + 150))
            
            furniture['trash_bins'].append({
                'position': bin_pos,
                'type': 'street_bin',
                'capacity': 50,  # liters
                'color': 'green',  # Swedish standard
                'has_lid': True,
                'has_ashtray': True
            })
        
        # Bike racks near shops/amenities (if tagged)
        if 'bicycle_parking' in road_data.get('tags', {}):
            # Place bike rack
            furniture['bike_racks'].append({
                'position': road_data['points'][len(road_data['points'])//2],
                'type': 'wheel_holder',  # Swedish: hjulhållare
                'capacity': 10,  # bikes
                'covered': False
            })
        
        # Bus stops (if tagged)
        if 'bus' in road_data.get('tags', {}).get('public_transport', ''):
            furniture['bus_stops'].append({
                'position': road_data.get('bus_stop_position'),
                'type': 'bus_shelter',
                'has_seating': True,
                'has_timetable': True,
                'has_heating': True,  # Common in Sweden!
                'covered': True
            })
        
        return furniture
```

**EXPORT TO .rterrain:**

```json
{
  "road_details": {
    "road_id": "way_12345",
    
    "sidewalks": [
      {
        "side": "left",
        "width": 200,
        "material": "concrete",
        "tree_pits": [...],
        "tactile_paving_zones": [...]
      },
      {
        "side": "right",
        "width": 200,
        "material": "concrete"
      }
    ],
    
    "curbs": [
      {
        "side": "left",
        "height": 15,
        "style": "standard",
        "lowered_sections": [
          {"start": 45.2, "end": 48.5}  // Crossing
        ]
      }
    ],
    
    "guard_rails": [
      {
        "start_distance": 234.5,
        "end_distance": 567.8,
        "side": "right",
        "type": "w_beam",
        "post_spacing": 400,
        "reason": "sharp_curve"
      }
    ],
    
    "road_signs": [
      {
        "type": "speed_limit",
        "position": [125340, 234560, 4780],
        "rotation": [0, 45, 0],
        "sign_id": "C31",
        "speed": "50",
        "size": "standard"
      },
      {
        "type": "warning_curve",
        "sign_id": "A5-1",
        "direction": "right"
      }
    ],
    
    "markings": {
      "center_line": {
        "style": "dashed",
        "color": "white",
        "segments": [...]
      },
      "crosswalks": [
        {
          "position": [126000, 235000, 4590],
          "width": 700,
          "style": "zebra"
        }
      ]
    }
  }
}
```

**UE5 IMPORT:**

```cpp
void ImportRoadDetails(FRoadData Road, FRoadDetails Details)
{
    // 1. Create sidewalks
    for (FSidewalk& Sidewalk : Details.Sidewalks)
    {
        USplineComponent* SidewalkSpline = CreateSpline(Sidewalk.Points);
        UStaticMesh* SidewalkMesh = LoadAsset<UStaticMesh>("SM_Sidewalk");
        
        CreateSplineMesh(SidewalkSpline, SidewalkMesh, Sidewalk.Width);
        ApplyMaterial(SidewalkSpline, Sidewalk.Material);
    }
    
    // 2. Create curbs
    for (FCurb& Curb : Details.Curbs)
    {
        USplineComponent* CurbSpline = CreateSpline(Curb.Points);
        UStaticMesh* CurbMesh = LoadAsset<UStaticMesh>("SM_Curb_Granite");
        
        // Curbs are small, use instanced static mesh
        for (FVector& Point : Curb.Points)
        {
            SpawnInstancedMesh(CurbMesh, Point, Curb.# 📋 REALTERRAIN STUDIO - TASKS

**Project:** RealTerrain Studio  
**Tagline:** "From Earth to Engine"  
**Sprint:** Pre-Launch Development  

---

## 🎯 HOW TO USE THIS FILE

### For User (You):
1. Review tasks in current sprint
2. When ready, tell Claude Code: "Start Task X"
3. Claude Code will mark it IN_PROGRESS
4. When done, Claude marks it DONE
5. Review and approve before moving to next task

### For Agent (Claude Code):
1. **ALWAYS check this file before starting work**
2. Mark task as IN_PROGRESS when starting
3. Update progress notes as you work
4. Mark as DONE when complete
5. Update CHANGELOG.md
6. Ask user before moving to next major task

---

## 📊 TASK STATUS LEGEND

- `[ ]` TODO - Not started
- `[~]` IN_PROGRESS - Currently working on this
- `[✓]` DONE - Completed and tested
- `[!]` BLOCKED - Waiting on something
- `[?]` QUESTION - Needs clarification

---

## 🚀 SPRINT 1: PROJECT SETUP (Week 1)

**Goal:** Get basic project structure and development environment ready

### Setup & Configuration

#### TASK-001: Initialize Project Structure
**Status:** `[ ]` TODO  
**Priority:** HIGH  
**Estimated Time:** 30 minutes  
**Agent Model:** Sonnet 4.5

**Description:**
Create the complete folder structure for RealTerrain Studio project.

**Requirements:**
- Create root folder: `RealTerrainStudio/`
- Create subfolders: `qgis-plugin/`, `ue5-plugin/`, `backend/`, `website/`, `docs/`, `tests/`
- Create essential files: `README.md`, `CHANGELOG.md`, `.gitignore`
- Initialize git repository
- Create folder structure for each plugin

**Acceptance Criteria:**
- [ ] All folders created
- [ ] Git initialized
- [ ] README.md with project overview
- [ ] .gitignore includes Python, C++, and IDE files

**Notes:**
```
User needs to: Just approve the structure
No coding knowledge required
```

---

#### TASK-002: Setup Python Virtual Environment
**Status:** `[ ]` TODO  
**Priority:** HIGH  
**Estimated Time:** 20 minutes  
**Agent Model:** Sonnet 4.5

**Description:**
Create Python virtual environment for QGIS plugin development.

**Requirements:**
- Create venv in `qgis-plugin/` folder
- Install QGIS dependencies
- Create `requirements.txt` with pinned versions
- Create activation instructions for user

**Acceptance Criteria:**
- [ ] Virtual environment created
- [ ] requirements.txt with all dependencies
- [ ] Clear instructions in README for user to activate venv

**Commands for User:**
```bash
cd qgis-plugin
python -m venv venv
source venv/bin/activate  # Mac/Linux
# OR
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

---

#### TASK-003: Setup Supabase Project
**Status:** `[ ]` TODO  
**Priority:** HIGH  
**Estimated Time:** 45 minutes  
**Agent Model:** Opus 4 (Architecture)

**Description:**
Initialize Supabase backend for licensing and data storage.

**Requirements:**
- Create Supabase project setup guide
- Design database schema (SQL files)
- Create initial tables: users, licenses, hardware_activations
- Setup Row Level Security (RLS) policies
- Create environment variable template

**Acceptance Criteria:**
- [ ] SQL migration files in `backend/supabase/migrations/`
- [ ] RLS policies defined
- [ ] `.env.example` file with required variables
- [ ] Setup instructions for user

**User Actions Required:**
1. Create Supabase account at supabase.com
2. Create new project
3. Copy project URL and API keys
4. Run SQL migrations in Supabase dashboard

---

#### TASK-004: Setup VS Code Workspace
**Status:** `[ ]` TODO  
**Priority:** MEDIUM  
**Estimated Time:** 15 minutes  
**Agent Model:** Sonnet 4.5

**Description:**
Create VS Code workspace configuration with recommended extensions.

**Requirements:**
- Create `.vscode/` folder
- Add `settings.json` with Python/C++ config
- Add `extensions.json` with recommended extensions
- Add `launch.json` for debugging

**Acceptance Criteria:**
- [ ] Workspace settings configured
- [ ] Extension recommendations listed
- [ ] Debug configurations added

---

## 🏗️ SPRINT 2: QGIS PLUGIN FOUNDATION (Week 2)

**Goal:** Create basic QGIS plugin that can be loaded

### Core Plugin Structure

#### TASK-101: Create QGIS Plugin Skeleton
**Status:** `[ ]` TODO  
**Priority:** HIGH  
**Estimated Time:** 1 hour  
**Agent Model:** Sonnet 4.5

**Description:**
Create the basic QGIS plugin structure that can be loaded in QGIS.

**Requirements:**
- Create `metadata.txt` with plugin info
- Create `__init__.py` with plugin class
- Create main plugin file `realterrain_studio.py`
- Add plugin icon
- Create basic menu entry in QGIS

**Acceptance Criteria:**
- [ ] Plugin loads without errors in QGIS
- [ ] Appears in QGIS Plugins menu
- [ ] Has icon and proper metadata
- [ ] Shows "Hello World" message when activated

**Testing Instructions for User:**
1. Copy plugin folder to QGIS plugins directory
2. Open QGIS
3. Go to Plugins → Manage and Install Plugins
4. Enable "RealTerrain Studio"
5. Check Plugins menu for new entry

---

#### TASK-102: Create Main Dialog UI with Game Profile System
**Status:** `[ ]` TODO  
**Priority:** HIGH  
**Estimated Time:** 4 hours  
**Agent Model:** Opus 4

**Description:**
Build the main user interface dialog using PyQt5 with intelligent Game Profile wizard.

**GAME PROFILE SYSTEM** ⭐ **NEW FEATURE**

**Step 1: Profile Selection (Wizard Start)**
User sees friendly question: **"What type of project are you creating?"**

**Available Profiles:**

**🎮 GAME PROFILES:**
1. **Military Simulation / Tactical Shooter**
   - Examples: Arma, Squad, Ground Branch, Insurgency
   - Icon: 🎖️
   
2. **Open World / RPG**
   - Examples: Skyrim, Witcher, GTA, RDR2
   - Icon: 🗺️
   
3. **Racing / Driving Game**
   - Examples: Forza Horizon, Gran Turismo, Need for Speed
   - Icon: 🏎️
   
4. **Survival / Crafting**
   - Examples: Rust, DayZ, The Forest, Minecraft-like
   - Icon: ⛺
   
5. **Flight Simulator**
   - Examples: MSFS, X-Plane, DCS
   - Icon: ✈️
   
6. **Battle Royale**
   - Examples: PUBG, Fortnite, Apex Legends
   - Icon: 🎯
   
7. **City Builder / Strategy**
   - Examples: Cities Skylines, Anno, Civilization
   - Icon: 🏙️
   
8. **Horror / Atmospheric**
   - Examples: Silent Hill, Resident Evil, Outlast
   - Icon: 👻
   
9. **Multiplayer Shooter (Non-tactical)**
   - Examples: Battlefield, Call of Duty, Halo
   - Icon: 🔫

**🎨 NON-GAME PROFILES:**
10. **Architectural Visualization**
    - Real estate, urban planning, presentations
    - Icon: 🏗️
    
11. **Film / Virtual Production**
    - Background plates, previsualization, LED walls
    - Icon: 🎬
    
12. **Education / Research**
    - Geography, geology, simulation, teaching
    - Icon: 🎓
    
13. **Custom / Advanced**
    - Full manual control for power users
    - Icon: 🔧

**Step 2: Auto-Configuration Based on Profile**

Each profile automatically enables/disables features:

```python
# Example: Military Simulation Profile
MILSIM_PROFILE = {
    "name": "Military Simulation / Tactical Shooter",
    "description": "Realistic terrain for tactical games like Arma, Squad",
    
    # Data Sources
    "elevation": {
        "enabled": True,
        "resolution": 5,  # 5m (high detail)
        "source": "best_available"  # LiDAR if possible
    },
    "satellite": {
        "enabled": True,
        "resolution": 1,  # 1m imagery
        "prefer_recent": True
    },
    "osm_data": {
        "enabled": True,
        "features": [
            "roads", "buildings", "railways", 
            "power_lines", "fences", "bridges"
        ]
    },
    
    # Materials
    "materials": {
        "enabled": True,
        "types": ["grass", "dirt", "rock", "forest", "sand", "gravel"]
    },
    
    # Special Features
    "tactical_analysis": True,  # 🎖️ Key feature!
    "fortifications": {
        "enabled": True,
        "level": "medium",  # light/medium/heavy/extreme
        "types": [
            "hesco_barriers",
            "sandbags", 
            "trenches",
            "roadblocks",
            "speed_bumps",
            "wire_obstacles"
        ]
    },
    "cover_analysis": True,
    "spawn_points": {
        "player_spawns": True,
        "enemy_spawns": True,
        "objective_markers": True
    },
    "navmesh_hints": True,
    
    # Optimization
    "collision_mesh": "detailed",
    "lod_levels": 4,
    
    # Tips shown to user
    "tips": [
        "✅ Tactical analysis enabled - AI will suggest defensive positions",
        "✅ Fortifications will be auto-placed at strategic points",
        "✅ Cover analysis will mark bullet-stopping objects",
        "💡 Recommended: Use 'medium' fortification level for balanced gameplay",
        "💡 Check spawn point suggestions in tactical_data.json after export"
    ],
    
    # Recommended UE5 settings
    "ue5_recommendations": {
        "landscape_material": "Military_Master",
        "collision": "High_Detail",
        "streaming": "World_Partition"
    }
}

# Example: Open World RPG Profile
OPEN_WORLD_PROFILE = {
    "name": "Open World / RPG",
    "description": "Vast explorable worlds with diverse biomes",
    
    "elevation": {
        "enabled": True,
        "resolution": 10,  # 10m (balanced)
        "source": "srtm"
    },
    "satellite": {
        "enabled": True,
        "resolution": 2,
        "color_grading": "vibrant"  # More fantasy-like
    },
    "osm_data": {
        "enabled": True,
        "features": ["roads", "buildings", "water", "forests", "landmarks"]
    },
    
    "materials": {
        "enabled": True,
        "types": ["grass", "dirt", "rock", "forest", "snow", "sand", "water"]
    },
    
    # Special Features
    "seasonal_variations": True,  # 4 seasons!
    "vegetation_distribution": True,
    "trail_generation": True,  # Hiking paths
    "poi_suggestions": True,  # Points of interest
    "biome_transitions": True,
    
    "procedural_buildings": {
        "enabled": True,
        "style": "regional",
        "density": "medium"
    },
    
    "scatter_objects": {
        "enabled": True,
        "types": ["rocks", "logs", "flowers", "bushes"]
    },
    
    "tips": [
        "✅ Seasonal variations enabled - 4 versions of terrain",
        "✅ Trail network will connect interesting locations",
        "✅ Biome transitions will blend naturally",
        "💡 Consider using 'vibrant' color grading for fantasy feel",
        "💡 POI suggestions will mark scenic viewpoints and quest locations"
    ]
}

# Example: Racing Game Profile
RACING_PROFILE = {
    "name": "Racing / Driving Game",
    "description": "Optimized road networks and race tracks",
    
    "elevation": {
        "enabled": True,
        "resolution": 5,
        "source": "srtm"
    },
    "satellite": {
        "enabled": True,
        "resolution": 1
    },
    "osm_data": {
        "enabled": True,
        "features": ["roads", "highways", "tracks", "buildings", "landmarks"],
        "road_detail": "maximum"  # Extra road data
    },
    
    "materials": {
        "enabled": True,
        "types": ["asphalt", "dirt", "gravel", "grass", "concrete"]
    },
    
    # Special Features
    "road_network_enhancement": True,
    "racing_track_analysis": {
        "enabled": True,
        "corner_analysis": True,
        "track_suggestions": True,
        "checkpoint_placement": True
    },
    "collision_mesh": "road_optimized",
    
    "procedural_details": {
        "guard_rails": True,
        "road_signs": True,
        "street_lights": True,
        "barriers": True
    },
    
    "tips": [
        "✅ Road network enhanced with proper width and markings",
        "✅ Corner analysis will rate difficulty of turns",
        "✅ Track suggestions for point-to-point and circuit races",
        "💡 Guard rails auto-placed on dangerous curves",
        "💡 Check racing_analysis.json for lap time estimates"
    ]
}
```

**Step 3: Configuration Preview**

Show user what will be enabled:
```
┌─────────────────────────────────────────┐
│  Profile: Military Simulation           │
├─────────────────────────────────────────┤
│                                         │
│  ✅ High-resolution elevation (5m)      │
│  ✅ Recent satellite imagery (1m)       │
│  ✅ OSM data (roads, buildings, etc)    │
│  ✅ Material generation (7 types)       │
│  ✅ Tactical analysis (AI)              │
│  ✅ Fortification placement             │
│  ✅ Cover & concealment analysis        │
│  ✅ Spawn point intelligence            │
│  ✅ Navigation mesh hints               │
│                                         │
│  Area size: [Input] km²                 │
│  Output: Unreal Engine 5                │
│                                         │
│  [Customize Settings] [Next]           │
└─────────────────────────────────────────┘
```

**Step 4: Optional Customization**

User can click "Customize Settings" to tweak:
- Fortification level (light/medium/heavy)
- Material types
- Resolution trade-offs
- Enable/disable specific features

**Updated UI Requirements:**
- Create profile selection wizard (first-run and always accessible)
- Profile cards with icons and descriptions
- Auto-configuration system
- Configuration preview screen
- "Customize" advanced settings panel
- Save custom profiles
- Area selection (bounding box input)
- Resolution (auto-set by profile, can override)
- Data source checkboxes (auto-checked by profile)
- Output folder picker
- Export button with profile indicator
- Progress bar with profile-specific steps

**Profile Storage:**
```python
# Save user's profile choice
user_profile = {
    "selected_profile": "military_simulation",
    "customizations": {
        "fortification_level": "heavy",  # User changed from medium
        "resolution": 3  # User increased from 5m to 3m
    },
    "last_used": "2024-12-07"
}
```

**Benefits:**
- ✅ Non-technical users don't need to understand GIS
- ✅ Optimal settings for each game type
- ✅ No overwhelming options
- ✅ Tips guide users to best practices
- ✅ Can still customize if needed
- ✅ Faster workflow (less decisions)

**Acceptance Criteria:**
- [ ] Profile wizard shows on first run
- [ ] 13 profiles available with clear descriptions
- [ ] Auto-configuration works correctly per profile
- [ ] User can customize after profile selection
- [ ] Tips are shown based on profile
- [ ] Profile choice saved between sessions
- [ ] "Change Profile" always accessible
- [ ] Dialog opens when plugin clicked
- [ ] All UI elements present and styled
- [ ] Buttons respond correctly
- [ ] Dialog closes properly

---

#### TASK-103: Implement License Validation UI
**Status:** `[ ]` TODO  
**Priority:** HIGH  
**Estimated Time:** 2 hours  
**Agent Model:** Opus 4 (Security)

**Description:**
Create license activation and validation interface.

**Requirements:**
- Create `licensing/license_manager.py`
- Create `ui/license_dialog.py`
- Hardware fingerprint generation
- License key input field
- Activation button
- Status display (Free/Pro/Expired)

**Flow:**
1. First run: Show license dialog
2. User enters license key OR continues with Free
3. Validate against Supabase
4. Store encrypted license locally
5. Check on every plugin start

**Acceptance Criteria:**
- [ ] License dialog shows on first run
- [ ] Can activate with valid license key
- [ ] Can use Free version without key
- [ ] License status shown in main UI
- [ ] Invalid keys rejected with friendly message

---

## 🗺️ SPRINT 3: TERRAIN EXPORT BASICS (Week 3)

**Goal:** Export basic elevation data and test end-to-end

### Elevation Data

#### TASK-201: Implement SRTM Data Fetcher
**Status:** `[ ]` TODO  
**Priority:** HIGH  
**Estimated Time:** 3 hours  
**Agent Model:** Opus 4

**Description:**
Download elevation data from SRTM (Shuttle Radar Topography Mission).

**Requirements:**
- Create `core/data_sources/srtm.py`
- Connect to SRTM API (free, no auth needed)
- Handle bounding box input
- Download tiles
- Merge tiles if multiple needed
- Cache downloaded data

**Technical Details:**
- SRTM provides 30m resolution globally (free)
- 90m resolution for older version
- Tiles are ~25MB each
- Need to handle tile boundaries

**Acceptance Criteria:**
- [ ] Can download SRTM data for any global location
- [ ] Handles multi-tile areas
- [ ] Caches data to avoid re-downloads
- [ ] Progress callback for UI
- [ ] Error handling for no internet/server down

**Testing:**
```python
# Test with San Francisco area
bbox = (-122.5, 37.7, -122.4, 37.8)
elevation = fetch_srtm_elevation(bbox)
# Should return numpy array of heights
```

---

#### TASK-202: Create Elevation Data Processor
**Status:** `[ ]` TODO  
**Priority:** HIGH  
**Estimated Time:** 2 hours  
**Agent Model:** Opus 4

**Description:**
Process raw elevation data into formats needed for export.

**Requirements:**
- Resample to target resolution
- Fill no-data values
- Apply smoothing (optional)
- Convert to different formats (GeoTIFF, PNG16, RAW)
- Calculate min/max/range for normalization

**Acceptance Criteria:**
- [ ] Can convert elevation data to multiple formats
- [ ] Handles no-data values gracefully
- [ ] Maintains precision (16-bit minimum)
- [ ] Fast processing (<5 seconds for 10km²)

---

#### TASK-203: Implement Heightmap Export with .rterrain Format ⭐ UPDATED
**Status:** `[ ]` TODO  
**Priority:** HIGH  
**Estimated Time:** 3 hours  
**Agent Model:** Opus 4

**Description:**
Export processed elevation as custom .rterrain package for UE5 plugin.

**NEW: .rterrain FILE FORMAT** ⭐

Instead of 47+ separate files, everything packed into ONE file!

**File Structure:**
```
terrain_stockholm.rterrain  (Single file!)
│
├─ Header (JSON metadata)
├─ Heightmap data (compressed)
├─ Satellite texture (compressed)
├─ Material masks (6-8 layers)
├─ OSM objects data
├─ Vegetation spawn data
├─ Tactical analysis (if milsim)
├─ Profile configuration
├─ Hardware warnings
└─ Checksums
```

**Technical Implementation:**

```python
class RTerrainFormat:
    """
    Custom container format for RealTerrain Studio exports
    Extension: .rterrain
    MIME type: application/vnd.realterrain.package
    """
    
    MAGIC_NUMBER = b'RTER'  # File signature
    VERSION = 1  # Format version
    
    def __init__(self):
        self.header = {}
        self.data_blocks = {}
    
    def create_package(self, export_data, output_path):
        """
        Create single .rterrain file from all export data
        """
        with open(output_path, 'wb') as f:
            # 1. Write magic number and version
            f.write(self.MAGIC_NUMBER)
            f.write(struct.pack('I', self.VERSION))
            
            # 2. Write header (JSON metadata)
            header = self._create_header(export_data)
            header_json = json.dumps(header, indent=2)
            header_bytes = header_json.encode('utf-8')
            f.write(struct.pack('I', len(header_bytes)))
            f.write(header_bytes)
            
            # 3. Write data blocks
            self._write_data_block(f, 'heightmap', export_data.heightmap)
            self._write_data_block(f, 'satellite', export_data.satellite)
            self._write_data_block(f, 'materials', export_data.materials)
            self._write_data_block(f, 'osm_data', export_data.osm_objects)
            self._write_data_block(f, 'vegetation', export_data.vegetation)
            
            # Optional blocks
            if export_data.tactical_analysis:
                self._write_data_block(f, 'tactical', export_data.tactical_analysis)
            
            # 4. Write index (for quick access)
            self._write_index(f)
            
            # 5. Write checksum
            self._write_checksum(f)
    
    def _create_header(self, export_data):
        """
        Create metadata header
        """
        return {
            "format": "RealTerrain Package",
            "version": self.VERSION,
            "created": datetime.now().isoformat(),
            "plugin_version": "1.0.0",
            
            # Project info
            "project": {
                "name": export_data.project_name,
                "profile": export_data.profile,
                "location": export_data.location_name,
                "bbox": export_data.bbox,
                "area_km2": export_data.area_km2
            },
            
            # Terrain specs
            "terrain": {
                "resolution_m": export_data.resolution,
                "heightmap_size": export_data.heightmap_size,
                "min_elevation": export_data.min_elevation,
                "max_elevation": export_data.max_elevation,
                "coordinate_system": "WGS84"
            },
            
            # Textures
            "textures": {
                "satellite_size": export_data.satellite_size,
                "satellite_format": "JPEG",
                "material_layers": len(export_data.materials),
                "compression": "high"
            },
            
            # Content counts
            "content": {
                "osm_objects": len(export_data.osm_objects),
                "buildings": export_data.building_count,
                "roads_km": export_data.road_length,
                "trees": export_data.tree_count,
                "vegetation_types": len(export_data.vegetation_types)
            },
            
            # UE5 import hints
            "ue5": {
                "landscape_components": export_data.landscape_components,
                "recommended_lod_levels": 5,
                "world_partition": export_data.use_world_partition,
                "nanite_recommended": export_data.tree_count > 100_000,
                "estimated_vram_mb": export_data.vram_estimate
            },
            
            # Hardware validation
            "validation": {
                "min_ram_gb": export_data.min_ram,
                "min_vram_gb": export_data.min_vram,
                "export_time_minutes": export_data.export_time,
                "import_time_minutes": export_data.import_time,
                "warnings": export_data.warnings
            },
            
            # Data blocks index (byte offsets)
            "data_blocks": {}  # Populated during write
        }
    
    def _write_data_block(self, file, block_name, data):
        """
        Write compressed data block with header
        """
        # Record start position
        start_pos = file.tell()
        
        # Compress data
        if isinstance(data, np.ndarray):
            # Numpy array (heightmap, masks)
            compressed = self._compress_array(data)
        elif isinstance(data, bytes):
            # Binary data (JPEG satellite)
            compressed = zlib.compress(data, level=9)
        else:
            # JSON data (OSM, vegetation)
            json_bytes = json.dumps(data).encode('utf-8')
            compressed = zlib.compress(json_bytes, level=9)
        
        # Write block header
        block_header = {
            'name': block_name,
            'compressed_size': len(compressed),
            'uncompressed_size': len(data) if isinstance(data, bytes) else data.nbytes,
            'compression': 'zlib',
            'checksum': hashlib.md5(compressed).hexdigest()
        }
        
        header_bytes = json.dumps(block_header).encode('utf-8')
        file.write(struct.pack('I', len(header_bytes)))
        file.write(header_bytes)
        
        # Write compressed data
        file.write(compressed)
        
        # Record in index
        self.data_blocks[block_name] = {
            'offset': start_pos,
            'size': file.tell() - start_pos
        }
    
    def _compress_array(self, array):
        """
        Efficiently compress numpy array
        """
        # Use blosc for better numpy compression
        import blosc
        return blosc.compress(array.tobytes(), typesize=array.itemsize)
    
    def read_package(self, rterrain_path):
        """
        Read .rterrain file and extract all data
        Used by UE5 plugin
        """
        with open(rterrain_path, 'rb') as f:
            # 1. Verify magic number
            magic = f.read(4)
            if magic != self.MAGIC_NUMBER:
                raise ValueError("Not a valid .rterrain file!")
            
            # 2. Read version
            version = struct.unpack('I', f.read(4))[0]
            if version != self.VERSION:
                raise ValueError(f"Unsupported version: {version}")
            
            # 3. Read header
            header_size = struct.unpack('I', f.read(4))[0]
            header_bytes = f.read(header_size)
            self.header = json.loads(header_bytes.decode('utf-8'))
            
            # 4. Read all data blocks
            while f.tell() < os.path.getsize(rterrain_path) - 32:  # 32 bytes for checksum
                block = self._read_data_block(f)
                self.data_blocks[block['name']] = block['data']
            
            # 5. Verify checksum
            self._verify_checksum(f)
        
        return self
    
    def get_heightmap(self):
        """Extract heightmap as numpy array"""
        return self.data_blocks['heightmap']
    
    def get_satellite(self):
        """Extract satellite image"""
        return self.data_blocks['satellite']
    
    def get_materials(self):
        """Extract material masks"""
        return self.data_blocks['materials']
    
    def get_osm_objects(self):
        """Extract OSM data"""
        return self.data_blocks['osm_data']
    
    def get_metadata(self):
        """Get all metadata"""
        return self.header
```

**File Size Comparison:**

```python
# Traditional approach (47 files):
exports/terrain_stockholm/
  ├─ heightmap.png         (32 MB)
  ├─ heightmap.raw         (64 MB)
  ├─ satellite.jpg         (25 MB)
  ├─ satellite.tga         (90 MB)
  ├─ grass_mask.png        (8 MB)
  ├─ rock_mask.png         (8 MB)
  ├─ dirt_mask.png         (8 MB)
  ├─ forest_mask.png       (8 MB)
  ├─ sand_mask.png         (8 MB)
  ├─ water_mask.png        (8 MB)
  ├─ osm_roads.json        (2 MB)
  ├─ osm_buildings.json    (5 MB)
  ├─ osm_railways.json     (0.5 MB)
  ├─ vegetation_trees.json (15 MB)
  ├─ tactical_data.json    (1 MB)
  ├─ metadata.json         (0.1 MB)
  └─ ... (30+ more files)
TOTAL: ~350 MB (uncompressed, redundant formats)

# .rterrain approach (1 file):
exports/
  └─ terrain_stockholm.rterrain  (85 MB compressed!)
  
BENEFITS:
✓ 75% smaller (compression)
✓ 1 file vs 47 files
✓ Faster transfer
✓ Can't lose individual files
✓ Version controlled easily
✓ Email/upload friendly
```

**UI in QGIS Plugin:**

```
┌──────────────────────────────────────────────────────┐
│  📦 EXPORT FORMAT                                    │
├──────────────────────────────────────────────────────┤
│                                                      │
│  ● .rterrain Package (Recommended) ⭐                │
│    └─ Single file, all data included                │
│    └─ Optimized for UE5 import                      │
│    └─ Size: ~85 MB (compressed)                      │
│                                                      │
│  ○ Traditional (Multiple files)                      │
│    └─ 47+ separate files                             │
│    └─ Compatible with other tools                    │
│    └─ Size: ~350 MB                                  │
│                                                      │
│  ○ Custom (Advanced users)                           │
│    └─ Choose exactly what to export                  │
│                                                      │
│  Output: terrain_stockholm.rterrain                  │
│  Location: [Browse...]                               │
│                                                      │
│  [Export]                                            │
│                                                      │
└──────────────────────────────────────────────────────┘
```

**UE5 Import:**

```
In Unreal Engine 5:
1. File → Import → RealTerrain Package
2. Browse to .rterrain file
3. Click Open
4. Plugin reads EVERYTHING automatically:
   - Creates Landscape
   - Applies satellite texture
   - Applies material layers
   - Spawns OSM objects
   - Places vegetation
   - Configures World Partition
   - Done!

Time: 2-3 minutes for entire import! 🚀
```

**UE5 Plugin Code:**

```cpp
// In UE5 C++ plugin
class FRTerrainImporter
{
public:
    bool ImportRTerrainFile(const FString& FilePath)
    {
        // 1. Open .rterrain file
        TArray<uint8> FileData;
        if (!FFileHelper::LoadFileToArray(FileData, *FilePath))
            return false;
        
        // 2. Parse header
        FRTerrainHeader Header = ParseHeader(FileData);
        
        // 3. Create Landscape
        ALandscape* Landscape = CreateLandscape(Header.TerrainSize);
        
        // 4. Extract and apply heightmap
        TArray<uint16> Heightmap = ExtractHeightmap(FileData);
        ApplyHeightmap(Landscape, Heightmap);
        
        // 5. Extract and apply satellite texture
        UTexture2D* SatelliteTex = ExtractSatellite(FileData);
        ApplyTexture(Landscape, SatelliteTex);
        
        // 6. Extract and apply material layers
        TArray<UTexture2D*> Masks = ExtractMaterialMasks(FileData);
        ApplyMaterialLayers(Landscape, Masks);
        
        // 7. Extract and spawn OSM objects
        TArray<FOSMObject> OSMData = ExtractOSMData(FileData);
        SpawnOSMObjects(OSMData);
        
        // 8. Extract and spawn vegetation
        FVegetationData VegData = ExtractVegetation(FileData);
        SpawnVegetation(VegData);
        
        // 9. Configure based on metadata
        if (Header.UseWorldPartition)
            ConfigureWorldPartition(Landscape);
        
        UE_LOG(LogRealTerrain, Log, TEXT("Import complete! %s"), *Header.ProjectName);
        return true;
    }
};
```

**Advantages for User:**

```
QGIS Side (Export):
✅ Click "Export"
✅ Wait 8 minutes
✅ Get 1 file: terrain.rterrain
✅ Easy to:
   - Email to team
   - Upload to cloud
   - Version control (Git LFS)
   - Backup
   - Share

UE5 Side (Import):
✅ Drag & drop .rterrain file
✅ Wait 2 minutes
✅ Everything appears!
   - Landscape ✓
   - Textures ✓
   - Materials ✓
   - Objects ✓
   - Vegetation ✓
✅ Start working immediately!
```

**Advanced Features:**

```python
class RTerrainFormat:
    
    # Feature: Progressive loading
    def extract_preview(self, rterrain_path):
        """
        Extract low-res preview without loading full file
        """
        with open(rterrain_path, 'rb') as f:
            header = self._read_header_only(f)
            
            # Generate preview
            preview = {
                'thumbnail': self._create_thumbnail(header),
                'stats': header['content'],
                'warnings': header['validation']['warnings'],
                'compatible_ue_version': '5.1+'
            }
        return preview
    
    # Feature: Incremental updates
    def update_package(self, rterrain_path, updates):
        """
        Update specific blocks without re-exporting everything
        Example: User tweaked tree density, only update vegetation block
        """
        package = self.read_package(rterrain_path)
        
        if 'vegetation' in updates:
            package.data_blocks['vegetation'] = updates['vegetation']
        
        # Rewrite only changed blocks
        self.create_package(package, rterrain_path)
    
    # Feature: Compatibility check
    def check_ue5_compatibility(self, rterrain_path, ue5_version):
        """
        Check if .rterrain file is compatible with UE5 version
        """
        header = self._read_header_only(rterrain_path)
        
        checks = {
            'landscape_size': header['terrain']['heightmap_size'] <= 8192,
            'nanite_available': ue5_version >= '5.1' if header['ue5']['nanite_recommended'] else True,
            'world_partition': ue5_version >= '5.0',
            'texture_size': header['textures']['satellite_size'] <= 8192
        }
        
        return all(checks.values()), checks
```

**File Format Specification Document:**

```markdown
# .rterrain File Format Specification v1.0

## Structure
Offset | Size    | Description
-------|---------|-------------
0      | 4       | Magic number: 'RTER' (0x52544552)
4      | 4       | Version (uint32)
8      | 4       | Header size (uint32)
12     | N       | Header JSON (UTF-8)
12+N   | ...     | Data blocks
EOF-32 | 32      | SHA256 checksum

## Header JSON Schema
{
  "format": "RealTerrain Package",
  "version": 1,
  "created": "ISO-8601 datetime",
  "project": {...},
  "terrain": {...},
  "textures": {...},
  "content": {...},
  "ue5": {...},
  "validation": {...},
  "data_blocks": {...}
}

## Data Blocks
Each block:
- Block header (JSON, size-prefixed)
- Compressed data (zlib or blosc)
- Checksum (MD5)

## Compression
- Arrays: blosc (better for numpy)
- JSON: zlib
- Images: stored as JPEG (already compressed)
```

**Acceptance Criteria:**
- [ ] Exports as single .rterrain file
- [ ] Compression reduces size by 70%+
- [ ] UE5 plugin can read format
- [ ] Includes all data (heightmap, textures, objects, etc)
- [ ] Metadata accessible without full extract
- [ ] Checksums verify integrity
- [ ] Version compatible
- [ ] Can update individual blocks
- [ ] Preview/thumbnail generation
- [ ] Backward compatible (future versions can read v1)
- [ ] Documentation complete

---

## 🎨 SPRINT 4: SATELLITE IMAGERY (Week 4)

### Satellite Data Integration

#### TASK-301: Implement Sentinel-2 Fetcher
**Status:** `[ ]` TODO  
**Priority:** MEDIUM  
**Estimated Time:** 3 hours  
**Agent Model:** Opus 4

**Description:**
Download satellite imagery from Sentinel-2 (free ESA service).

**Requirements:**
- Connect to Sentinel Hub or Copernicus API
- Search for cloudless images
- Download RGB bands
- Stitch tiles if needed
- Handle date range selection

**Acceptance Criteria:**
- [ ] Can fetch recent satellite imagery
- [ ] Prefers cloudless images
- [ ] Handles authentication (API key)
- [ ] Downloads at requested resolution
- [ ] Caches images

---

#### TASK-302: Export Satellite Textures
**Status:** `[ ]` TODO  
**Priority:** MEDIUM  
**Estimated Time:** 2 hours  
**Agent Model:** Sonnet 4.5

**Description:**
Process and export satellite imagery as textures for UE5.

**Requirements:**
- Export as high-quality JPEG (for size)
- Export as TGA (lossless alternative)
- Apply color correction (optional)
- Match heightmap dimensions exactly
- Include in metadata

**Output:**
```
exports/
  terrain_001/
    satellite.jpg      (8-bit RGB)
    satellite_meta.json
```

**Acceptance Criteria:**
- [ ] Texture matches heightmap size
- [ ] Good visual quality
- [ ] Reasonable file size (<50MB for 10km²)

---

## 🏘️ SPRINT 5: OSM INTEGRATION (Week 5)

### OpenStreetMap Data

#### TASK-401: Implement OSM Data Fetcher with Chunking ⭐ UPDATED
**Status:** `[ ]` TODO  
**Priority:** MEDIUM  
**Estimated Time:** 5 hours  
**Agent Model:** Opus 4

**Description:**
Fetch OpenStreetMap data with intelligent chunking and coordinate transformation.

**CRITICAL: Overpass API Limits**
- Max 50,000 nodes per query
- Must split large areas into chunks
- Reassemble data correctly
- Handle rate limiting

**OSM CHUNKING SYSTEM:**

```python
class OSMFetcher:
    """
    Intelligent OSM data fetcher with automatic chunking
    """
    
    MAX_NODES = 50_000  # Overpass limit
    TIMEOUT = 180  # seconds
    
    def __init__(self):
        self.overpass_url = "https://overpass-api.de/api/interpreter"
        self.chunks_processed = 0
        self.total_chunks = 0
    
    def fetch_osm_data(self, bbox, filters, progress_callback=None):
        """
        Fetch OSM data with automatic chunking
        
        Args:
            bbox: (min_lon, min_lat, max_lon, max_lat)
            filters: Dict of OSM feature types to fetch
            progress_callback: Function to report progress
        """
        # 1. Estimate data size
        estimated_nodes = self.estimate_node_count(bbox, filters)
        
        # 2. Calculate chunk size
        if estimated_nodes > self.MAX_NODES:
            chunks = self.create_chunks(bbox, estimated_nodes)
            logger.info(f"Area too large, splitting into {len(chunks)} chunks")
        else:
            chunks = [bbox]
        
        self.total_chunks = len(chunks)
        
        # 3. Fetch each chunk
        all_data = {
            'nodes': [],
            'ways': [],
            'relations': []
        }
        
        for i, chunk_bbox in enumerate(chunks):
            logger.info(f"Fetching chunk {i+1}/{len(chunks)}")
            
            chunk_data = self.fetch_chunk(chunk_bbox, filters)
            
            # Merge data
            all_data['nodes'].extend(chunk_data['nodes'])
            all_data['ways'].extend(chunk_data['ways'])
            all_data['relations'].extend(chunk_data['relations'])
            
            # Progress callback
            if progress_callback:
                progress = (i + 1) / len(chunks) * 100
                progress_callback(progress, f"Chunk {i+1}/{len(chunks)}")
            
            self.chunks_processed = i + 1
            
            # Rate limiting (be nice to Overpass API)
            if i < len(chunks) - 1:
                time.sleep(1)  # 1 second between requests
        
        # 4. Remove duplicates (nodes on chunk boundaries)
        deduplicated = self.remove_duplicates(all_data)
        
        # 5. Stitch together split ways
        stitched = self.stitch_ways(deduplicated)
        
        return stitched
    
    def estimate_node_count(self, bbox, filters):
        """
        Estimate number of nodes in area
        Based on area size and density
        """
        area_km2 = self.calculate_area(bbox)
        
        # Density estimates (nodes per km²)
        DENSITY = {
            'roads': 500,
            'buildings': 2000,
            'power_lines': 300,
            'railways': 100,
            'water': 200,
            'poi': 500,
            'street_furniture': 1000
        }
        
        estimated = 0
        for feature_type in filters:
            if feature_type in DENSITY:
                estimated += DENSITY[feature_type] * area_km2
        
        # Add 30% buffer for safety
        return int(estimated * 1.3)
    
    def create_chunks(self, bbox, estimated_nodes):
        """
        Split bbox into smaller chunks
        """
        min_lon, min_lat, max_lon, max_lat = bbox
        
        # Calculate how many chunks needed
        chunks_needed = math.ceil(estimated_nodes / self.MAX_NODES)
        
        # Split in grid (e.g., 2x2, 3x3, 4x4)
        grid_size = math.ceil(math.sqrt(chunks_needed))
        
        lon_step = (max_lon - min_lon) / grid_size
        lat_step = (max_lat - min_lat) / grid_size
        
        chunks = []
        for i in range(grid_size):
            for j in range(grid_size):
                chunk_bbox = (
                    min_lon + i * lon_step,
                    min_lat + j * lat_step,
                    min_lon + (i + 1) * lon_step,
                    min_lat + (j + 1) * lat_step
                )
                chunks.append(chunk_bbox)
        
        logger.info(f"Split into {grid_size}x{grid_size} grid = {len(chunks)} chunks")
        return chunks
    
    def fetch_chunk(self, bbox, filters):
        """
        Fetch single chunk from Overpass API
        """
        query = self.build_overpass_query(bbox, filters)
        
        try:
            response = requests.post(
                self.overpass_url,
                data={'data': query},
                timeout=self.TIMEOUT
            )
            response.raise_for_status()
            
            data = response.json()
            return self.parse_overpass_response(data)
            
        except requests.Timeout:
            logger.error("Overpass API timeout")
            # Retry with smaller timeout
            return self.fetch_chunk_retry(bbox, filters)
        
        except requests.RequestException as e:
            logger.error(f"Overpass API error: {e}")
            return {'nodes': [], 'ways': [], 'relations': []}
    
    def build_overpass_query(self, bbox, filters):
        """
        Build Overpass QL query based on filters
        """
        min_lon, min_lat, max_lon, max_lat = bbox
        bbox_str = f"{min_lat},{min_lon},{max_lat},{max_lon}"
        
        # Start query
        query = f"[out:json][timeout:{self.TIMEOUT}];\n(\n"
        
        # Add filters
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
        
        if filters.get('poi'):
            query += f'  node["amenity"]({bbox_str});\n'
            query += f'  way["amenity"]({bbox_str});\n'
        
        # ... (add all other filters)
        
        # End query - get geometry
        query += ");\nout geom;"
        
        return query
    
    def remove_duplicates(self, data):
        """
        Remove duplicate nodes/ways from overlapping chunks
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
            if node['id'] not in seen_nodes:
                unique_data['nodes'].append(node)
                seen_nodes.add(node['id'])
        
        # Deduplicate ways
        for way in data['ways']:
            if way['id'] not in seen_ways:
                unique_data['ways'].append(way)
                seen_ways.add(way['id'])
        
        # Deduplicate relations
        for relation in data['relations']:
            if relation['id'] not in seen_relations:
                unique_data['relations'].append(relation)
                seen_relations.add(relation['id'])
        
        logger.info(f"Removed {len(data['nodes']) - len(unique_data['nodes'])} duplicate nodes")
        logger.info(f"Removed {len(data['ways']) - len(unique_data['ways'])} duplicate ways")
        
        return unique_data
    
    def stitch_ways(self, data):
        """
        Stitch together ways that were split across chunk boundaries
        
        Example: A long road split into 3 chunks should be 1 continuous way
        """
        ways_by_name = {}
        
        for way in data['ways']:
            # Group ways by name and type
            name = way.get('tags', {}).get('name', '')
            highway_type = way.get('tags', {}).get('highway', '')
            
            key = (name, highway_type)
            
            if key not in ways_by_name:
                ways_by_name[key] = []
            ways_by_name[key].append(way)
        
        stitched_ways = []
        
        for key, ways in ways_by_name.items():
            if len(ways) == 1:
                # Single way, no stitching needed
                stitched_ways.append(ways[0])
            else:
                # Multiple segments, try to connect them
                connected = self.connect_way_segments(ways)
                stitched_ways.extend(connected)
        
        data['ways'] = stitched_ways
        return data
    
    def connect_way_segments(self, segments):
        """
        Connect way segments that touch at endpoints
        """
        # Complex algorithm - connects segments into continuous paths
        # ... implementation details ...
        return segments  # Placeholder
```

**COORDINATE TRANSFORMATION & PLACEMENT:**

```python
class OSMToUE5Converter:
    """
    Convert OSM data to UE5 coordinate system with proper placement
    """
    
    def __init__(self, bbox, terrain_origin, heightmap):
        self.bbox = bbox
        self.terrain_origin = terrain_origin  # UE5 world coordinates
        self.heightmap = heightmap  # For ground placement
        
        # Calculate conversion factors
        self.setup_coordinate_transform()
    
    def setup_coordinate_transform(self):
        """
        Calculate transformation from WGS84 (lat/lon) to UE5 (X, Y, Z)
        """
        min_lon, min_lat, max_lon, max_lat = self.bbox
        
        # Calculate meters per degree at this latitude
        # (Earth is not a perfect sphere)
        lat_center = (min_lat + max_lat) / 2
        
        # Meters per degree longitude (varies with latitude)
        self.meters_per_degree_lon = 111320 * math.cos(math.radians(lat_center))
        
        # Meters per degree latitude (roughly constant)
        self.meters_per_degree_lat = 110540
        
        # UE5 uses centimeters
        self.cm_per_degree_lon = self.meters_per_degree_lon * 100
        self.cm_per_degree_lat = self.meters_per_degree_lat * 100
        
        logger.info(f"Coordinate transform: {self.cm_per_degree_lon:.2f} cm/deg lon, "
                   f"{self.cm_per_degree_lat:.2f} cm/deg lat")
    
    def latlon_to_ue5(self, lat, lon):
        """
        Convert lat/lon to UE5 world coordinates (X, Y, Z)
        
        UE5 Coordinate System:
        - X: Forward (North)
        - Y: Right (East)
        - Z: Up (Elevation)
        """
        min_lon, min_lat, max_lon, max_lat = self.bbox
        
        # Calculate offset from terrain origin (in degrees)
        delta_lat = lat - min_lat
        delta_lon = lon - min_lon
        
        # Convert to UE5 centimeters
        ue5_x = delta_lat * self.cm_per_degree_lat  # North
        ue5_y = delta_lon * self.cm_per_degree_lon  # East
        
        # Get ground elevation at this point
        ue5_z = self.get_ground_elevation(lat, lon)
        
        # Add terrain origin offset
        ue5_x += self.terrain_origin[0]
        ue5_y += self.terrain_origin[1]
        ue5_z += self.terrain_origin[2]
        
        return (ue5_x, ue5_y, ue5_z)
    
    def get_ground_elevation(self, lat, lon):
        """
        Sample heightmap to get ground elevation at lat/lon
        
        CRITICAL: This prevents objects from floating in air!
        """
        min_lon, min_lat, max_lon, max_lat = self.bbox
        
        # Normalize to [0, 1]
        norm_x = (lat - min_lat) / (max_lat - min_lat)
        norm_y = (lon - min_lon) / (max_lon - min_lon)
        
        # Clamp to valid range
        norm_x = max(0, min(1, norm_x))
        norm_y = max(0, min(1, norm_y))
        
        # Sample heightmap
        height, width = self.heightmap.shape
        pixel_x = int(norm_x * (height - 1))
        pixel_y = int(norm_y * (width - 1))
        
        # Get elevation value (convert from heightmap units to cm)
        elevation_m = self.heightmap[pixel_x, pixel_y]
        elevation_cm = elevation_m * 100
        
        return elevation_cm
    
    def convert_building(self, osm_building):
        """
        Convert OSM building to UE5 placement data
        
        Handles:
        - Correct position (on ground)
        - Correct rotation (building orientation)
        - Correct height
        """
        # Get building footprint (polygon)
        nodes = osm_building['geometry']
        
        # Convert all nodes to UE5 coordinates
        ue5_points = [self.latlon_to_ue5(node['lat'], node['lon']) 
                      for node in nodes]
        
        # Calculate building center
        center_x = sum(p[0] for p in ue5_points) / len(ue5_points)
        center_y = sum(p[1] for p in ue5_points) / len(ue5_points)
        center_z = sum(p[2] for p in ue5_points) / len(ue5_points)
        
        # Calculate building rotation (from longest wall)
        rotation = self.calculate_building_rotation(ue5_points)
        
        # Get building height
        tags = osm_building.get('tags', {})
        height = self.get_building_height(tags)
        
        # Get number of floors
        levels = int(tags.get('building:levels', 1))
        
        return {
            'type': 'building',
            'position': (center_x, center_y, center_z),
            'rotation': rotation,  # Yaw angle in degrees
            'footprint': ue5_points,
            'height': height,
            'levels': levels,
            'tags': tags
        }
    
    def calculate_building_rotation(self, points):
        """
        Calculate building rotation from footprint
        
        Finds longest wall and aligns building to it
        This ensures buildings face roads correctly!
        """
        if len(points) < 2:
            return 0.0
        
        # Find longest edge
        max_length = 0
        best_angle = 0
        
        for i in range(len(points) - 1):
            p1 = points[i]
            p2 = points[i + 1]
            
            # Calculate edge length
            dx = p2[0] - p1[0]
            dy = p2[1] - p1[1]
            length = math.sqrt(dx*dx + dy*dy)
            
            if length > max_length:
                max_length = length
                # Calculate angle (in degrees)
                best_angle = math.degrees(math.atan2(dy, dx))
        
        # Normalize to 0-360
        best_angle = best_angle % 360
        
        return best_angle
    
    def get_building_height(self, tags):
        """
        Get building height from OSM tags
        
        Priority:
        1. building:height (explicit)
        2. building:levels (estimate 3m per floor)
        3. Default (one story = 3m)
        """
        # Check explicit height
        if 'height' in tags:
            try:
                return float(tags['height']) * 100  # meters to cm
            except ValueError:
                pass
        
        if 'building:height' in tags:
            try:
                return float(tags['building:height']) * 100
            except ValueError:
                pass
        
        # Estimate from levels
        if 'building:levels' in tags:
            try:
                levels = int(tags['building:levels'])
                return levels * 300  # 3m per floor in cm
            except ValueError:
                pass
        
        # Default: single story
        return 300  # 3 meters
    
    def convert_road(self, osm_road):
        """
        Convert OSM road to UE5 spline data
        
        Roads are splines that follow ground elevation
        """
        nodes = osm_road['geometry']
        tags = osm_road.get('tags', {})
        
        # Convert nodes to UE5 coordinates
        spline_points = []
        for node in nodes:
            ue5_pos = self.latlon_to_ue5(node['lat'], node['lon'])
            
            # Roads should be SLIGHTLY above ground (5cm)
            # to prevent z-fighting with terrain
            ue5_pos = (ue5_pos[0], ue5_pos[1], ue5_pos[2] + 5)
            
            spline_points.append(ue5_pos)
        
        # Get road attributes
        highway_type = tags.get('highway', 'unclassified')
        lanes = int(tags.get('lanes', self.estimate_lanes(highway_type)))
        width = self.get_road_width(highway_type, lanes)
        surface = tags.get('surface', 'asphalt')
        max_speed = tags.get('maxspeed', '')
        name = tags.get('name', '')
        
        return {
            'type': 'road',
            'highway_type': highway_type,
            'spline_points': spline_points,
            'width': width,  # cm
            'lanes': lanes,
            'surface': surface,
            'max_speed': max_speed,
            'name': name,
            'tags': tags
        }
    
    def get_road_width(self, highway_type, lanes):
        """
        Estimate road width based on type and lanes
        """
        LANE_WIDTH = 350  # cm (3.5 meters per lane)
        
        WIDTHS = {
            'motorway': LANE_WIDTH * max(lanes, 4),
            'trunk': LANE_WIDTH * max(lanes, 3),
            'primary': LANE_WIDTH * max(lanes, 2),
            'secondary': LANE_WIDTH * max(lanes, 2),
            'tertiary': LANE_WIDTH * max(lanes, 1),
            'residential': 600,  # 6m
            'service': 400,  # 4m
            'track': 300,  # 3m
            'path': 150,  # 1.5m
            'footway': 150,
            'cycleway': 200
        }
        
        return WIDTHS.get(highway_type, LANE_WIDTH * lanes)
    
    def convert_tree(self, osm_tree):
        """
        Convert OSM tree to UE5 placement
        
        Trees must be placed ON GROUND with random rotation
        """
        lat = osm_tree['lat']
        lon = osm_tree['lon']
        
        ue5_pos = self.latlon_to_ue5(lat, lon)
        
        # Random rotation for natural look
        rotation = random.uniform(0, 360)
        
        # Random scale variation (±10%)
        scale = random.uniform(0.9, 1.1)
        
        tags = osm_tree.get('tags', {})
        species = tags.get('species', 'unknown')
        
        return {
            'type': 'tree',
            'position': ue5_pos,
            'rotation': rotation,
            'scale': scale,
            'species': species,
            'tags': tags
        }
    
    def convert_power_line(self, osm_powerline):
        """
        Convert power line to spline with towers
        
        Power lines: suspended between towers at height
        """
        nodes = osm_powerline['geometry']
        tags = osm_powerline.get('tags', {})
        
        # Power line height above ground
        line_height = 1000  # 10m default
        if 'height' in tags:
            try:
                line_height = float(tags['height']) * 100
            except ValueError:
                pass
        
        spline_points = []
        tower_positions = []
        
        for i, node in enumerate(nodes):
            ue5_pos = self.latlon_to_ue5(node['lat'], node['lon'])
            
            # Power line elevated above ground
            elevated_pos = (
                ue5_pos[0],
                ue5_pos[1],
                ue5_pos[2] + line_height
            )
            
            spline_points.append(elevated_pos)
            
            # Place tower every 50-100m (or at each node)
            if i % 2 == 0 or i == 0 or i == len(nodes) - 1:
                tower_positions.append(ue5_pos)  # Tower on ground
        
        return {
            'type': 'power_line',
            'spline_points': spline_points,
            'tower_positions': tower_positions,
            'voltage': tags.get('voltage', ''),
            'tags': tags
        }
```

**EXPORT TO .rterrain FILE:**

```python
def export_osm_to_rterrain(osm_data, converter):
    """
    Convert OSM data and include in .rterrain package
    """
    converted_objects = {
        'roads': [],
        'buildings': [],
        'trees': [],
        'power_lines': [],
        'railways': [],
        'poi': []
    }
    
    # Convert each OSM element
    for way in osm_data['ways']:
        tags = way.get('tags', {})
        
        if 'highway' in tags:
            converted_objects['roads'].append(
                converter.convert_road(way)
            )
        
        elif 'building' in tags:
            converted_objects['buildings'].append(
                converter.convert_building(way)
            )
        
        elif 'power' in tags and tags['power'] == 'line':
            converted_objects['power_lines'].append(
                converter.convert_power_line(way)
            )
        
        elif 'railway' in tags:
            converted_objects['railways'].append(
                converter.convert_railway(way)
            )
    
    for node in osm_data['nodes']:
        tags = node.get('tags', {})
        
        if 'natural' in tags and tags['natural'] == 'tree':
            converted_objects['trees'].append(
                converter.convert_tree(node)
            )
        
        elif 'amenity' in tags:
            converted_objects['poi'].append(
                converter.convert_poi(node)
            )
    
    return converted_objects
```

**Acceptance Criteria:**
- [ ] Fetches OSM data with Overpass API
- [ ] Handles 50,000 node limit with chunking
- [ ] Splits large areas into manageable chunks
- [ ] Removes duplicate nodes from overlapping chunks
- [ ] Stitches split ways back together
- [ ] Converts lat/lon to UE5 coordinates correctly
- [ ] Places objects ON GROUND (samples heightmap)
- [ ] Buildings have correct rotation (face roads)
- [ ] Roads follow terrain elevation
- [ ] Power lines elevated at correct height
- [ ] Trees have random rotation for natural look
- [ ] Handles all OSM feature types
- [ ] Progress callback during download
- [ ] Error handling for API failures
- [ ] Rate limiting (1 second between chunks)
- [ ] Exports to .rterrain format

---

#### TASK-402: Export OSM Objects List
**Status:** `[ ]` TODO  
**Priority:** MEDIUM  
**Estimated Time:** 2 hours  
**Agent Model:** Sonnet 4.5

**Description:**
Export OSM objects as structured list for UE5 spawning.

**Requirements:**
- Create JSON file with objects
- Include position (lat/lon and local XY)
- Include type/tags
- Include rotation (for roads)
- Organized by category

**Output Format:**
```json
{
  "roads": [
    {
      "id": "way_123",
      "type": "primary",
      "points": [[x1,y1], [x2,y2]],
      "width": 10,
      "surface": "asphalt"
    }
  ],
  "buildings": [
    {
      "id": "way_456",
      "polygon": [[x1,y1], [x2,y2], ...],
      "height": 15,
      "levels": 3
    }
  ]
}
```

**Acceptance Criteria:**
- [ ] All objects exported with correct data
- [ ] Positions are relative to terrain origin
- [ ] Categories properly separated

---

## 🎨 SPRINT 6: MATERIAL MASKS (Week 6)

### Automated Material Generation

#### TASK-501: Implement Material Classifier
**Status:** `[ ]` TODO  
**Priority:** MEDIUM  
**Estimated Time:** 4 hours  
**Agent Model:** Opus 4

**Description:**
Analyze terrain and satellite data to generate material masks.

**Requirements:**
- Analyze slope (steep = rock, flat = grass)
- Analyze satellite colors (green = vegetation, brown = dirt)
- Analyze elevation (high = snow, low = grass)
- Analyze proximity to water
- Generate masks for each material type

**Material Types:**
1. Grass (flat, low elevation, green)
2. Rock (steep slopes, high elevation)
3. Dirt (medium slope, brown)
4. Sand (near water, flat, tan)
5. Snow (very high elevation)
6. Forest (dense green areas)
7. Water (blue in satellite)

**Output:**
```
exports/
  terrain_001/
    masks/
      grass_mask.png    (grayscale weight map)
      rock_mask.png
      dirt_mask.png
      ...
```

**Acceptance Criteria:**
- [ ] Generates reasonable masks automatically
- [ ] Masks are 8-bit grayscale (0-255)
- [ ] Match heightmap dimensions
- [ ] Blend zones between materials

---

## 🎮 SPRINT 7: UE5 PLUGIN BASICS (Week 7)

### Unreal Engine 5 Integration

#### TASK-601: Create UE5 Plugin Structure
**Status:** `[ ]` TODO  
**Priority:** HIGH  
**Estimated Time:** 2 hours  
**Agent Model:** Sonnet 4.5

**Description:**
Create basic UE5 C++ plugin structure.

**Requirements:**
- Create `.uplugin` file
- Create module structure
- Setup build configuration
- Add to UE5 plugins folder
- Create basic editor menu entry

**Acceptance Criteria:**
- [ ] Plugin compiles in UE5
- [ ] Appears in Plugins list
- [ ] Can be enabled
- [ ] Shows menu entry in Editor

**Testing for User:**
1. Copy plugin to UE5 project's Plugins folder
2. Open Unreal Editor
3. Edit → Plugins → search "RealTerrain"
4. Enable plugin
5. Restart editor

---

#### TASK-602: Implement Heightmap Importer
**Status:** `[ ]` TODO  
**Priority:** HIGH  
**Estimated Time:** 3 hours  
**Agent Model:** Opus 4

**Description:**
Import heightmap and create Landscape in UE5.

**Requirements:**
- Read 16-bit PNG heightmap
- Read metadata JSON
- Create Landscape actor
- Set proper scale (based on metadata)
- Apply heightmap data
- Position at world origin

**Acceptance Criteria:**
- [ ] Imports heightmap successfully
- [ ] Creates Landscape with correct dimensions
- [ ] Maintains elevation accuracy
- [ ] Proper world-space scale

---

#### TASK-603: Implement Material Application with Spline System ⭐ UPDATED
**Status:** `[ ]` TODO  
**Priority:** MEDIUM  
**Estimated Time:** 6 hours  
**Agent Model:** Opus 4

**Description:**
Apply material layers to landscape AND generate UE5 Splines for linear features.

**CRITICAL: SPLINE GENERATION FOR UE5**

Many OSM features MUST be Splines in UE5:
- Roads (spline meshes for road surfaces)
- Railways (spline-based tracks)
- Power lines (cables suspended between towers)
- Rivers/Streams (water splines)
- Fences/Walls (follow terrain)
- Pipelines
- Trails/Paths

**SPLINE DATA FORMAT IN .rterrain:**

```python
class SplineExporter:
    """
    Export OSM linear features as UE5-ready spline data
    """
    
    def export_road_spline(self, road_data):
        """
        Export road as spline with all necessary data for UE5
        
        UE5 needs:
        - Spline points (positions)
        - Tangents (for smooth curves)
        - Width (for road mesh)
        - Material info
        - Metadata (lanes, speed, etc)
        """
        return {
            'type': 'road_spline',
            'spline_id': road_data['osm_id'],
            'name': road_data.get('name', 'Unnamed Road'),
            
            # Spline geometry
            'points': [
                {
                    'position': (x, y, z),  # UE5 world coordinates
                    'arrive_tangent': (tx, ty, tz),  # Tangent coming into point
                    'leave_tangent': (tx, ty, tz),   # Tangent leaving point
                    'rotation': (pitch, yaw, roll),  # Rotation at this point
                    'scale': (sx, sy, sz)  # Scale at this point (for width variation)
                }
                for point in road_data['points']
            ],
            
            # Spline properties
            'spline_type': 'Curve',  # or 'Linear', 'CurveCustomTangent'
            'closed_loop': False,  # True for roundabouts, race tracks
            
            # Road-specific data
            'road_type': road_data['highway'],  # motorway, primary, etc
            'width': road_data['width'],  # cm
            'lanes': road_data['lanes'],
            'surface': road_data['surface'],  # asphalt, gravel, dirt
            'max_speed': road_data.get('max_speed', ''),
            
            # UE5 mesh generation hints
            'mesh_profile': self.get_road_mesh_profile(road_data),
            'material': self.get_road_material(road_data),
            
            # Additional features
            'has_sidewalk': road_data.get('sidewalk') in ['both', 'left', 'right'],
            'has_bike_lane': 'cycleway' in road_data.get('tags', {}),
            'one_way': road_data.get('oneway', 'no') == 'yes',
            
            # Decoration spawn points
            'street_light_positions': self.calculate_street_light_positions(road_data),
            'road_sign_positions': self.calculate_sign_positions(road_data),
            'tree_positions': self.calculate_roadside_tree_positions(road_data),
        }
    
    def calculate_tangents(self, points):
        """
        Calculate smooth tangents for spline curves
        
        UE5 uses Hermite splines - needs tangents for smooth curves
        """
        tangents = []
        
        for i in range(len(points)):
            if i == 0:
                # First point: tangent toward next point
                tangent = self.normalize(
                    self.subtract(points[i+1], points[i])
                )
            elif i == len(points) - 1:
                # Last point: tangent from previous point
                tangent = self.normalize(
                    self.subtract(points[i], points[i-1])
                )
            else:
                # Middle points: average of incoming and outgoing
                incoming = self.normalize(
                    self.subtract(points[i], points[i-1])
                )
                outgoing = self.normalize(
                    self.subtract(points[i+1], points[i])
                )
                tangent = self.normalize(
                    self.add(incoming, outgoing)
                )
            
            # Scale tangent for curve smoothness
            # Longer tangents = smoother curves
            tangent_length = self.distance(points[i], points[i+1] if i < len(points)-1 else points[i-1])
            tangent = self.multiply(tangent, tangent_length * 0.5)
            
            tangents.append({
                'arrive': tangent,
                'leave': tangent
            })
        
        return tangents
    
    def export_railway_spline(self, railway_data):
        """
        Export railway as spline
        
        Railways need very smooth curves (trains can't turn sharp!)
        """
        return {
            'type': 'railway_spline',
            'spline_id': railway_data['osm_id'],
            
            # Geometry (extra smooth!)
            'points': self.generate_smooth_points(
                railway_data['points'],
                smoothing_factor=0.8  # High smoothing for trains
            ),
            
            # Railway properties
            'railway_type': railway_data['railway'],  # rail, subway, tram, etc
            'gauge': railway_data.get('gauge', '1435'),  # mm (standard gauge)
            'electrified': railway_data.get('electrified', 'no'),
            'max_speed': railway_data.get('maxspeed', ''),
            'tracks': int(railway_data.get('tracks', 1)),
            
            # UE5 mesh hints
            'mesh_profile': 'railway_track',
            'tie_spacing': 60,  # cm between railroad ties
            'ballast_width': 400,  # cm (gravel bed width)
            
            # Overhead lines (if electrified)
            'catenary_height': 550 if railway_data.get('electrified') == 'contact_line' else 0,
            'catenary_poles': self.calculate_catenary_pole_positions(railway_data)
        }
    
    def export_powerline_spline(self, powerline_data):
        """
        Export power line as spline with catenary sag
        
        Power lines hang in catenary curves between towers!
        """
        # Calculate tower positions
        tower_positions = self.calculate_tower_positions(
            powerline_data['points'],
            tower_spacing=80  # meters between towers
        )
        
        # Generate catenary curves between towers
        spline_points = []
        for i in range(len(tower_positions) - 1):
            tower_a = tower_positions[i]
            tower_b = tower_positions[i+1]
            
            # Generate catenary curve
            catenary_points = self.generate_catenary_curve(
                tower_a,
                tower_b,
                sag_factor=0.03  # 3% sag
            )
            
            spline_points.extend(catenary_points)
        
        return {
            'type': 'powerline_spline',
            'spline_id': powerline_data['osm_id'],
            
            # Cable geometry (catenary curves)
            'cable_points': spline_points,
            
            # Tower positions (placed on ground)
            'tower_positions': tower_positions,
            'tower_type': self.get_tower_type(powerline_data),
            
            # Electrical properties
            'voltage': powerline_data.get('voltage', ''),
            'cables': int(powerline_data.get('cables', 3)),
            'cable_spacing': 150,  # cm horizontal spacing
            
            # Visual details
            'insulator_count': len(tower_positions) * 3,  # 3 per tower
            'danger_signs': True if int(powerline_data.get('voltage', '0')) > 10000 else False
        }
    
    def export_river_spline(self, river_data):
        """
        Export river/stream as spline for water plugin
        
        Rivers need flow direction and width variation
        """
        points = river_data['points']
        
        # Calculate flow direction (downhill)
        flow_direction = self.calculate_flow_direction(points)
        
        # Calculate width variation (wider at mouth, narrower at source)
        widths = self.calculate_river_widths(points, river_data)
        
        return {
            'type': 'river_spline',
            'spline_id': river_data['osm_id'],
            'name': river_data.get('name', 'Unnamed River'),
            
            # Geometry
            'points': [
                {
                    'position': point,
                    'width': widths[i],  # Variable width
                    'depth': self.estimate_depth(widths[i]),
                    'flow_velocity': self.estimate_velocity(widths[i], flow_direction)
                }
                for i, point in enumerate(points)
            ],
            
            # Water properties
            'waterway_type': river_data['waterway'],  # river, stream, canal
            'flow_direction': flow_direction,  # Downstream direction
            
            # UE5 Water Plugin data
            'water_material': 'M_River',
            'generate_foam': True,  # White water on rocks
            'generate_ripples': True,
            'water_speed': self.estimate_flow_speed(river_data),
            
            # Riverbed
            'riverbed_depth': 100,  # cm below water surface
            'riverbed_material': 'sand' if river_data.get('intermittent') else 'rock'
        }
    
    def export_fence_spline(self, fence_data):
        """
        Export fence/wall as spline mesh
        
        Fences follow terrain exactly
        """
        return {
            'type': 'fence_spline',
            'spline_id': fence_data['osm_id'],
            
            # Geometry (follows ground closely)
            'points': fence_data['points'],  # Already on ground
            
            # Fence properties
            'barrier_type': fence_data['barrier'],  # fence, wall, hedge, etc
            'height': self.get_fence_height(fence_data),
            'material_type': fence_data.get('material', 'wood'),
            
            # UE5 mesh
            'mesh_type': self.get_fence_mesh_type(fence_data),
            'post_spacing': 200,  # cm between posts
            'gate_positions': self.find_gate_positions(fence_data),
            
            # Visual details
            'weathering': 0.5,  # 0-1 how weathered/old
            'vegetation_overgrowth': fence_data['barrier'] == 'hedge'
        }
    
    def export_trail_spline(self, trail_data):
        """
        Export hiking/bike trail as spline
        
        Trails are narrow, follow terrain closely
        """
        return {
            'type': 'trail_spline',
            'spline_id': trail_data['osm_id'],
            'name': trail_data.get('name', 'Unnamed Trail'),
            
            # Geometry
            'points': trail_data['points'],
            
            # Trail properties
            'trail_type': trail_data['highway'],  # path, footway, cycleway, track
            'surface': trail_data.get('surface', 'ground'),
            'width': trail_data.get('width', 150),  # cm
            'difficulty': trail_data.get('sac_scale', 'hiking'),  # hiking, mountain_hiking, etc
            
            # Features along trail
            'waymarkers': self.calculate_waymarker_positions(trail_data),
            'benches': trail_data.get('bench_positions', []),
            'viewpoints': trail_data.get('viewpoint_positions', []),
            
            # Vegetation
            'vegetation_density': 0.7,  # Dense vegetation along trails
            'grass_height': 30  # cm
        }
    
    def generate_catenary_curve(self, point_a, point_b, sag_factor=0.03):
        """
        Generate realistic power line sag between towers
        
        Catenary equation: y = a * cosh(x/a)
        """
        distance = self.distance_2d(point_a, point_b)
        height_diff = point_b[2] - point_a[2]
        
        # Number of points for smooth curve
        num_points = max(10, int(distance / 500))  # Point every 5m
        
        points = []
        for i in range(num_points):
            t = i / (num_points - 1)
            
            # Linear interpolation
            x = point_a[0] + t * (point_b[0] - point_a[0])
            y = point_a[1] + t * (point_b[1] - point_a[1])
            z_linear = point_a[2] + t * height_diff
            
            # Add catenary sag (downward curve)
            # Maximum sag at middle
            sag = -distance * sag_factor * math.sin(t * math.pi)
            
            z = z_linear + sag
            
            points.append((x, y, z))
        
        return points
```

**UE5 IMPORT - SPLINE CREATION:**

```cpp
// In UE5 Plugin

void URealTerrainImporter::ImportRoadSpline(FRoadSplineData SplineData)
{
    // 1. Create Spline Component
    USplineComponent* RoadSpline = NewObject<USplineComponent>(
        GetTransientPackage(),
        USplineComponent::StaticClass()
    );
    
    // 2. Clear default points
    RoadSpline->ClearSplinePoints();
    
    // 3. Add all points from .rterrain data
    for (int32 i = 0; i < SplineData.Points.Num(); i++)
    {
        FSplinePoint Point;
        Point.Position = SplineData.Points[i].Position;
        Point.ArriveTangent = SplineData.Points[i].ArriveTangent;
        Point.LeaveTangent = SplineData.Points[i].LeaveTangent;
        Point.Rotation = SplineData.Points[i].Rotation;
        Point.Scale = SplineData.Points[i].Scale;
        Point.Type = ESplinePointType::Curve;  // Smooth curves
        
        RoadSpline->AddPoint(Point, false);
    }
    
    RoadSpline->UpdateSpline();
    
    // 4. Create Spline Mesh Component for road surface
    USplineMeshComponent* RoadMesh = NewObject<USplineMeshComponent>();
    
    // 5. Set road mesh (from asset library)
    UStaticMesh* RoadMeshAsset = LoadRoadMesh(SplineData.RoadType);
    RoadMesh->SetStaticMesh(RoadMeshAsset);
    
    // 6. Apply material
    UMaterialInterface* RoadMaterial = LoadRoadMaterial(SplineData.Surface);
    RoadMesh->SetMaterial(0, RoadMaterial);
    
    // 7. Configure mesh along spline
    RoadMesh->SetStartAndEnd(
        RoadSpline->GetLocationAtSplinePoint(0, ESplineCoordinateSpace::World),
        RoadSpline->GetTangentAtSplinePoint(0, ESplineCoordinateSpace::World),
        RoadSpline->GetLocationAtSplinePoint(1, ESplineCoordinateSpace::World),
        RoadSpline->GetTangentAtSplinePoint(1, ESplineCoordinateSpace::World)
    );
    
    // 8. Scale to road width
    FVector Scale(1.0f, SplineData.Width / 400.0f, 1.0f);  // Default mesh is 4m wide
    RoadMesh->SetStartScale(Scale);
    RoadMesh->SetEndScale(Scale);
    
    // 9. Spawn decorations (street lights, signs, etc)
    if (SplineData.StreetLightPositions.Num() > 0)
    {
        SpawnStreetLights(RoadSpline, SplineData.StreetLightPositions);
    }
    
    // 10. Spawn roadside vegetation
    if (SplineData.TreePositions.Num() > 0)
    {
        SpawnRoadsideTrees(RoadSpline, SplineData.TreePositions);
    }
    
    UE_LOG(LogRealTerrain, Log, TEXT("Created road spline: %s (%d points)"),
           *SplineData.Name, SplineData.Points.Num());
}

void URealTerrainImporter::ImportPowerLineSpline(FPowerLineSplineData SplineData)
{
    // 1. Create power line cable splines (3 cables for 3-phase power)
    int32 NumCables = SplineData.Cables;
    TArray<USplineComponent*> CableSplines;
    
    for (int32 i = 0; i < NumCables; i++)
    {
        USplineComponent* Cable = NewObject<USplineComponent>();
        Cable->ClearSplinePoints();
        
        // Offset cables horizontally (spacing)
        float HorizontalOffset = (i - NumCables/2.0f) * SplineData.CableSpacing;
        
        // Add catenary curve points
        for (const FVector& Point : SplineData.CablePoints)
        {
            FVector OffsetPoint = Point + FVector(0, HorizontalOffset, 0);
            Cable->AddSplinePoint(OffsetPoint, ESplineCoordinateSpace::World);
        }
        
        Cable->UpdateSpline();
        CableSplines.Add(Cable);
    }
    
    // 2. Spawn power line towers
    for (const FVector& TowerPos : SplineData.TowerPositions)
    {
        SpawnPowerTower(TowerPos, SplineData.TowerType, SplineData.Voltage);
    }
    
    // 3. Create cable mesh along splines
    for (USplineComponent* Cable : CableSplines)
    {
        CreateCableMesh(Cable, SplineData.Voltage);
    }
}

void URealTerrainImporter::ImportRiverSpline(FRiverSplineData SplineData)
{
    // Use UE5 Water Plugin
    AWaterBody* River = GetWorld()->SpawnActor<AWaterBodyRiver>();
    
    USplineComponent* RiverSpline = River->GetWaterSpline();
    RiverSpline->ClearSplinePoints();
    
    // Add river points with width variation
    for (int32 i = 0; i < SplineData.Points.Num(); i++)
    {
        FVector Position = SplineData.Points[i].Position;
        float Width = SplineData.Points[i].Width;
        
        RiverSpline->AddSplinePoint(Position, ESplineCoordinateSpace::World);
        
        // Set width at this point
        RiverSpline->SetSplinePointType(i, ESplinePointType::Curve);
        RiverSpline->SetScaleAtSplinePoint(i, FVector(1.0f, Width / 1000.0f, 1.0f));
    }
    
    RiverSpline->UpdateSpline();
    
    // Configure water properties
    River->SetWaterMaterial(LoadWaterMaterial(SplineData.WaterwayType));
    River->SetWaterVelocity(SplineData.WaterSpeed);
    
    // Set flow direction
    River->GetWaterSpline()->SetClosedLoop(false);
    // Water flows from first point to last point
}

void URealTerrainImporter::ImportFenceSpline(FFenceSplineData SplineData)
{
    USplineComponent* FenceSpline = NewObject<USplineComponent>();
    FenceSpline->ClearSplinePoints();
    
    // Add fence points (already on ground from QGIS)
    for (const FVector& Point : SplineData.Points)
    {
        FenceSpline->AddSplinePoint(Point, ESplineCoordinateSpace::World);
    }
    
    FenceSpline->UpdateSpline();
    
    // Spawn fence posts at regular intervals
    float SplineLength = FenceSpline->GetSplineLength();
    float PostSpacing = SplineData.PostSpacing;
    int32 NumPosts = FMath::CeilToInt(SplineLength / PostSpacing);
    
    for (int32 i = 0; i <= NumPosts; i++)
    {
        float Distance = i * PostSpacing;
        FVector Location = FenceSpline->GetLocationAtDistanceAlongSpline(
            Distance,
            ESplineCoordinateSpace::World
        );
        
        FRotator Rotation = FenceSpline->GetRotationAtDistanceAlongSpline(
            Distance,
            ESplineCoordinateSpace::World
        );
        
        SpawnFencePost(Location, Rotation, SplineData.Height);
    }
    
    // Create fence mesh between posts
    CreateFenceMesh(FenceSpline, SplineData.MeshType, SplineData.Height);
    
    // Spawn gates at designated positions
    for (const FVector& GatePos : SplineData.GatePositions)
    {
        SpawnGate(GatePos, SplineData.BarrierType);
    }
}
```

**SPLINE MESH PROFILES:**

```cpp
// Different mesh profiles for different road types

FRoadMeshProfile GetRoadMeshProfile(FString RoadType)
{
    if (RoadType == "motorway")
    {
        return FRoadMeshProfile{
            .LaneWidth = 375,        // cm per lane
            .Lanes = 3,              // Per direction
            .HasMedian = true,
            .MedianWidth = 200,
            .HasShoulder = true,
            .ShoulderWidth = 250,
            .HasSidewalk = false,
            .GuardRail = true,
            .Lighting = true
        };
    }
    else if (RoadType == "primary")
    {
        return FRoadMeshProfile{
            .LaneWidth = 350,
            .Lanes = 2,
            .HasMedian = false,
            .HasShoulder = true,
            .ShoulderWidth = 100,
            .HasSidewalk = true,
            .SidewalkWidth = 150,
            .GuardRail = false,
            .Lighting = true
        };
    }
    else if (RoadType == "residential")
    {
        return FRoadMeshProfile{
            .LaneWidth = 300,
            .Lanes = 1,
            .HasMedian = false,
            .HasShoulder = false,
            .HasSidewalk = true,
            .SidewalkWidth = 150,
            .GuardRail = false,
            .Lighting = true,
            .ParkingLane = true
        };
    }
    // ... etc
}
```

**DECORATION ALONG SPLINES:**

```python
# In QGIS - calculate decoration positions

def calculate_street_light_positions(road_data, spacing=30):
    """
    Place street lights every 30m along road
    
    Returns positions along spline
    """
    spline_length = calculate_spline_length(road_data['points'])
    num_lights = int(spline_length / spacing)
    
    light_positions = []
    for i in range(num_lights):
        distance = i * spacing
        
        # Get position at distance along spline
        position, tangent = get_spline_point_at_distance(
            road_data['points'],
            distance
        )
        
        # Offset to side of road (not in middle!)
        normal = perpendicular(tangent)
        offset = road_data['width'] / 2 + 100  # 1m from road edge
        
        light_position = position + normal * offset
        
        light_positions.append({
            'position': light_position,
            'rotation': angle_from_tangent(tangent)
        })
    
    return light_positions

def calculate_roadside_tree_positions(road_data):
    """
    Place trees along road (if tagged with trees)
    """
    if 'trees' not in road_data.get('tags', {}):
        return []
    
    trees_per_km = 50  # Density
    spline_length = calculate_spline_length(road_data['points'])
    num_trees = int(spline_length / 1000 * trees_per_km)
    
    tree_positions = []
    for i in range(num_trees):
        # Random spacing for natural look
        distance = random.uniform(i * 20, (i+1) * 20)
        
        position, tangent = get_spline_point_at_distance(
            road_data['points'],
            distance
        )
        
        # Offset to side (alternating left/right)
        normal = perpendicular(tangent)
        side = 1 if i % 2 == 0 else -1
        offset = (road_data['width'] / 2 + 200) * side  # 2m from edge
        
        # Add some randomness
        offset += random.uniform(-50, 50)
        
        tree_position = position + normal * offset
        
        tree_positions.append(tree_position)
    
    return tree_positions
```

**Acceptance Criteria (UPDATED):**
- [ ] Exports roads as UE5 Spline data (not just points)
- [ ] Exports railways as smooth splines
- [ ] Exports power lines with catenary curves
- [ ] Exports rivers with flow direction
- [ ] Exports fences as splines
- [ ] Exports trails as splines
- [ ] Calculates smooth tangents for curves
- [ ] Includes width variation along splines
- [ ] Includes decoration positions (lights, trees, signs)
- [ ] UE5 plugin creates Spline Components
- [ ] UE5 plugin generates Spline Meshes
- [ ] Roads have proper width and materials
- [ ] Power lines sag realistically
- [ ] Rivers use UE5 Water Plugin
- [ ] Fences follow terrain exactly
- [ ] All splines placed on ground correctly
- [ ] Decorations spawn along splines
- [ ] Performance optimized (LODs for long splines)

---

## 🔧 SPRINT 8: POLISH & TESTING (Week 8)

### Quality & Reliability

#### TASK-701: Create Comprehensive Tests
**Status:** `[ ]` TODO  
**Priority:** HIGH  
**Estimated Time:** 4 hours  
**Agent Model:** Sonnet 4.5

**Description:**
Write unit and integration tests for all modules.

**Requirements:**
- Unit tests for each major function
- Integration tests for full pipeline
- Mock external API calls for testing
- Test error conditions
- Achieve >80% code coverage

**Test Categories:**
- Data fetching (with/without internet)
- Data processing (various inputs)
- Export (different formats)
- License validation
- UI interactions

**Acceptance Criteria:**
- [ ] All tests pass
- [ ] Coverage >80%
- [ ] CI/CD pipeline setup (GitHub Actions)

---

#### TASK-702: Error Handling & Recovery
**Status:** `[ ]` TODO  
**Priority:** HIGH  
**Estimated Time:** 3 hours  
**Agent Model:** Opus 4

**Description:**
Improve error handling throughout application.

**Requirements:**
- Try-except blocks for all risky operations
- User-friendly error messages
- Automatic retry for transient errors
- Graceful degradation (work with partial data)
- Error logging for debugging

**Acceptance Criteria:**
- [ ] No crashes on common errors
- [ ] Helpful error messages
- [ ] Errors logged properly
- [ ] User can recover from errors

---

#### TASK-703: Performance Optimization
**Status:** `[ ]` TODO  
**Priority:** MEDIUM  
**Estimated Time:** 3 hours  
**Agent Model:** Opus 4

**Description:**
Optimize for speed and memory usage.

**Focus Areas:**
- Cache downloaded data
- Parallel processing where possible
- Efficient memory usage for large datasets
- Progress callbacks (don't freeze UI)
- Lazy loading

**Targets:**
- 10km² terrain: <2 minutes total export
- Memory usage: <2GB peak
- UI remains responsive during export

**Acceptance Criteria:**
- [ ] Meets performance targets
- [ ] No memory leaks
- [ ] UI doesn't freeze

---

#### TASK-704: Documentation Complete
**Status:** `[ ]` TODO  
**Priority:** HIGH  
**Estimated Time:** 4 hours  
**Agent Model:** Sonnet 4.5

**Description:**
Create comprehensive user and developer documentation.

**Required Docs:**
1. User Guide (step-by-step tutorials)
2. Installation Guide
3. Troubleshooting Guide
4. API Documentation
5. Developer Guide (for contributors)
6. Video Tutorial Scripts

**Acceptance Criteria:**
- [ ] Non-technical user can follow guides
- [ ] All features documented
- [ ] Screenshots and examples included
- [ ] Hosted on website

---

## 🚀 SPRINT 9: PRO FEATURES (Week 9-10)

### Advanced Functionality

#### TASK-801: Batch Processing
**Status:** `[ ]` TODO  
**Priority:** MEDIUM  
**Estimated Time:** 3 hours  
**Agent Model:** Opus 4

**Description:**
Allow users to export multiple areas at once (Pro only).

**Requirements:**
- Define multiple bounding boxes
- Queue processing
- Parallel downloads (where possible)
- Combined progress tracking
- Save batch presets

**Acceptance Criteria:**
- [ ] Can define multiple areas
- [ ] Processes sequentially or parallel
- [ ] Shows overall progress
- [ ] Only available with Pro license

---

#### TASK-802: LiDAR Integration
**Status:** `[ ]` TODO  
**Priority:** LOW  
**Estimated Time:** 4 hours  
**Agent Model:** Opus 4

**Description:**
Support high-resolution LiDAR data where available (Pro).

**Requirements:**
- Detect LiDAR availability for area
- Download from national sources (Lantmäteriet for Sweden)
- Process point cloud to DEM
- Merge with SRTM where LiDAR unavailable

**Acceptance Criteria:**
- [ ] Uses LiDAR when available
- [ ] Falls back to SRTM gracefully
- [ ] Higher quality results

---

## 🌐 SPRINT 10: WEBSITE & MARKETING (Week 11-12)

### Online Presence

#### TASK-901: Build Landing Page
**Status:** `[ ]` TODO  
**Priority:** MEDIUM  
**Estimated Time:** 6 hours  
**Agent Model:** Sonnet 4.5

**Description:**
Create marketing website with Next.js.

**Pages Needed:**
- Home (hero, features, demo video)
- Pricing
- Documentation
- Download
- Blog (optional)

**Acceptance Criteria:**
- [ ] Responsive design
- [ ] Fast loading
- [ ] Clear call-to-actions
- [ ] Integrated with Stripe

---

#### TASK-902: Setup Payment System
**Status:** `[ ]` TODO  
**Priority:** HIGH  
**Estimated Time:** 4 hours  
**Agent Model:** Opus 4

**Description:**
Integrate Stripe for Pro subscriptions.

**Requirements:**
- Stripe checkout integration
- Webhook for payment confirmation
- Automatic license generation on payment
- Email confirmation
- Customer portal for subscription management

**Acceptance Criteria:**
- [ ] Can purchase Pro subscription
- [ ] License generated automatically
- [ ] User receives email with license key
- [ ] Can manage subscription

---

## 🎮 SPRINT 11: GAMEPLAY FEATURES (Week 13-14)

**Goal:** Game-specific features för olika genres

### Tactical & Military Simulation

#### TASK-1001: Tactical Analysis System (MILSIM)
**Status:** `[ ]` TODO  
**Priority:** MEDIUM  
**Estimated Time:** 4 hours  
**Agent Model:** Opus 4

**Description:**
AI-powered tactical analysis för military simulation maps.

**Features:**
- **Defensive Position Analysis:**
  - Natural cover locations (rocks, trees, buildings)
  - High ground advantages
  - Overwatch positions
  - Sniper nests
  - Fields of fire calculations
  - Concealment vs Cover differentiation

- **Fortification Suggestions:**
  - Barrier placement (HESCO, concrete, sandbags)
  - Roadblock locations
  - Checkpoint positions
  - Perimeter defense points
  - Bunker locations
  - Trench system recommendations

- **Offensive Planning:**
  - Attack vectors
  - Approach routes (covered/exposed)
  - Breach points
  - Rally points
  - Exfil locations

- **Hazards & Obstacles:**
  - Speed bumps on roads
  - Tank traps
  - Wire obstacles
  - Mine placement zones
  - IED high-risk areas
  - Anti-vehicle ditches

**AI Analysis Based On:**
- Terrain slope and elevation
- Sight lines and visibility
- Cover availability
- Road networks
- Building positions
- Water obstacles
- Vegetation density

**Export Format:**
```json
{
  "tactical_points": {
    "defensive_positions": [
      {
        "id": "def_001",
        "type": "overwatch",
        "position": [x, y, z],
        "elevation_advantage": 45.2,
        "cover_rating": "excellent",
        "sight_lines": ["north", "east"],
        "recommended_assets": ["sandbags", "mg_nest"]
      }
    ],
    "fortifications": [
      {
        "type": "barrier",
        "subtype": "hesco",
        "positions": [[x1,y1], [x2,y2]],
        "length": 50.0,
        "purpose": "road_checkpoint"
      }
    ],
    "hazards": [
      {
        "type": "speed_bump",
        "position": [x, y],
        "road_id": "way_123"
      }
    ]
  }
}
```

**Acceptance Criteria:**
- [ ] Analyzes terrain for tactical features
- [ ] Suggests realistic fortification placement
- [ ] Exports as JSON for UE5 spawning
- [ ] Configurable aggression level (light/medium/heavy fortification)
- [ ] Respects rules of engagement zones

---

#### TASK-1002: Cover & Concealment Analysis
**Status:** `[ ]` TODO  
**Priority:** MEDIUM  
**Estimated Time:** 3 hours  
**Agent Model:** Opus 4

**Description:**
Analyze and mark cover vs concealment locations.

**Features:**
- **Cover Types:**
  - Hard cover (stops bullets: concrete, thick walls)
  - Soft cover (stops some rounds: wood, thin metal)
  - Penetrable cover (delays only: bushes, thin wood)

- **Concealment:**
  - Visual concealment (hides from sight)
  - Thermal concealment
  - Shadow areas by time of day

- **Height Categories:**
  - Standing cover (>1.8m)
  - Crouching cover (0.9-1.8m)
  - Prone cover (<0.9m)

**Export:**
- Heatmaps for cover density
- Individual cover objects with ratings
- Line-of-sight blockage analysis

**Acceptance Criteria:**
- [ ] Distinguishes cover from concealment
- [ ] Rates cover quality (bullet stopping)
- [ ] Height-appropriate categorization
- [ ] Exports for UE5 AI navigation

---

#### TASK-1003: Spawn Point Intelligence
**Status:** `[ ]` TODO  
**Priority:** MEDIUM  
**Estimated Time:** 2 hours  
**Agent Model:** Sonnet 4.5

**Description:**
AI suggests optimal spawn points for different game modes.

**Spawn Types:**
- **Player Spawns:** Safe, flat, good visibility
- **Enemy Spawns:** Strategic, behind cover, flanking positions
- **Vehicle Spawns:** Road access, flat ground, protected
- **Supply Drop Zones:** Open, accessible, tactical value
- **Objective Markers:** Central, contestable, interesting

**Game Mode Support:**
- Team Deathmatch
- Capture the Flag
- King of the Hill
- Search & Destroy
- Battle Royale zones

**Acceptance Criteria:**
- [ ] Suggests balanced spawn locations
- [ ] Avoids spawn camping spots
- [ ] Per-game-mode configurations
- [ ] Export with spawn categories

---

### General Gameplay

#### TASK-1004: Navmesh Hints Generation
**Status:** `[ ]` TODO  
**Priority:** HIGH  
**Estimated Time:** 3 hours  
**Agent Model:** Opus 4

**Description:**
Generate navigation mesh hints for AI pathfinding.

**Features:**
- Walkable areas (slope < 45°)
- Jump-required zones
- Climb points
- Vaulting obstacles
- Water crossings (wade/swim)
- No-go zones (too steep, dangerous)
- Preferred paths (roads, trails)
- Off-limits areas (out of bounds)

**Export:**
- UE5 Recast Navmesh ready format
- Area types (walk, jump, swim, etc.)
- Cost modifiers (prefer roads)
- Dynamic obstacles support

**Acceptance Criteria:**
- [ ] Accurate walkable area detection
- [ ] Handles complex terrain
- [ ] Vehicle navmesh separate from infantry
- [ ] Exports as UE5 can import directly

---

#### TASK-1005: Collision Mesh Optimization
**Status:** `[ ]` TODO  
**Priority:** HIGH  
**Estimated Time:** 2 hours  
**Agent Model:** Opus 4

**Description:**
Generate optimized collision meshes separate from visual terrain.

**Features:**
- Simplified geometry (10-50x fewer polygons)
- Multiple LOD levels
- Convex decomposition for physics
- Per-material collision properties
- Separate collision for:
  - Player/character
  - Vehicles
  - Projectiles
  - Debris

**Acceptance Criteria:**
- [ ] Collision mesh matches visual closely enough
- [ ] Huge performance improvement
- [ ] No collision gaps or stuck spots
- [ ] Exports as separate files

---

## 🎨 SPRINT 12: PROCEDURAL GENERATION (Week 15-16)

**Goal:** Automatically generate detailed world elements

#### TASK-1101: Procedural Building Generation
**Status:** `[ ]` TODO  
**Priority:** MEDIUM  
**Estimated Time:** 6 hours  
**Agent Model:** Opus 4

**Description:**
Generate 3D buildings from OSM footprints.

**Features:**
- Extrude buildings from footprints
- Use OSM height data (building:levels)
- Regional architectural styles:
  - Scandinavian (Sweden, Norway)
  - European (Germany, France)
  - North American
  - Asian
  - Custom

- Building components:
  - Walls with windows
  - Roofs (flat, pitched, complex)
  - Doors and entrances
  - Balconies
  - Chimneys, antennas
  - Fire escapes

- LOD system:
  - LOD0: Full detail
  - LOD1: Simplified
  - LOD2: Box representation
  - LOD3: Billboard

**Acceptance Criteria:**
- [ ] Generates buildings from OSM data
- [ ] Respects architectural style
- [ ] Includes interior access points
- [ ] LODs work correctly
- [ ] Performance: 1000+ buildings at 60fps

---

#### TASK-1102: Procedural Road Network Enhancement
**Status:** `[ ]` TODO  
**Priority:** MEDIUM  
**Estimated Time:** 4 hours  
**Agent Model:** Opus 4

**Description:**
Enhance OSM roads with procedural details.

**Features:**
- Road meshes with proper width
- Lane markings (paint)
- Road signs (speed limits, warnings)
- Guard rails on dangerous curves
- Street lights in urban areas
- Sidewalks where appropriate
- Crosswalks at intersections
- Road damage/wear based on traffic
- Dirt road ruts and puddles

**Road Types:**
- Motorway (highway)
- Primary roads
- Secondary roads
- Residential streets
- Dirt roads
- Trails

**Acceptance Criteria:**
- [ ] Roads look realistic
- [ ] Proper topology (no gaps)
- [ ] Spline-based for smooth curves
- [ ] Assets placed logically

---

#### TASK-1103: Vegetation Distribution System
**Status:** `[ ]` TODO  
**Priority:** MEDIUM  
**Estimated Time:** 5 hours  
**Agent Model:** Opus 4

**Description:**
Procedurally place trees, bushes, and grass.

**Features:**
- Tree placement based on:
  - Satellite data (green = trees)
  - Elevation (altitude zones)
  - Slope (avoid too steep)
  - Proximity to water
  - Soil type

- Species by biome:
  - Pine forests (Pinus sylvestris)
  - Spruce forests (Picea abies)
  - Birch forests (Betula)
  - Mixed deciduous
  - Tropical/exotic (for other regions)

- Density variation:
  - Dense forest
  - Open woodland
  - Scattered trees
  - Individual specimens

- Understory:
  - Bushes
  - Ferns
  - Grass (different heights)
  - Flowers (seasonal)
  - Fallen logs
  - Rocks

**Output:**
- Foliage spawn rules for UE5
- Instance data for millions of trees
- LOD crossfade distances
- Wind animation parameters

**Acceptance Criteria:**
- [ ] Realistic forest distribution
- [ ] Performance: 100k+ trees at 60fps
- [ ] Seasonal variation support
- [ ] Respects clearings (roads, buildings)

---

#### TASK-1104: Fence & Wall Generation
**Status:** `[ ]` TODO  
**Priority:** LOW  
**Estimated Time:** 3 hours  
**Agent Model:** Sonnet 4.5

**Description:**
Auto-generate fences and walls along boundaries.

**Features:**
- Property boundaries (cadastral data)
- Stone walls (rural Sweden common)
- Wooden fences (farms, residential)
- Chain-link fences (industrial)
- Highway barriers (concrete, metal)
- Gates at access points

**Placement Logic:**
- Follow cadastral boundaries
- Follow roads (highway barriers)
- Around buildings (residential fences)
- Farm perimeters
- Adapt to terrain slope

**Acceptance Criteria:**
- [ ] Fences follow boundaries smoothly
- [ ] Proper gates at logical points
- [ ] Matches regional style
- [ ] Spline-based deformation

---

#### TASK-1105: Scatter Detail Objects
**Status:** `[ ]` TODO  
**Priority:** LOW  
**Estimated Time:** 2 hours  
**Agent Model:** Sonnet 4.5

**Description:**
Scatter small detail objects for realism.

**Objects to Scatter:**
- **Forests:** Fallen logs, stumps, rocks, mushrooms, pine cones
- **Rivers:** Stones, driftwood, reeds
- **Fields:** Hay bales, farm equipment, scattered rocks
- **Urban:** Trash bins, benches, planters, bikes
- **Roads:** Road debris, small rocks, tire marks
- **Mountains:** Loose rocks, scree, snow patches

**Rules:**
- Context-aware (correct biome)
- Density variation (clustered, not uniform)
- Avoid roads and buildings
- Slope-appropriate
- Size variation

**Acceptance Criteria:**
- [ ] Natural-looking distribution
- [ ] Performance optimized (instancing)
- [ ] Easy to toggle on/off per category

---

## 🌦️ SPRINT 13: ENVIRONMENT & ATMOSPHERE (Week 17)

**Goal:** Weather, seasons, lighting, audio

#### TASK-1201: Seasonal Variation Export
**Status:** `[ ]` TODO  
**Priority:** MEDIUM  
**Estimated Time:** 4 hours  
**Agent Model:** Opus 4

**Description:**
Export 4 seasonal versions of terrain.

**Per Season:**
- **Spring:**
  - Fresh green vegetation
  - Melting snow at high altitudes
  - Muddy areas
  - Blooming flowers
  - Increased water flow

- **Summer:**
  - Lush green
  - Full foliage
  - Dry riverbeds (drought)
  - Maximum grass height
  - Warm color palette

- **Autumn:**
  - Orange/red/yellow foliage
  - Falling leaves ground layer
  - Reduced vegetation
  - Harvest fields (cut)
  - Overcast lighting preset

- **Winter:**
  - Snow coverage (altitude-based)
  - Bare deciduous trees
  - Ice on water bodies
  - Reduced grass
  - Blue-tinted lighting

**Exports:**
- 4x material mask sets
- 4x color grading LUTs
- 4x foliage density maps
- Seasonal lighting presets

**Acceptance Criteria:**
- [ ] Visually distinct seasons
- [ ] Realistic transitions
- [ ] Performance similar across seasons
- [ ] Easy switching in UE5

---

#### TASK-1202: Weather Data Integration
**Status:** `[ ]` TODO  
**Priority:** LOW  
**Estimated Time:** 3 hours  
**Agent Model:** Sonnet 4.5

**Description:**
Fetch and integrate real weather data.

**Data Sources:**
- Historical weather (SMHI for Sweden, NOAA globally)
- Average temperature by month
- Precipitation patterns
- Wind direction/speed
- Cloud coverage
- Fog frequency

**Use Cases:**
- Realistic weather system settings
- Seasonal accuracy
- Regional climate matching
- Dynamic weather probabilities

**Export:**
- Weather preset JSON
- UE5 Weather system configs
- Probability tables

**Acceptance Criteria:**
- [ ] Accurate for location
- [ ] Monthly variation data
- [ ] Usable in UE5 weather systems

---

#### TASK-1203: Water Flow Simulation
**Status:** `[ ]` TODO  
**Priority:** MEDIUM  
**Estimated Time:** 4 hours  
**Agent Model:** Opus 4

**Description:**
Simulate water flow from elevation data.

**Features:**
- River path generation (high to low)
- Lake formation (natural basins)
- Waterfall detection
- Flow direction maps
- Flow velocity estimation
- Flood zone prediction
- Watershed boundaries

**Physics:**
- Follows gravity
- Accumulates in basins
- Carves channels over time (erosion)
- Splits/merges streams

**Export:**
- Water body polygons
- Flow direction texture
- Velocity map
- Depth map
- UE5 Water plugin ready

**Acceptance Criteria:**
- [ ] Realistic river paths
- [ ] Lakes in correct locations
- [ ] Waterfalls at elevation drops
- [ ] No water flowing uphill!

---

#### TASK-1204: Sound Occlusion Maps
**Status:** `[ ]` TODO  
**Priority:** LOW  
**Estimated Time:** 2 hours  
**Agent Model:** Sonnet 4.5

**Description:**
Generate audio occlusion data for 3D sound.

**Analysis:**
- Line-of-sight to sound sources
- Material-based dampening (forest, buildings, terrain)
- Echo zones (valleys, canyons)
- Reverb zones (urban, caves)
- Open area propagation

**Export:**
- Occlusion volume data
- Reverb zone definitions
- Material acoustic properties
- UE5 Audio Volume setup

**Acceptance Criteria:**
- [ ] Realistic sound propagation
- [ ] Forests dampen sound
- [ ] Valleys create echoes
- [ ] Performance efficient

---

#### TASK-1205: Time of Day Calculation
**Status:** `[ ]` TODO  
**Priority:** LOW  
**Estimated Time:** 2 hours  
**Agent Model:** Sonnet 4.5

**Description:**
Calculate sun/moon positions for location and date.

**Features:**
- Sun path through day
- Sunrise/sunset times
- Golden hour timing
- Blue hour timing
- Seasonal sun angle variation
- Moon phases and position
- Shadow length predictions

**Export:**
- UE5 Directional Light presets
- Sky sphere settings
- Time of day curve data
- Seasonal light color LUTs

**Acceptance Criteria:**
- [ ] Astronomically accurate
- [ ] Works for any location/date
- [ ] Exports UE5-ready lighting

---

## 🎨 SPRINT 14: ARTIST TOOLS (Week 18)

**Goal:** Tools for artists and level designers

#### TASK-1301: Reference Photo Collection
**Status:** `[ ]` TODO  
**Priority:** LOW  
**Estimated Time:** 3 hours  
**Agent Model:** Sonnet 4.5

**Description:**
Collect reference photos from area.

**Sources:**
- Google Street View (where available)
- Flickr with location tags
- Wikimedia Commons
- Mapillary (crowdsourced street photos)

**Organization:**
- By location (grid)
- By category (buildings, nature, roads)
- By season (if multiple available)
- Metadata (date, location, source)

**Export:**
- Folder structure with images
- Index JSON with metadata
- Contact sheet overview

**Acceptance Criteria:**
- [ ] Fetches available photos
- [ ] Organized logically
- [ ] Copyright info included
- [ ] Easy to browse

---

#### TASK-1302: Color Palette Extraction
**Status:** `[ ]` TODO  
**Priority:** LOW  
**Estimated Time:** 2 hours  
**Agent Model:** Sonnet 4.5

**Description:**
Extract color palettes from satellite imagery.

**Analysis:**
- Dominant colors (5-10 main colors)
- Sky color
- Vegetation color (seasonal)
- Earth tones
- Water color
- Urban grays

**Output:**
- Hex codes
- RGB values
- UE5 Material parameter collection
- Photoshop/Substance swatch file
- Color mood board image

**Acceptance Criteria:**
- [ ] Representative colors extracted
- [ ] Usable in UE5/art tools
- [ ] Seasonal variants available

---

#### TASK-1303: Minimap Generation
**Status:** `[ ]` TODO  
**Priority:** MEDIUM  
**Estimated Time:** 3 hours  
**Agent Model:** Sonnet 4.5

**Description:**
Auto-generate minimap for games.

**Features:**
- Top-down orthographic view
- Styled rendering (not just satellite)
- Road highlighting
- Building outlines
- Water bodies in blue
- Forests in green
- POI markers
- Grid overlay (optional)

**Zoom Levels:**
- Strategic (full map)
- Tactical (local area)
- Detail (immediate vicinity)

**Export Formats:**
- PNG (various sizes)
- Vector SVG (scalable)
- UE5 Widget ready
- Unity Sprite

**Acceptance Criteria:**
- [ ] Clear and readable
- [ ] Proper styling
- [ ] Multiple zoom levels
- [ ] Updates if terrain changes

---

#### TASK-1304: Viewshed Analysis
**Status:** `[ ]` TODO  
**Priority:** LOW  
**Estimated Time:** 3 hours  
**Agent Model:** Opus 4

**Description:**
Calculate what's visible from specific points.

**Use Cases:**
- Scenic overlook placement
- Sniper position analysis
- Surveillance camera coverage
- Privacy analysis (what neighbors see)
- Tourism viewpoint rating

**Features:**
- 360° visibility calculation
- Distance-based visibility (fog of war)
- Terrain occlusion
- Building occlusion
- Forest occlusion (partial)
- Time of day (shadows)

**Visualization:**
- Heatmap (green=visible, red=hidden)
- 3D visualization in UE5
- Coverage percentage

**Acceptance Criteria:**
- [ ] Accurate line-of-sight
- [ ] Handles complex terrain
- [ ] Fast computation (<1 min for point)
- [ ] Export as texture/data

---

## 🚀 SPRINT 15: WORKFLOW ENHANCEMENT (Week 19)

**Goal:** Speed up and streamline workflows

#### TASK-1401: Template System
**Status:** `[ ]` TODO  
**Priority:** MEDIUM  
**Estimated Time:** 3 hours  
**Agent Model:** Sonnet 4.5

**Description:**
Save and load export configuration templates.

**Templates Include:**
- Area size/resolution
- Enabled data sources
- Material settings
- OSM feature filters
- Export format preferences
- Post-processing options

**Built-in Templates:**
- "Quick Preview" (low res, fast)
- "High Quality" (max quality)
- "City Center" (urban focus)
- "Wilderness" (nature focus)
- "Military Sim" (tactical features)
- "Racing Track" (road focus)

**Features:**
- Save custom templates
- Share templates (export/import)
- Template marketplace (future)
- Version templates
- Template categories

**Acceptance Criteria:**
- [ ] Can save/load templates
- [ ] Built-in templates work
- [ ] Import/export templates
- [ ] User-friendly UI

---

#### TASK-1402: Multi-Resolution Pyramid
**Status:** `[ ]` TODO  
**Priority:** HIGH  
**Estimated Time:** 3 hours  
**Agent Model:** Opus 4

**Description:**
Export same terrain in multiple resolutions.

**Resolution Levels:**
- **Ultra:** 1m per pixel (close-up detail)
- **High:** 5m per pixel (standard gameplay)
- **Medium:** 10m per pixel (medium distance)
- **Low:** 30m per pixel (far LOD)
- **Preview:** 100m per pixel (quick loading)

**Smart Loading:**
- UE5 World Partition integration
- Auto LOD switching
- Streaming based on camera distance
- Memory-efficient

**Export:**
- All 5 resolutions
- LOD transition data
- Streaming configuration
- Memory budget recommendations

**Acceptance Criteria:**
- [ ] All resolutions match perfectly
- [ ] Seamless LOD transitions
- [ ] Huge performance improvement
- [ ] Easy UE5 setup

---

#### TASK-1403: Tile System for Massive Worlds
**Status:** `[ ]` TODO  
**Priority:** MEDIUM  
**Estimated Time:** 4 hours  
**Agent Model:** Opus 4

**Description:**
Split huge areas into manageable tiles.

**Features:**
- Auto-tile large areas (>25km²)
- Configurable tile size (5km, 10km, 20km)
- Overlap zones for seamless blending
- Coordinate system per tile
- Batch export all tiles
- Tile index/manifest

**Tile Naming:**
```
terrain_tile_x0_y0/
terrain_tile_x1_y0/
terrain_tile_x0_y1/
...
```

**World Partition:**
- UE5 World Partition ready
- Auto-loading boundaries
- Streaming optimization
- Memory budget per tile

**Acceptance Criteria:**
- [ ] Tiles join seamlessly
- [ ] No visible seams
- [ ] Handles 100km+ worlds
- [ ] Batch export works

---

#### TASK-1404: Change Detection & Updates
**Status:** `[ ]` TODO  
**Priority:** LOW  
**Estimated Time:** 3 hours  
**Agent Model:** Opus 4

**Description:**
Detect what changed and only re-export that.

**Change Detection:**
- Compare current export vs previous
- Detect satellite image updates
- Detect OSM data changes
- Detect elevation data updates (rare)

**Smart Re-export:**
- Only changed tiles
- Incremental updates
- Version control
- Changelog generation

**Use Cases:**
- Iterative development
- Live-service games (world updates)
- Seasonal updates
- Bug fix re-exports

**Acceptance Criteria:**
- [ ] Accurately detects changes
- [ ] Only re-exports needed parts
- [ ] 10-100x faster for small changes
- [ ] Version history tracking

---

## 📊 SPRINT 16: DATA & ANALYSIS (Week 20)

**Goal:** Analytics and insights

#### TASK-1501: Terrain Statistics Dashboard
**Status:** `[ ]` TODO  
**Priority:** LOW  
**Estimated Time:** 3 hours  
**Agent Model:** Sonnet 4.5

**Description:**
Generate comprehensive terrain statistics.

**Statistics:**
- Min/max/avg elevation
- Total area (km²)
- Slope distribution histogram
- Aspect (direction) rose
- Land cover percentages:
  - Forest: X%
  - Urban: Y%
  - Water: Z%
  - Agriculture: W%
- Road network length
- Building count
- Population estimate

**Visualization:**
- Charts and graphs
- Comparison to other areas
- Difficulty rating (for gameplay)
- Suitability scores (racing, hiking, tactical)

**Export:**
- PDF report
- JSON data
- Dashboard in plugin UI

**Acceptance Criteria:**
- [ ] Accurate statistics
- [ ] Visual presentation
- [ ] Easy to understand
- [ ] Useful for planning

---

#### TASK-1502: Biome Transition Analysis
**Status:** `[ ]` TODO  
**Priority:** LOW  
**Estimated Time:** 2 hours  
**Agent Model:** Opus 4

**Description:**
Analyze and smooth biome transitions.

**Features:**
- Detect biome boundaries
- Identify ecotones (transition zones)
- Generate gradient blending
- Validate ecological accuracy
- Suggest improvements

**Biome Types:**
- Alpine (high elevation)
- Montane forest
- Lowland forest
- Wetlands
- Agricultural
- Urban
- Water

**Export:**
- Biome classification map
- Transition zones
- Blending rules
- Ecological notes

**Acceptance Criteria:**
- [ ] Realistic biome placement
- [ ] Smooth transitions
- [ ] Ecologically sound
- [ ] Easy artist override

---

## 🎯 SPRINT 17: GAME GENRE SPECIFIC (Week 21)

**Goal:** Features for specific game types

#### TASK-1601: Racing Game Optimization
**Status:** `[ ]` TODO  
**Priority:** LOW  
**Estimated Time:** 3 hours  
**Agent Model:** Opus 4

**Description:**
Optimize road network for racing games.

**Features:**
- Road quality rating
- Corner analysis (tight/wide/chicane)
- Straight sections (top speed zones)
- Elevation changes (challenging)
- Dangerous sections (cliffs, narrow)
- Track loop detection
- Lap time estimation

**Track Suggestions:**
- Point-to-point routes
- Circuit routes
- Rally stages
- Off-road trails

**Export:**
- Race track splines
- Checkpoint suggestions
- Sector divisions
- Timing gates
- Leaderboard zones

**Acceptance Criteria:**
- [ ] Identifies good racing roads
- [ ] Analyzes difficulty
- [ ] Exports track data
- [ ] Works with racing game logic

---

#### TASK-1602: Survival Game Resource Map
**Status:** `[ ]` TODO  
**Priority:** LOW  
**Estimated Time:** 2 hours  
**Agent Model:** Sonnet 4.5

**Description:**
Generate resource distribution for survival games.

**Resources:**
- **Water:** Rivers, lakes (highest priority)
- **Food:** Forests (hunting), fields (foraging)
- **Shelter:** Caves, overhangs, buildings
- **Materials:**
  - Wood (forests)
  - Stone (mountains)
  - Metal (near water/caves)
- **Danger Zones:**
  - Avalanche risk
  - Flood zones
  - Exposure (no shelter)

**Difficulty Zones:**
- Safe starter areas
- Medium challenge zones
- Extreme survival areas

**Export:**
- Resource spawn rules
- Danger zone polygons
- Difficulty heatmap

**Acceptance Criteria:**
- [ ] Logical resource placement
- [ ] Balanced difficulty progression
- [ ] Realistic survival challenges

---

## 🌐 SPRINT 18: CLOUD & COLLABORATION (Week 22)

**Goal:** Cloud processing and team features

#### TASK-1701: Cloud Processing Queue
**Status:** `[ ]` TODO  
**Priority:** MEDIUM  
**Estimated Time:** 6 hours  
**Agent Model:** Opus 4

**Description:**
Offload large jobs to cloud processing.

**Features:**
- Upload job to cloud
- Progress tracking
- Email notification when done
- Download results
- Job queue management
- Priority processing (Pro)

**Use Cases:**
- 100x100km exports
- Batch processing 50+ tiles
- High-res LiDAR processing
- Overnight processing

**Infrastructure:**
- AWS Lambda / Google Cloud Functions
- Supabase storage for results
- Queue system (Redis)
- Cost estimation before processing

**Acceptance Criteria:**
- [ ] Can submit large jobs
- [ ] Reliable processing
- [ ] Email notifications work
- [ ] Reasonable pricing

---

## 🎨 SPRINT 19: ADVANCED MATERIALS & TEXTURES (Week 23)

**Goal:** Professional material generation and detail

#### TASK-1801: Erosion Pattern Generation
**Status:** `[ ]` TODO  
**Priority:** MEDIUM  
**Estimated Time:** 4 hours  
**Agent Model:** Opus 4

**Description:**
Generate realistic erosion patterns for added terrain detail.

**Features:**
- Water erosion channels (rain runoff paths)
- Wind erosion patterns (exposed areas)
- Weathering on rock faces
- Crack patterns on stone
- Soil displacement visualization
- Age-based weathering intensity

**Analysis Based On:**
- Slope angle (water flows down)
- Rainfall data (wet climates = more erosion)
- Vegetation coverage (roots prevent erosion)
- Rock type hardness
- Prevailing wind direction

**Export:**
- Erosion detail textures (normal maps)
- Flow direction maps
- Weathering intensity masks
- UE5 Material layer parameters

**Acceptance Criteria:**
- [ ] Realistic erosion patterns
- [ ] Matches geological processes
- [ ] Adds visual detail to terrain
- [ ] Performance friendly (texture-based)

---

#### TASK-1802: Trail Network Generation
**Status:** `[ ]` TODO  
**Priority:** MEDIUM  
**Estimated Time:** 3 hours  
**Agent Model:** Opus 4

**Description:**
Generate hiking trails, bike paths, and animal paths.

**Trail Types:**
- Hiking trails (connects viewpoints, POIs)
- Mountain bike trails (follows elevation contours)
- Cross-country ski tracks (winter, flat-ish terrain)
- Animal paths (between water and shelter)
- Game trails (deer, elk through forests)

**Generation Logic:**
- Prefer scenic routes
- Avoid very steep slopes (>30° for hiking)
- Connect natural POIs (lakes, peaks, valleys)
- Follow ridge lines for views
- Use existing clearings
- Respect private property (where data available)

**Attributes:**
- Difficulty rating (easy, moderate, hard, extreme)
- Surface type (dirt, gravel, rock)
- Width (single-track, double-track, wide path)
- Seasonal availability
- Distance and elevation gain

**Export:**
- Trail splines
- Difficulty markers
- Surface materials
- Signage locations
- Parking/trailhead suggestions

**Acceptance Criteria:**
- [ ] Trails look natural
- [ ] Connect logical points
- [ ] Difficulty ratings accurate
- [ ] Good for outdoor/adventure games

---

#### TASK-1803: Geology Layer Integration
**Status:** `[ ]` TODO  
**Priority:** LOW  
**Estimated Time:** 3 hours  
**Agent Model:** Opus 4

**Description:**
Integrate geological data for realistic material placement.

**Data Sources:**
- Geological survey data (SGU for Sweden, USGS for USA)
- Bedrock type maps
- Soil composition maps
- Groundwater data
- Mineral deposits

**Use Cases:**
- Realistic rock material placement (granite vs limestone)
- Soil color accuracy
- Cave system likelihood
- Mining locations (historical/potential)
- Foundation stability (for building placement)

**Material Mapping:**
- Granite → Gray, hard, resistant
- Limestone → Beige, weathered, caves
- Sandstone → Red/tan, eroded
- Clay → Dense vegetation, smooth
- Sand → Loose, dunes, beaches

**Export:**
- Geological layer masks
- Material property data
- Cave probability maps
- Mining site markers

**Acceptance Criteria:**
- [ ] Geologically accurate materials
- [ ] Regional variation correct
- [ ] Useful for simulation/education
- [ ] Optional (not required for games)

---

## 🎮 SPRINT 20: ADVANCED GAMEPLAY SYSTEMS (Week 24)

**Goal:** Deep gameplay integration features

#### TASK-1901: Asset Library Integration
**Status:** `[ ]` TODO  
**Priority:** MEDIUM  
**Estimated Time:** 5 hours  
**Agent Model:** Opus 4

**Description:**
Auto-detect and suggest matching assets from libraries.

**Integration With:**
- Quixel Megascans (Epic's library)
- Unreal Marketplace
- Sketchfab (public domain)
- User's local asset library

**Smart Matching:**
- Tree species → Correct 3D tree models
- Building types → Architectural style matches
- Rock types → Geological accuracy
- Road surfaces → Asphalt, gravel, dirt textures
- Vegetation biomes → Regional plant species

**Features:**
- Asset recommendation engine
- Preview thumbnails
- One-click apply suggestions
- Bulk import matched assets
- Custom asset library support

**Export:**
- Asset mapping file (OSM type → Asset path)
- Download list (for marketplace assets)
- Import script for UE5

**Acceptance Criteria:**
- [ ] Suggests relevant assets
- [ ] Reduces manual asset hunting
- [ ] Works with major libraries
- [ ] User can override suggestions

---

#### TASK-1902: Population Density Integration
**Status:** `[ ]` TODO  
**Priority:** LOW  
**Estimated Time:** 2 hours  
**Agent Model:** Sonnet 4.5

**Description:**
Import population density data for NPC spawning.

**Data Sources:**
- Census data (SCB for Sweden, Census Bureau for USA)
- OpenStreetMap building tags (residential vs commercial)
- Night-time light satellite data (activity heatmap)
- Mobile phone density data (where available)

**Use Cases:**
- Realistic crowd density in cities
- Empty rural areas
- Rush hour traffic simulation
- Event gathering spots (stadiums, parks)
- Zombie apocalypse population distribution

**Export:**
- Population heatmap texture
- Per-building occupancy estimates
- Traffic density zones
- Activity pattern data (day/night)

**Acceptance Criteria:**
- [ ] Realistic population distribution
- [ ] Useful for NPC spawning
- [ ] Time-of-day variation
- [ ] Privacy-respecting (aggregated data)

---

#### TASK-1903: Historical Change Visualization
**Status:** `[ ]` TODO  
**Priority:** LOW  
**Estimated Time:** 3 hours  
**Agent Model:** Sonnet 4.5

**Description:**
Show how area changed over time.

**Features:**
- Compare satellite imagery from different years
- Detect changes:
  - New buildings
  - Deforestation
  - Urban expansion
  - Road construction
  - Natural disasters (fire, flood)

**Timeline:**
- 1990s (if available)
- 2000s
- 2010s
- 2020s
- Current

**Visualization:**
- Before/after slider
- Change heatmap (red=demolished, green=built)
- Timeline animation
- Change statistics

**Use Cases:**
- Historical storytelling
- Urban planning visualization
- Disaster impact assessment
- Time-travel game mechanics
- Educational content

**Export:**
- Multiple terrain versions (per decade)
- Change detection masks
- Annotation markers

**Acceptance Criteria:**
- [ ] Accurate change detection
- [ ] Visual timeline
- [ ] Useful for storytelling
- [ ] Not all regions have historical data (graceful fallback)

---

## 🎯 SPRINT 21: PERFORMANCE & OPTIMIZATION (Week 25)

**Goal:** Make everything faster and more efficient

#### TASK-2001: Memory Optimization System
**Status:** `[ ]` TODO  
**Priority:** HIGH  
**Estimated Time:** 4 hours  
**Agent Model:** Opus 4

**Description:**
Optimize memory usage for large terrains.

**Techniques:**
- Lazy loading (load on demand)
- Tile-based streaming
- Texture compression
- Mesh LOD system
- Object pooling
- Cache management

**Targets:**
- 10km² terrain: <2GB RAM
- 100km² terrain: <8GB RAM
- Smooth 60fps on mid-range PC

**Features:**
- Memory profiler (show usage)
- Optimization suggestions
- Auto-optimization option
- Platform-specific presets (PC, console, mobile)

**Acceptance Criteria:**
- [ ] Meets memory targets
- [ ] No memory leaks
- [ ] Fast loading times
- [ ] Smooth performance

---

#### TASK-2002: Export Format Optimization
**Status:** `[ ]` TODO  
**Priority:** MEDIUM  
**Estimated Time:** 3 hours  
**Agent Model:** Opus 4

**Description:**
Optimize file formats for size and speed.

**Formats:**
- Heightmaps: 16-bit PNG (compression) vs RAW (speed)
- Textures: JPEG (size) vs TGA (quality) vs DDS (GPU-ready)
- Meshes: FBX (compatibility) vs glTF (modern) vs UE5 native
- Data: JSON (readable) vs MessagePack (compact) vs Binary

**Smart Selection:**
- User chooses priority (size vs speed vs quality)
- Auto-recommend best format
- Batch conversion
- Compression level control

**Benchmarks:**
- 10km² terrain: <500MB total export
- Compression: 50-80% size reduction
- Import speed: <2 minutes in UE5

**Acceptance Criteria:**
- [ ] Smaller file sizes
- [ ] Fast import times
- [ ] No quality loss (lossless option)
- [ ] Multiple format support

---

## 📱 SPRINT 22: EXTENDED PLATFORMS (Week 26)

**Goal:** Support more platforms and tools

#### TASK-2101: Unity Plugin
**Status:** `[ ]` TODO  
**Priority:** MEDIUM  
**Estimated Time:** 8 hours  
**Agent Model:** Opus 4

**Description:**
Create Unity version of import plugin.

**Features:**
- Import RealTerrain Studio exports
- Create Unity Terrain
- Apply materials and textures
- Spawn prefabs from OSM data
- Unity-specific optimizations

**Unity Terrain System:**
- Heightmap import
- Texture splatmaps
- Tree/grass placement
- Detail objects

**Differences from UE5:**
- Different material system
- Different LOD approach
- Different streaming system

**Acceptance Criteria:**
- [ ] Works in Unity 2021+
- [ ] Feature parity with UE5 plugin
- [ ] Unity Asset Store ready
- [ ] Documentation for Unity users

---

#### TASK-2102: Godot Plugin
**Status:** `[ ]` TODO  
**Priority:** LOW  
**Estimated Time:** 6 hours  
**Agent Model:** Opus 4

**Description:**
Support Godot Engine (open-source game engine).

**Features:**
- Import to Godot 4.x
- Terrain generation
- Material application
- Object spawning

**Why Godot:**
- Growing indie community
- Open source
- Cross-platform
- Free alternative to Unity/Unreal

**Acceptance Criteria:**
- [ ] Works in Godot 4.0+
- [ ] Basic feature set
- [ ] Community contribution friendly
- [ ] Documentation

---

#### TASK-2103: Blender Integration
**Status:** `[ ]` TODO  
**Priority:** LOW  
**Estimated Time:** 4 hours  
**Agent Model:** Sonnet 4.5

**Description:**
Import terrains into Blender for rendering/editing.

**Use Cases:**
- Architectural visualization
- Cinematic renders
- Manual editing/sculpting
- Animation backgrounds

**Features:**
- Import heightmap as mesh
- Apply satellite texture
- Import OSM objects as curves/meshes
- Material node setup

**Blender-Specific:**
- Displacement modifier setup
- Cycles/Eevee materials
- Geometry nodes for details
- Camera suggestions

**Acceptance Criteria:**
- [ ] Clean import into Blender
- [ ] Render-ready materials
- [ ] Editable geometry
- [ ] Documentation for artists

---

## 🎓 SPRINT 23: EDUCATIONAL & SPECIAL USE (Week 27)

**Goal:** Features for education and niche markets

#### TASK-2201: Educational Mode
**Status:** `[ ]` TODO  
**Priority:** LOW  
**Estimated Time:** 3 hours  
**Agent Model:** Sonnet 4.5

**Description:**
Special features for schools and education.

**Features:**
- Simplified UI (students)
- Pre-made lesson templates
- Geography quiz mode
- Geological layer explanations
- Climate zone teaching
- Virtual field trips

**Teacher Tools:**
- Assignment templates
- Student progress tracking
- Collaboration projects
- Presentation mode

**Example Lessons:**
- "How mountains form" (geology)
- "Water cycle visualization" (hydrology)
- "Climate zones" (geography)
- "Urban planning" (social studies)
- "Ecosystem simulation" (biology)

**Acceptance Criteria:**
- [ ] Age-appropriate interface
- [ ] Curriculum-aligned content
- [ ] Teacher dashboard
- [ ] Student-safe (no external links)

---

#### TASK-2202: Flight Simulator Data Export
**Status:** `[ ]` TODO  
**Priority:** LOW  
**Estimated Time:** 4 hours  
**Agent Model:** Opus 4

**Description:**
Export data compatible with flight simulators.

**Flight Sim Specific:**
- Airport locations (ICAO codes from OSM)
- Runway data (length, heading, elevation)
- Navigation beacons (VOR, NDB positions)
- Airspace boundaries
- Landmark identification
- Flight path suggestions
- Terrain mesh for collision

**Supported Sims:**
- Microsoft Flight Simulator 2020
- X-Plane 12
- DCS World
- Custom flight games

**Export:**
- Terrain mesh (LOD optimized)
- Airport definitions
- Navigation data (XML/CSV)
- Landmark database

**Acceptance Criteria:**
- [ ] Accurate aviation data
- [ ] Compatible with major sims
- [ ] Proper coordinate systems
- [ ] Performance optimized for flight

---

#### TASK-2203: Disaster Simulation Data
**Status:** `[ ]` TODO  
**Priority:** LOW  
**Estimated Time:** 3 hours  
**Agent Model:** Opus 4

**Description:**
Export data for disaster planning and simulation.

**Disaster Types:**
- Flooding (water flow + elevation)
- Wildfire spread (vegetation + wind)
- Earthquake damage (building vulnerability)
- Avalanche risk (slope + snow)
- Hurricane impact (coastal + wind)

**Risk Analysis:**
- High-risk zones
- Evacuation routes
- Safe zones
- Emergency service access
- Resource locations (hospitals, shelters)

**Use Cases:**
- Emergency planning
- Training simulations
- Public awareness
- Research and education

**Export:**
- Risk heatmaps
- Evacuation plans
- Resource markers
- Simulation parameters

**Acceptance Criteria:**
- [ ] Scientifically accurate
- [ ] Useful for planners
- [ ] Visualization tools
- [ ] Documentation for emergency services

---

## 🎬 SPRINT 24: VIRTUAL PRODUCTION (Week 28)

**Goal:** Film and TV production features

#### TASK-2301: Camera Path Generation
**Status:** `[ ]` TODO  
**Priority:** LOW  
**Estimated Time:** 4 hours  
**Agent Model:** Opus 4

**Description:**
Generate cinematic camera paths automatically.

**Features:**
- Scenic flight paths
- Ground-level dolly moves
- Establishing shots (wide to close)
- Follow terrain features
- Rule of thirds composition
- Speed ramping

**Path Types:**
- Aerial flyover
- Orbit around point
- Dolly track (ground)
- Crane movement
- Handheld simulation

**Export:**
- UE5 Sequencer format
- Keyframe data
- Speed curves
- Camera settings (FOV, aperture)

**Acceptance Criteria:**
- [ ] Smooth, cinematic paths
- [ ] Customizable speed/timing
- [ ] Exports to UE5 Sequencer
- [ ] Preview in QGIS (2D path)

---

#### TASK-2302: Lighting Rig Presets
**Status:** `[ ]` TODO  
**Priority:** LOW  
**Estimated Time:** 3 hours  
**Agent Model:** Sonnet 4.5

**Description:**
Pre-configured lighting setups based on location/time.

**Presets Based On:**
- Geographic location (latitude affects sun angle)
- Date and time
- Season
- Weather conditions

**Lighting Components:**
- Sun position/color
- Sky atmosphere
- Volumetric fog
- Cloud settings
- Moon/stars (night)

**Cinematic Presets:**
- Golden hour (sunrise/sunset)
- Blue hour (twilight)
- Harsh noon (overhead sun)
- Overcast day
- Stormy weather
- Night (moonlit)

**Export:**
- UE5 Lighting settings
- HDRI recommendations
- Post-process volumes
- Sequencer lighting setup

**Acceptance Criteria:**
- [ ] Realistic lighting
- [ ] Astronomically accurate
- [ ] Quick setup in UE5
- [ ] Matches real-world conditions

---

## 🔧 SPRINT 25: DEVELOPER TOOLS (Week 29)

**Goal:** Tools for advanced users and studios

#### TASK-2401: Python Scripting API
**Status:** `[ ]` TODO  
**Priority:** MEDIUM  
**Estimated Time:** 5 hours  
**Agent Model:** Opus 4

**Description:**
Expose Python API for automation and customization.

**API Features:**
```python
from realterrain import Studio

# Initialize
studio = Studio()

# Define area
bbox = studio.create_bbox(
    min_lon=-122.5, min_lat=37.7,
    max_lon=-122.4, max_lat=37.8
)

# Configure export
config = studio.ExportConfig(
    resolution=10,  # meters
    sources=['elevation', 'satellite', 'osm'],
    materials=True,
    osm_filters=['highway', 'building']
)

# Export
result = studio.export(bbox, config, output_dir='./exports')

# Access results
print(f"Heightmap: {result.heightmap_path}")
print(f"Satellite: {result.satellite_path}")
print(f"Statistics: {result.stats}")
```

**Advanced Features:**
- Batch processing loops
- Custom data source integration
- Post-processing hooks
- Event callbacks
- Error handling

**Acceptance Criteria:**
- [ ] Clean, documented API
- [ ] Example scripts included
- [ ] Stable and backwards-compatible
- [ ] Unit tested

---

#### TASK-2402: Command Line Interface
**Status:** `[ ]` TODO  
**Priority:** MEDIUM  
**Estimated Time:** 3 hours  
**Agent Model:** Sonnet 4.5

**Description:**
CLI tool for headless/automated workflows.

**Usage:**
```bash
# Basic export
realterrain export \
  --bbox "-122.5,37.7,-122.4,37.8" \
  --resolution 10 \
  --output ./terrain_001

# With config file
realterrain export --config terrain_config.json

# Batch processing
realterrain batch areas.csv --parallel 4

# Validate license
realterrain license activate XXXX-XXXX-XXXX-XXXX

# Show stats
realterrain stats --bbox "..." --format json
```

**Features:**
- All GUI features available
- Config file support (JSON/YAML)
- Progress bars
- Logging to file
- Exit codes for CI/CD
- Parallel processing

**Acceptance Criteria:**
- [ ] Feature parity with GUI
- [ ] Works on Windows/Mac/Linux
- [ ] Good error messages
- [ ] Documentation and examples

---

#### TASK-2403: Custom Data Layer Support
**Status:** `[ ]` TODO  
**Priority:** MEDIUM  
**Estimated Time:** 4 hours  
**Agent Model:** Opus 4

**Description:**
Allow users to import their own custom GIS data.

**Supported Formats:**
- Shapefiles (.shp)
- GeoJSON
- KML/KMZ (Google Earth)
- GPX (GPS tracks)
- CSV with coordinates
- GeoTIFF (raster data)

**Use Cases:**
- Proprietary survey data
- Custom POI markers
- Private property boundaries
- Archaeological sites
- Wildlife tracking data
- Custom annotations

**Integration:**
- Merge with OSM data
- Layer priority system
- Custom styling
- Export alongside standard data

**Acceptance Criteria:**
- [ ] Reads common GIS formats
- [ ] Validates data quality
- [ ] Integrates with export
- [ ] Preserves attributes

---

## 💰 SPRINT 26: MONETIZATION & BUSINESS (Week 30)

**Goal:** Revenue generation features

#### TASK-2501: Asset Marketplace (Phase 1)
**Status:** `[ ]` TODO  
**Priority:** MEDIUM  
**Estimated Time:** 8 hours  
**Agent Model:** Opus 4

**Description:**
Community marketplace for assets and templates.

**What Users Can Sell:**
- Prefab collections (buildings, props)
- Material packs
- Export templates
- Custom scripts
- Tutorials/courses

**Marketplace Features:**
- Upload/download assets
- Preview images/videos
- Ratings and reviews
- Search and categories
- Free and paid items
- Revenue share (RealTerrain 30%)

**Payment:**
- Stripe integration
- Automatic payouts
- Sales analytics
- Promotional tools

**Acceptance Criteria:**
- [ ] Secure file hosting
- [ ] Payment processing works
- [ ] Quality moderation
- [ ] User-friendly interface

---

#### TASK-2502: White-Label System (Enterprise)
**Status:** `[ ]` TODO  
**Priority:** LOW  
**Estimated Time:** 6 hours  
**Agent Model:** Opus 4

**Description:**
Allow enterprise customers to rebrand the product.

**Customization:**
- Replace logo and branding
- Custom color scheme
- Remove "RealTerrain Studio" references
- Custom splash screen
- Own domain name
- Custom about/help content

**Technical:**
- Configuration file based
- Asset replacement
- Theme system
- Build scripts for custom builds

**Pricing:**
- Enterprise tier only
- One-time setup fee + monthly
- Technical support included

**Acceptance Criteria:**
- [ ] Complete rebranding possible
- [ ] No RealTerrain references (if configured)
- [ ] Professional appearance
- [ ] Documentation for customization

---

#### TASK-2503: Analytics & Telemetry
**Status:** `[ ]` TODO  
**Priority:** MEDIUM  
**Estimated Time:** 4 hours  
**Agent Model:** Sonnet 4.5

**Description:**
Track usage for product improvement (privacy-respecting).

**Metrics:**
- Feature usage frequency
- Export sizes/resolutions
- Error rates
- Performance benchmarks
- Popular regions exported
- License tier distribution

**Privacy:**
- Opt-in only
- Anonymized data
- No personal information
- Clear privacy policy
- Can be disabled

**Use Cases:**
- Prioritize feature development
- Identify bugs/issues
- Optimize performance
- Business decisions

**Dashboard:**
- Admin panel showing metrics
- Charts and trends
- Export reports
- A/B test results

**Acceptance Criteria:**
- [ ] Privacy compliant (GDPR)
- [ ] Opt-in system
- [ ] Useful insights
- [ ] Secure data storage

---

## 🎮 SPRINT 27: GAME PROFILES & PRESETS (Week 31) ⭐ NEW

**Goal:** Complete game profile system with all presets

#### TASK-2601: Game Profile Configuration System
**Status:** `[ ]` TODO  
**Priority:** HIGH  
**Estimated Time:** 6 hours  
**Agent Model:** Opus 4

**Description:**
Create comprehensive profile system that auto-configures plugin based on game type.

**All Game Profiles (13 total):**

**1. Military Simulation / Tactical Shooter** 🎖️
```python
Features:
- Tactical analysis (AI suggestions)
- Fortification placement (HESCO, trenches, etc)
- Cover & concealment analysis
- Spawn point intelligence
- High-detail elevation (5m)
- Recent satellite imagery (1m)
- Full OSM data (roads, buildings, infrastructure)
- Navigation mesh hints

Tips:
"AI will suggest defensive positions and fortification locations"
"Cover analysis distinguishes bullet-stopping vs visual concealment"
"Spawn points balanced for competitive multiplayer"
```

**2. Open World / RPG** 🗺️
```python
Features:
- Seasonal variations (4 seasons)
- Biome transitions
- Trail network generation
- POI suggestions (scenic spots, quest locations)
- Vegetation distribution
- Procedural buildings (regional style)
- Scatter objects (rocks, logs, flowers)
- Medium detail (10m elevation)

Tips:
"Seasonal variations create 4 versions of your world"
"Trails connect interesting locations automatically"
"Biomes blend naturally with ecotone zones"
```

**3. Racing / Driving Game** 🏎️
```python
Features:
- Road network enhancement (proper width, markings)
- Racing track analysis (corners, straights)
- Track suggestions (circuit & point-to-point)
- Checkpoint placement
- Procedural road details (guard rails, signs, lights)
- Road-optimized collision mesh
- High road detail from OSM

Tips:
"Corner analysis rates difficulty of each turn"
"Track suggestions include lap time estimates"
"Guard rails auto-placed on dangerous curves"
```

**4. Survival / Crafting** ⛺
```python
Features:
- Resource distribution maps (water, food, shelter)
- Danger zone analysis (flood, avalanche risk)
- Safe zone identification
- Cave/shelter detection
- Vegetation for foraging
- Water source mapping
- Weather data integration
- Day/night survival difficulty

Tips:
"Water sources are critical - highlighted automatically"
"Danger zones marked for avalanche and flood risk"
"Shelter locations suggested based on terrain"
```

**5. Flight Simulator** ✈️
```python
Features:
- Airport data from OSM (runways, terminals)
- Navigation beacons (VOR, NDB)
- Airspace boundaries
- Landmark identification
- Flight path suggestions
- Terrain optimized for aerial view
- Lower resolution OK (30m)
- Wide area coverage

Tips:
"Airport runways include heading and elevation data"
"Landmarks auto-identified for VFR navigation"
"Optimized for high-altitude viewing"
```

**6. Battle Royale** 🎯
```python
Features:
- Safe zone suggestions (shrinking circle logic)
- Loot distribution zones
- Hot drop locations (high loot, high danger)
- Choke point identification
- Vantage points for combat
- Vehicle spawn suggestions
- Medium-detail everywhere (10m)
- Large area support (tiles)

Tips:
"Hot drops suggested at high loot density areas"
"Safe zones balanced for player distribution"
"Choke points create natural combat funnels"
```

**7. City Builder / Strategy** 🏙️
```python
Features:
- Urban planning analysis
- Buildable area detection (flat zones)
- Resource location (water, materials)
- Strategic choke points
- Road network for city layout
- Existing buildings as reference
- Population density data
- Zoning suggestions

Tips:
"Flat areas auto-detected for construction"
"Existing infrastructure shown for reference"
"Water sources and resources marked"
```

**8. Horror / Atmospheric** 👻
```python
Features:
- Fog zones (valleys, water bodies)
- Dense forest areas (visibility reduction)
- Abandoned building identification
- Isolated locations
- Sound occlusion maps (echo zones)
- Dark/shadowy area detection
- Weather: overcast, rain, fog
- Limited visibility zones

Tips:
"Fog naturally accumulates in valleys"
"Dense forests reduce visibility and create tension"
"Isolated buildings marked for atmospheric locations"
```

**9. Multiplayer Shooter (Non-tactical)** 🔫
```python
Features:
- Balanced spawn points
- Combat flow analysis (attack routes)
- Power position identification
- Cover distribution (not too much, not too little)
- Medium detail (10m)
- Simplified fortifications
- Map symmetry analysis (if applicable)
- Respawn location suggestions

Tips:
"Spawn points balanced to prevent camping"
"Power positions identified for king-of-hill modes"
"Cover distribution ensures fair combat"
```

**10. Architectural Visualization** 🏗️
```python
Features:
- High-detail elevation (1-3m)
- Recent high-res satellite (0.5-1m)
- Existing buildings (reference)
- Sun angle calculation for lighting
- Vegetation for context
- No game-specific features
- Photography reference collection
- Color palette extraction

Tips:
"Sun angles calculated for your location and date"
"Reference photos collected for texture accuracy"
"Existing context shown for integration"
```

**11. Film / Virtual Production** 🎬
```python
Features:
- Camera path generation
- Lighting rig presets (based on location/time)
- High visual quality (1-3m elevation)
- Recent satellite imagery
- Cinematic viewpoints
- Background plate optimization
- Color grading presets
- Reference photography

Tips:
"Camera paths generated for cinematic shots"
"Lighting presets match real sun angles for location"
"Viewpoints suggested for establishing shots"
```

**12. Education / Research** 🎓
```python
Features:
- Geological layer data
- Biome classification
- Climate zone information
- Historical change visualization
- Terrain statistics dashboard
- Educational annotations
- Simplified UI for students
- Teaching resources

Tips:
"Geological data shows bedrock and soil types"
"Statistics dashboard perfect for analysis"
"Historical changes show urban development"
```

**13. Custom / Advanced** 🔧
```python
Features:
- All features available
- Full manual control
- No auto-configuration
- Advanced settings exposed
- For power users
- Scripting support
- API access

Tips:
"Full control over every setting"
"Recommended only for experienced users"
"Check documentation for feature details"
```

**Profile Metadata:**
```python
class GameProfile:
    def __init__(self):
        self.id = "military_simulation"
        self.name = "Military Simulation / Tactical Shooter"
        self.icon = "🎖️"
        self.description = "Realistic terrain for tactical games like Arma, Squad"
        self.examples = ["Arma 3", "Squad", "Ground Branch", "Insurgency"]
        self.difficulty = "Medium"  # Easy, Medium, Advanced
        self.typical_area = "5-25 km²"
        self.export_time = "5-15 minutes"
        self.target_engines = ["Unreal Engine 5", "Unity"]
        
    def get_config(self):
        return {
            # All settings as shown above
        }
        
    def get_tips(self):
        return [
            "✅ Feature X enabled",
            "💡 Tip: Consider using Y for Z"
        ]
```

**UI Flow:**
```
Step 1: Welcome Screen
"Welcome to RealTerrain Studio - From Earth to Engine"
"What type of project are you creating?"

Step 2: Profile Grid
[Card: Military Sim 🎖️] [Card: Open World 🗺️] [Card: Racing 🏎️]
[Card: Survival ⛺]      [Card: Flight ✈️]      [Card: Battle Royale 🎯]
[Card: City Builder 🏙️] [Card: Horror 👻]       [Card: Shooter 🔫]
[Card: Arch Viz 🏗️]     [Card: Film 🎬]         [Card: Education 🎓]
[Card: Custom 🔧]

Step 3: Profile Preview
Shows what will be enabled
User can "Customize" or "Use as-is"

Step 4: Area Selection
Choose location and size
Profile suggests optimal size

Step 5: Export
Progress bar with profile-specific steps
```

**Storage:**
```json
// User's saved profile preference
{
  "current_profile": "military_simulation",
  "customizations": {
    "fortification_level": "heavy",
    "resolution": 3
  },
  "recent_profiles": [
    "military_simulation",
    "open_world",
    "racing"
  ],
  "favorites": ["military_simulation"]
}
```

**Acceptance Criteria:**
- [ ] All 13 profiles implemented
- [ ] Each profile has correct auto-configuration
- [ ] Icons and descriptions clear
- [ ] Tips shown based on profile
- [ ] User can customize after selection
- [ ] Profile choice persists
- [ ] Easy to switch profiles
- [ ] Export uses profile settings
- [ ] Documentation for each profile

---

#### TASK-2602: Profile Recommendation Engine
**Status:** `[ ]` TODO  
**Priority:** MEDIUM  
**Estimated Time:** 3 hours  
**Agent Model:** Opus 4

**Description:**
Suggest best profile based on user's area selection and needs.

**Smart Recommendations:**

```python
def recommend_profile(area_bbox, area_size, region_type):
    """
    Analyze selected area and suggest best profile
    """
    recommendations = []
    
    # Analyze area characteristics
    is_urban = detect_urban_density(area_bbox)
    has_roads = detect_road_network(area_bbox)
    is_mountainous = detect_elevation_variance(area_bbox)
    has_water = detect_water_bodies(area_bbox)
    
    # Military Sim: Good for varied terrain
    if is_mountainous and has_roads and not is_urban:
        recommendations.append({
            "profile": "military_simulation",
            "score": 95,
            "reason": "Varied terrain perfect for tactical gameplay"
        })
    
    # Racing: Good for road networks
    if has_roads and not is_mountainous:
        recommendations.append({
            "profile": "racing",
            "score": 90,
            "reason": "Good road network for racing tracks"
        })
    
    # City Builder: Urban areas
    if is_urban:
        recommendations.append({
            "profile": "city_builder",
            "score": 85,
            "reason": "Existing urban infrastructure as reference"
        })
    
    # Open World: Large diverse areas
    if area_size > 25 and is_mountainous and has_water:
        recommendations.append({
            "profile": "open_world",
            "score": 90,
            "reason": "Large diverse area perfect for exploration"
        })
    
    return sorted(recommendations, key=lambda x: x['score'], reverse=True)
```

**UI Display:**
```
Based on your selected area, we recommend:

🎖️ Military Simulation (95% match)
   ├─ Reason: Varied terrain perfect for tactical gameplay
   └─ [Use This Profile]

🏎️ Racing Game (90% match)
   ├─ Reason: Good road network for racing tracks
   └─ [Use This Profile]

🗺️ Open World RPG (85% match)
   ├─ Reason: Diverse biomes for exploration
   └─ [Use This Profile]

[Show All Profiles] [I'll Choose Myself]
```

**Acceptance Criteria:**
- [ ] Analyzes area characteristics
- [ ] Suggests 1-3 best profiles
- [ ] Explains reasoning
- [ ] User can accept or choose manually
- [ ] Improves over time (learning)

---

#### TASK-2604: Hardware Requirements & Engine Limits System ⭐ CRITICAL
**Status:** `[ ]` TODO  
**Priority:** HIGH  
**Estimated Time:** 5 hours  
**Agent Model:** Opus 4

**Description:**
Real-time validation system that warns users about hardware and engine limitations.

**SYSTEM OVERVIEW:**

**1. Hardware Requirements Calculator**

```python
class HardwareCalculator:
    def calculate_requirements(self, area_size_km2, resolution_m, profile):
        """
        Calculate RAM, VRAM, disk space, and processing time
        """
        # Base calculations
        heightmap_size = self.calculate_heightmap_resolution(area_size_km2, resolution_m)
        texture_size = self.calculate_texture_size(area_size_km2, resolution_m)
        osm_objects = self.estimate_osm_objects(area_size_km2, profile)
        vegetation_count = self.estimate_vegetation(area_size_km2, profile)
        
        # Memory requirements
        ram_needed = self.calculate_ram(heightmap_size, texture_size, osm_objects)
        vram_needed = self.calculate_vram(texture_size, vegetation_count)
        disk_space = self.calculate_disk_space(area_size_km2, profile)
        
        # Processing
        export_time = self.estimate_export_time(area_size_km2, resolution_m)
        import_time_ue5 = self.estimate_ue5_import_time(area_size_km2)
        
        return {
            "ram_gb": ram_needed,
            "vram_gb": vram_needed,
            "disk_gb": disk_space,
            "export_time_minutes": export_time,
            "import_time_minutes": import_time_ue5,
            "warnings": self.generate_warnings(ram_needed, vram_needed, area_size_km2)
        }
```

**Hardware Requirement Tiers:**

```python
HARDWARE_TIERS = {
    "minimum": {
        "cpu": "Intel i5-8400 / AMD Ryzen 5 2600",
        "ram": "16 GB",
        "vram": "4 GB (GTX 1650)",
        "disk": "50 GB SSD",
        "max_area": "5 km²",
        "max_resolution": "10m",
        "note": "Suitable for small areas, preview quality"
    },
    "recommended": {
        "cpu": "Intel i7-10700 / AMD Ryzen 7 3700X",
        "ram": "32 GB",
        "vram": "8 GB (RTX 3060)",
        "disk": "200 GB SSD",
        "max_area": "25 km²",
        "max_resolution": "5m",
        "note": "Good for most projects, balanced quality"
    },
    "high_end": {
        "cpu": "Intel i9-12900K / AMD Ryzen 9 5950X",
        "ram": "64 GB",
        "vram": "12 GB (RTX 3080)",
        "disk": "500 GB NVMe SSD",
        "max_area": "100 km²",
        "max_resolution": "3m",
        "note": "Professional workflows, large terrains"
    },
    "workstation": {
        "cpu": "Threadripper 3970X / Xeon W-3275",
        "ram": "128 GB+",
        "vram": "24 GB (RTX 4090 / A6000)",
        "disk": "1 TB+ NVMe SSD",
        "max_area": "500 km²",
        "max_resolution": "1m",
        "note": "Studio-grade, massive open worlds"
    }
}
```

**2. Unreal Engine 5 Limits Database**

```python
UE5_LIMITS = {
    "landscape": {
        "max_components": 32 * 32,  # 1024 total
        "max_resolution": 8192 * 8192,  # per landscape
        "max_heightmap_size": 8192,
        "recommended_max_size": 4033 * 4033,  # for performance
        "world_composition_max": "theoretically unlimited with World Partition"
    },
    
    "textures": {
        "max_texture_size": 8192,  # 8K max
        "recommended_satellite": 4096,
        "max_material_layers": 8,  # landscape layers
        "streaming_pool_size": "~3 GB default, configurable"
    },
    
    "instancing": {
        "max_instances_per_type": 2_000_000,  # 2 million (Nanite)
        "traditional_instancing": 100_000,  # without Nanite
        "max_unique_meshes": 10_000,
        "hierarchical_instancing": 1_000_000
    },
    
    "vegetation": {
        "max_foliage_instances": 10_000_000,  # with proper LODs
        "recommended_dense_forest": 500_000,  # per km²
        "max_grass_density": 400,  # per m²
        "tree_variety_recommended": 5-10  # species per biome
    },
    
    "physics": {
        "max_collision_components": 100_000,
        "simplified_collision_recommended": True,
        "physics_substeps": 1  # more = slower
    },
    
    "world_partition": {
        "cell_size_recommended": 128_000,  # cm (1.28 km)
        "loading_range": "2-4 cells",
        "max_world_size": "virtually unlimited"
    },
    
    "memory": {
        "base_engine": 2_000,  # MB
        "per_km2_landscape": 150,  # MB
        "per_100k_trees": 500,  # MB
        "per_1k_buildings": 200,  # MB
        "texture_streaming": 3_000  # MB default
    }
}
```

**3. Real-Time Validation UI**

**Main Export Dialog with Live Feedback:**

```
┌──────────────────────────────────────────────────────┐
│  RealTerrain Studio - Export Configuration          │
├──────────────────────────────────────────────────────┤
│                                                      │
│  Profile: Military Simulation 🎖️                    │
│  Area: 15 km² (3.87 x 3.87 km)                      │
│  Resolution: 5m                                      │
│                                                      │
├──────────────────────────────────────────────────────┤
│  💻 HARDWARE REQUIREMENTS                            │
├──────────────────────────────────────────────────────┤
│                                                      │
│  ✅ RAM:  8.2 GB needed                              │
│     You have: 32 GB ✓                                │
│                                                      │
│  ✅ VRAM: 4.5 GB needed                              │
│     You have: 8 GB (RTX 3060) ✓                      │
│                                                      │
│  ✅ Disk: 12 GB needed                               │
│     Available: 450 GB ✓                              │
│                                                      │
│  ⏱️ Processing Time:                                 │
│     Export: ~8 minutes                               │
│     UE5 Import: ~3 minutes                           │
│                                                      │
│  Your PC: RECOMMENDED TIER ✅                        │
│  Status: Ready to export!                            │
│                                                      │
├──────────────────────────────────────────────────────┤
│  🎮 UNREAL ENGINE 5 COMPATIBILITY                    │
├──────────────────────────────────────────────────────┤
│                                                      │
│  Landscape:                                          │
│  ✅ Size: 3870 x 3870 (within 8192 limit)            │
│  ✅ Components: 60 (max 1024)                         │
│  ✅ Heightmap: 4096x4096 ✓                           │
│                                                      │
│  Textures:                                           │
│  ✅ Satellite: 4096x4096 (recommended)               │
│  ✅ Material layers: 6 (max 8)                       │
│                                                      │
│  Vegetation (estimated):                             │
│  ⚠️ Trees: ~850,000                                  │
│     Recommended max: 500,000 per km²                 │
│     Suggestion: Enable LOD system ✓                  │
│     With Nanite: ✅ No problem                       │
│                                                      │
│  OSM Objects:                                        │
│  ✅ Buildings: ~1,200 (within limits)                │
│  ✅ Roads: 45 km (no limit with splines)             │
│  ✅ Props: ~3,400 instances                          │
│                                                      │
│  Memory in UE5 (estimated):                          │
│  Landscape: 2.2 GB                                   │
│  Textures: 1.8 GB                                    │
│  Vegetation: 4.2 GB                                  │
│  Objects: 0.9 GB                                     │
│  ─────────────────                                   │
│  Total: ~9.1 GB VRAM needed                          │
│  Your GPU: 8 GB ⚠️                                   │
│                                                      │
│  ⚠️ WARNING: Close to VRAM limit                     │
│  Suggestions:                                        │
│  • Reduce tree density to 70% (-30%)                 │
│  • Use texture compression                           │
│  • Enable aggressive LOD                             │
│                                                      │
│  [Auto-Optimize] [Manual Tweaks] [Export Anyway]    │
│                                                      │
├──────────────────────────────────────────────────────┤
│  💡 OPTIMIZATION SUGGESTIONS                         │
├──────────────────────────────────────────────────────┤
│                                                      │
│  Based on your system (32GB RAM, RTX 3060):         │
│                                                      │
│  ✅ Current settings are good                        │
│  ⚠️ Consider reducing tree density                   │
│  💡 Enable World Partition for this size             │
│  💡 Use Nanite for vegetation (UE5.1+)              │
│                                                      │
│  [Show Detailed Report]                              │
│                                                      │
└──────────────────────────────────────────────────────┘
```

**4. Warning System with Traffic Light Colors**

```python
class LimitChecker:
    def check_limits(self, config, user_hardware):
        warnings = []
        
        # Check RAM
        if config.ram_needed > user_hardware.ram * 0.9:
            warnings.append({
                "level": "critical",  # 🔴
                "type": "ram",
                "message": "Not enough RAM! Export may fail or crash.",
                "solution": "Reduce area size or resolution"
            })
        elif config.ram_needed > user_hardware.ram * 0.7:
            warnings.append({
                "level": "warning",  # 🟡
                "type": "ram",
                "message": "High RAM usage. Close other applications.",
                "solution": "Recommended: Upgrade to 64 GB for this area"
            })
        
        # Check UE5 landscape limits
        if config.heightmap_resolution > 8192:
            warnings.append({
                "level": "critical",  # 🔴
                "type": "ue5_landscape",
                "message": f"Heightmap {config.heightmap_resolution}x{config.heightmap_resolution} exceeds UE5 max (8192x8192)!",
                "solution": "Use World Partition and split into tiles",
                "auto_fix": "Split into 4 tiles of 4096x4096"
            })
        
        # Check vegetation count
        tree_density = config.tree_count / config.area_km2
        if tree_density > 1_000_000:
            warnings.append({
                "level": "critical",  # 🔴
                "type": "vegetation",
                "message": f"Too many trees! {config.tree_count:,} total",
                "solution": "Enable Nanite or reduce density",
                "impact": "Will cause severe performance issues"
            })
        elif tree_density > 500_000:
            warnings.append({
                "level": "warning",  # 🟡
                "type": "vegetation",
                "message": "High tree count. Consider LOD optimization.",
                "solution": "Nanite recommended for this density"
            })
        
        # Check VRAM
        if config.vram_needed > user_hardware.vram:
            warnings.append({
                "level": "critical",  # 🔴
                "type": "vram",
                "message": "Insufficient VRAM! UE5 may crash or freeze.",
                "solution": "Reduce texture resolution or area size",
                "alternative": "Use texture streaming (slower loading)"
            })
        
        # Check disk space
        if config.disk_needed > user_hardware.available_disk * 0.9:
            warnings.append({
                "level": "critical",  # 🔴
                "type": "disk",
                "message": "Not enough disk space!",
                "solution": f"Free up {config.disk_needed - user_hardware.available_disk:.1f} GB"
            })
        
        # Check processing time
        if config.export_time > 60:  # 1 hour
            warnings.append({
                "level": "info",  # 🔵
                "type": "time",
                "message": f"Large export will take ~{config.export_time:.0f} minutes",
                "solution": "Consider using Cloud Processing (Pro feature)"
            })
        
        return warnings
```

**5. Auto-Optimization System**

```python
class AutoOptimizer:
    def optimize_for_hardware(self, config, user_hardware):
        """
        Automatically adjust settings to fit hardware
        """
        optimized = config.copy()
        changes = []
        
        # If RAM insufficient
        if config.ram_needed > user_hardware.ram * 0.8:
            # Reduce resolution
            optimized.resolution = min(config.resolution * 1.5, 30)
            changes.append(f"Resolution: {config.resolution}m → {optimized.resolution}m")
            
            # Reduce area
            if still_too_much:
                scale = sqrt(user_hardware.ram * 0.7 / config.ram_needed)
                optimized.area_km2 = config.area_km2 * scale
                changes.append(f"Area: {config.area_km2}km² → {optimized.area_km2:.1f}km²")
        
        # If VRAM insufficient
        if config.vram_needed > user_hardware.vram * 0.9:
            # Compress textures
            optimized.texture_compression = "high"
            changes.append("Texture compression: enabled")
            
            # Reduce satellite resolution
            optimized.satellite_resolution = 2048
            changes.append("Satellite texture: 4096 → 2048")
            
            # Reduce tree density
            optimized.tree_density *= 0.7
            changes.append("Tree density: -30%")
        
        # If exceeds UE5 landscape limit
        if config.heightmap_resolution > 8192:
            # Auto-tile
            tiles_needed = ceil(config.heightmap_resolution / 4096)
            optimized.use_tiling = True
            optimized.tile_count = tiles_needed * tiles_needed
            changes.append(f"Tiling: Split into {optimized.tile_count} tiles")
        
        return optimized, changes
```

**6. Pre-Export Checklist**

```
┌──────────────────────────────────────────────────────┐
│  📋 PRE-EXPORT CHECKLIST                             │
├──────────────────────────────────────────────────────┤
│                                                      │
│  System Status:                                      │
│  ✅ Hardware sufficient                              │
│  ✅ Disk space available                             │
│  ✅ Internet connection active                       │
│  ⚠️ Close other applications (recommended)           │
│                                                      │
│  Export Validation:                                  │
│  ✅ Within UE5 landscape limits                      │
│  ⚠️ High vegetation count (auto-optimized)           │
│  ✅ Memory requirements met                          │
│                                                      │
│  Estimated Resources:                                │
│  • RAM: 8.2 / 32 GB (26%)                            │
│  • VRAM: 4.5 / 8 GB (56%)                            │
│  • Disk: 12 / 450 GB (3%)                            │
│  • Time: ~11 minutes total                           │
│                                                      │
│  Recommendations Applied:                            │
│  ✓ Tree density reduced to 70%                       │
│  ✓ Texture compression enabled                       │
│  ✓ LOD system configured                             │
│                                                      │
│  [Back to Settings] [Start Export]                   │
│                                                      │
└──────────────────────────────────────────────────────┘
```

**7. Live Progress with Resource Monitoring**

```
┌──────────────────────────────────────────────────────┐
│  ⏳ EXPORTING TERRAIN...                             │
├──────────────────────────────────────────────────────┤
│                                                      │
│  Progress: ████████████░░░░░░░░ 65%                 │
│                                                      │
│  Current Step: Processing vegetation (4/7)          │
│  Trees placed: 595,000 / 850,000                    │
│                                                      │
│  System Resources:                                   │
│  RAM:  12.4 / 32 GB  [████████░░░░░░░░] 39%         │
│  VRAM: 3.2 / 8 GB    [██████░░░░░░░░░░] 40%         │
│  CPU:  67%           [███████████░░░░░]              │
│  Disk: Writing... 8.5 GB                             │
│                                                      │
│  Time Elapsed: 5m 23s                                │
│  Time Remaining: ~3m 10s                             │
│                                                      │
│  [Pause] [Cancel]                                    │
│                                                      │
└──────────────────────────────────────────────────────┘
```

**8. Export Report**

```
┌──────────────────────────────────────────────────────┐
│  ✅ EXPORT COMPLETE!                                 │
├──────────────────────────────────────────────────────┤
│                                                      │
│  Export Summary:                                     │
│  • Area: 15 km² (3.87 x 3.87 km)                     │
│  • Resolution: 5m                                    │
│  • Total time: 8m 33s                                │
│  • Files: 47 (12.3 GB)                               │
│                                                      │
│  Generated Assets:                                   │
│  ✓ Heightmap (4096x4096)                             │
│  ✓ Satellite texture (4096x4096)                     │
│  ✓ Material masks (6 types)                          │
│  ✓ OSM objects (4,623 items)                         │
│  ✓ Vegetation data (595,243 trees)                   │
│  ✓ Tactical analysis (milsim)                        │
│                                                      │
│  UE5 Import Expectations:                            │
│  • Import time: ~3 minutes                           │
│  • VRAM usage: ~6.8 GB                               │
│  • Recommended: Enable World Partition               │
│                                                      │
│  Optimizations Applied:                              │
│  ✓ Tree density reduced (30%)                        │
│  ✓ Textures compressed                               │
│  ✓ LOD levels: 5                                     │
│                                                      │
│  [Open Export Folder] [Import to UE5 Guide]          │
│                                                      │
└──────────────────────────────────────────────────────┘
```

**UI Elements:**

```python
# Color coding
COLORS = {
    "safe": "#4CAF50",      # Green ✅
    "warning": "#FF9800",   # Orange ⚠️
    "critical": "#F44336",  # Red 🔴
    "info": "#2196F3"       # Blue 💡
}

# Icons
ICONS = {
    "ram": "🖥️",
    "vram": "🎮",
    "disk": "💾",
    "time": "⏱️",
    "cpu": "⚙️",
    "landscape": "🗺️",
    "vegetation": "🌲",
    "buildings": "🏘️"
}
```

**Acceptance Criteria:**
- [ ] Detects user's hardware (RAM, VRAM, CPU, disk)
- [ ] Calculates requirements accurately
- [ ] Warns before UE5 limits exceeded
- [ ] Shows real-time validation in UI
- [ ] Auto-optimization suggestions
- [ ] Traffic light color system (green/yellow/red)
- [ ] Detailed export report
- [ ] Live resource monitoring during export
- [ ] Pre-export checklist
- [ ] Clear error messages with solutions
- [ ] Works on Windows/Mac/Linux
- [ ] Saved hardware profile for future exports

### Sprint Overview:
```
PHASE 1 - MVP (12 weeks):
Sprint 1 (Week 1):      Setup              - 4 tasks
Sprint 2 (Week 2):      Foundation         - 3 tasks
Sprint 3 (Week 3):      Elevation          - 3 tasks
Sprint 4 (Week 4):      Satellite          - 2 tasks
Sprint 5 (Week 5):      OSM                - 2 tasks
Sprint 6 (Week 6):      Materials          - 1 task
Sprint 7 (Week 7):      UE5 Basic          - 3 tasks
Sprint 8 (Week 8):      Polish             - 4 tasks
Sprint 9 (Week 9-10):   Pro Features       - 2 tasks
Sprint 10 (Week 11-12): Website            - 2 tasks

PHASE 2 - ADVANCED FEATURES (18 weeks):
Sprint 11 (Week 13-14): Gameplay           - 5 tasks
Sprint 12 (Week 15-16): Procedural Gen     - 5 tasks
Sprint 13 (Week 17):    Environment        - 5 tasks
Sprint 14 (Week 18):    Artist Tools       - 4 tasks
Sprint 15 (Week 19):    Workflow           - 4 tasks
Sprint 16 (Week 20):    Data Analysis      - 2 tasks
Sprint 17 (Week 21):    Genre Specific     - 2 tasks
Sprint 18 (Week 22):    Cloud & Collab     - 1 task
Sprint 19 (Week 23):    Advanced Materials - 3 tasks ⭐ NEW
Sprint 20 (Week 24):    Advanced Gameplay  - 3 tasks ⭐ NEW
Sprint 21 (Week 25):    Performance        - 2 tasks ⭐ NEW
Sprint 22 (Week 26):    Extended Platforms - 3 tasks ⭐ NEW
Sprint 23 (Week 27):    Educational        - 3 tasks ⭐ NEW
Sprint 24 (Week 28):    Virtual Production - 2 tasks ⭐ NEW
Sprint 25 (Week 29):    Developer Tools    - 3 tasks ⭐ NEW
Sprint 26 (Week 30):    Monetization       - 3 tasks ⭐ NEW

Total Tasks: 76 major tasks
MVP: 12 weeks (26 tasks)
Full Version: 30 weeks (76 tasks)
```

### Priority Breakdown:
- 🔴 **HIGH Priority**: 18 tasks (MVP critical)
- 🟡 **MEDIUM Priority**: 38 tasks (Major features)
- 🟢 **LOW Priority**: 20 tasks (Nice-to-have / Future)

### Feature Categories:
```
Core Terrain Export:        10 tasks
Gameplay Features:          10 tasks  
Procedural Generation:       8 tasks
Environment & Weather:       7 tasks
Artist & Designer Tools:     9 tasks
Performance & Workflow:      8 tasks
Platform Support:            6 tasks
Business & Monetization:     6 tasks
Educational & Special:       6 tasks
Developer Tools:             6 tasks
```

### Platform Support:
- ✅ Unreal Engine 5 (full support)
- ✅ Unity (import plugin)
- ✅ Godot (basic support)
- ✅ Blender (artist workflow)
- ✅ Web (future: web viewer)

### Unique Selling Points:
1. **Military Simulation** - Tactical analysis, fortifications
2. **Procedural Generation** - Buildings, roads, vegetation
3. **Seasonal Variations** - 4 seasons automatically
4. **Multi-Platform** - Unity, Godot, Blender support
5. **Asset Marketplace** - Community ecosystem
6. **Educational Mode** - School-friendly features
7. **Virtual Production** - Film/TV workflows
8. **API Access** - Automation for studios
9. **Cloud Processing** - Massive terrain exports
10. **Real Geodata** - NASA, ESA, OSM integration

### Priority Breakdown:
- 🔴 HIGH Priority: 15 tasks (must have for MVP)
- 🟡 MEDIUM Priority: 9 tasks (nice to have)
- 🟢 LOW Priority: 2 tasks (future enhancement)

---

## 🎯 CURRENT FOCUS

**Active Sprint:** NONE (Project not started yet)  
**Active Task:** NONE  
**Blocked Tasks:** NONE  

**Waiting for:** User to say "Rock On" 🎸

---

## 📝 NOTES FOR AGENT

### Before Starting Each Task:
1. ✅ Read task description completely
2. ✅ Check if previous tasks are complete
3. ✅ Verify you have necessary info
4. ✅ Explain to user what you'll build
5. ✅ Get approval if major decision

### While Working:
1. ✅ Mark task as `[~]` IN_PROGRESS
2. ✅ Add progress notes
3. ✅ Commit code regularly
4. ✅ Update documentation

### After Completing:
1. ✅ Mark task as `[✓]` DONE
2. ✅ Update CHANGELOG.md
3. ✅ Test functionality
4. ✅ Create testing instructions for user
5. ✅ Ask user to verify before moving on

---

## 🆘 IF YOU GET STUCK

### Ask User:
- Which data source should we use? (if multiple options)
- What should the UI look like? (if not specified)
- Should we add feature X? (if unsure about scope)
- This will take longer than estimated, ok to continue?

### Check First:
- AGENT_RULES.md for guidelines
- Previous tasks for context
- Dependencies are installed
- Internet connection for APIs

---

**Remember:** User cannot code! Be their guide. 🌟

---

*Last Updated: December 2024*  
*Total Tasks: 26*  
*Completed: 0*  
*In Progress: 0*