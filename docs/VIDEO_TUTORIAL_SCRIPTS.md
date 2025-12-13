# RealTerrain Studio - Video Tutorial Scripts

**Version:** 1.0.0
**Last Updated:** December 13, 2024

---

## 📋 Table of Contents

1. [Video 1: Getting Started (5 min)](#video-1-getting-started-5-min)
2. [Video 2: Complete Workflow (15 min)](#video-2-complete-workflow-15-min)
3. [Video 3: UE5 Import Guide (10 min)](#video-3-ue5-import-guide-10-min)
4. [Video 4: Advanced Features (20 min)](#video-4-advanced-features-20-min)
5. [Video 5: Troubleshooting (8 min)](#video-5-troubleshooting-8-min)
6. [Production Notes](#production-notes)

---

## 🎬 Video 1: Getting Started (5 min)

**Target Audience:** Complete beginners
**Goal:** First successful terrain export
**Prerequisites:** QGIS installed

### Script

**[0:00-0:15] INTRO**

*[Show title card: "RealTerrain Studio - Getting Started"]*

> "Hi! Welcome to RealTerrain Studio. In this 5-minute tutorial, you'll export your first real-world terrain. Let's get started!"

*[Show QGIS with RealTerrain Studio installed]*

---

**[0:15-1:00] INSTALLATION OVERVIEW**

*[Screen: QGIS Plugin Manager]*

> "First, let's make sure RealTerrain Studio is installed. In QGIS, go to Plugins, then Manage and Install Plugins."

*[Navigate to Plugins > Manage and Install Plugins]*

> "Search for 'RealTerrain Studio', and click Install Plugin."

*[Show plugin installing]*

> "Great! Now you'll see the RealTerrain Studio icon here in the toolbar."

*[Point to mountain icon in toolbar]*

> "Click it to open the panel."

*[Click icon, panel opens on right side]*

---

**[1:00-1:30] LICENSE ACTIVATION**

*[Screen: License section of panel]*

> "For this tutorial, we'll use the Free tier. Click 'Use Free Tier'."

*[Click button]*

> "The Free tier gives you 100 square kilometers of exports per month - perfect for learning and small projects!"

*[Show license status: "Free Tier Active"]*

---

**[1:30-2:30] SELECTING AREA**

*[Screen: QGIS map showing San Francisco]*

> "Now, let's select an area to export. I'm going to navigate to San Francisco."

*[Navigate map to San Francisco Bay Area]*

> "To define your export area, click the 'Draw Bounding Box' button."

*[Click Draw Bounding Box button, cursor changes to crosshair]*

> "Now, click and drag on the map to create a rectangle."

*[Draw small box around downtown San Francisco, ~2km x 2km]*

> "Start small for your first export - this is about 4 square kilometers. Perfect!"

*[Show coordinates automatically filled in panel]*

---

**[2:30-3:30] CONFIGURE EXPORT**

*[Screen: Data Sources section]*

> "For this quick export, we'll just grab elevation data. Check the 'Elevation Data' box."

*[Check Elevation Data]*

> "Select resolution: 30 meters. This gives good quality and downloads quickly."

*[Select 30m from dropdown]*

> "Let's preview what we're about to export. Click 'Preview'."

*[Click Preview button]*

*[Show preview dialog]:*
```
Area: 4.2 km²
Elevation tiles: 2
Estimated download: ~5 MB
Estimated time: ~30 seconds
```

> "Perfect! Only 5 megabytes and about 30 seconds. Let's do it!"

---

**[3:30-4:30] EXPORT**

*[Click Export button]*

> "Choose where to save your files. I'll create a folder called 'MyFirstTerrain'."

*[Create folder, select it, click Export]*

> "And... export is running!"

*[Show progress bar]:*
```
[========>           ] 45%
Downloading elevation tiles...
Processing tile 2/2
```

> "This will just take a moment..."

*[Progress completes]*

```
Export Complete! ✓
```

> "Excellent! Let's see what we got."

---

**[4:30-5:00] REVIEW FILES & OUTRO**

*[Open export folder in File Explorer]*

```
MyFirstTerrain/
├── terrain_heightmap.png
├── terrain_metadata.json
└── terrain_preview.jpg
```

> "Here are your files! The heightmap contains all the elevation data, and metadata has the geographic information."

*[Open terrain_preview.jpg showing terrain visualization]*

> "Looking good! You've successfully exported your first real-world terrain."

*[Show title card with next steps]*

> "In the next video, we'll add satellite imagery and import this into Unreal Engine 5. Thanks for watching!"

**[END]**

---

### Production Notes

**Screen Setup:**
- QGIS on main screen (1920x1080)
- Clean desktop, no distractions
- Cursor highlighting enabled

**Voice:**
- Upbeat, friendly tone
- Speak slowly and clearly
- Pause after each action

**Graphics:**
- Title cards: 3 seconds
- Highlight mouse clicks with circles
- Zoom in on important UI elements

**Music:**
- Soft background music (royalty-free)
- Lower volume during narration

---

## 🎬 Video 2: Complete Workflow (15 min)

**Target Audience:** Users who completed Video 1
**Goal:** Export complete terrain with satellite, roads, buildings
**Prerequisites:** Video 1 watched, RealTerrain Studio installed

### Script

**[0:00-0:30] INTRO**

*[Title card: "RealTerrain Studio - Complete Workflow"]*

> "Welcome back! In this tutorial, we'll create a complete, production-ready terrain with elevation, satellite imagery, roads, and buildings. Let's dive in!"

---

**[0:30-2:00] SELECTING URBAN AREA**

*[QGIS showing map of Stockholm]*

> "Today we're exporting part of Stockholm, Sweden. It's a great example because it has interesting terrain, water, and urban features."

*[Navigate to Stockholm downtown area]*

> "I'm going to select an area about 3 kilometers by 3 kilometers. Click Draw Bounding Box."

*[Draw box around Gamla Stan and surrounding areas]*

> "This area includes the old town, water, bridges, and modern buildings - perfect for showcasing all the features."

*[Coordinates shown: (18.05, 59.32, 18.08, 59.34)]*

---

**[2:00-5:00] CONFIGURING DATA SOURCES**

*[Screen: Data Sources section]*

> "Now let's configure what data to include. First, elevation."

*[Check Elevation Data]*

> "I'll use 10-meter resolution for high quality. This is great for detailed landscapes."

*[Select 10m resolution]*

> "Next, satellite imagery. This will give us realistic textures."

*[Check Satellite Imagery]*

> "Also 10 meters. Let's click Advanced to see more options."

*[Click Advanced button]*

*[Show advanced options]:*
```
Date Range:
  Start: 2024-06-01
  End: 2024-08-31
Max Cloud Cover: 10%
```

> "I'm setting a date range for summer imagery - fewer clouds, better lighting. And max cloud cover of 10% to get the clearest images."

*[Configure settings, click OK]*

> "Now for the really cool part - OpenStreetMap data!"

*[Check OpenStreetMap Data]*

*[Enable features]:*
- ☑ Roads
- ☑ Buildings
- ☑ Waterways
- ☑ Landuse

> "This gives us all the roads, building footprints, rivers, and parks. These will be imported as splines and geometry in Unreal Engine."

---

**[5:00-7:00] MATERIAL CLASSIFICATION**

*[Screen: Advanced Settings]*

> "One more cool feature: material classification. Enable this."

*[Check Material Classification]*

> "This analyzes your terrain and automatically assigns materials - grass, rock, water, asphalt - based on satellite imagery and OSM data."

*[Show material classification options]:*
```
Method: Satellite Analysis + OSM Tags
Materials:
  ☑ Grass
  ☑ Forest
  ☑ Rock
  ☑ Water
  ☑ Asphalt
  ☑ Sand
```

> "Perfect! Now let's preview before we export."

---

**[7:00-8:30] PREVIEW & VERIFICATION**

*[Click Preview button]*

*[Show preview dialog]:*
```
Area: 9.0 km²
Data Sources:
  - Elevation: 10m (16 tiles)
  - Satellite: 10m (36 tiles)
  - OSM: ~2,500 features

Estimated Download: ~120 MB
Estimated Time: ~8 minutes
Output Files: 8 files
```

> "Okay, so we're downloading about 120 megabytes, and it'll take around 8 minutes. That includes elevation, satellite images, and all the OSM data."

*[Show breakdown]:*
```
Files that will be created:
- terrain_heightmap.png (16-bit elevation)
- terrain_satellite.jpg (RGB texture)
- terrain_roads.json (road splines)
- terrain_buildings.json (building footprints)
- terrain_waterways.json (rivers, lakes)
- terrain_landuse.json (parks, forests)
- terrain_materials.json (material assignment)
- terrain_metadata.json (all geographic info)
```

> "Eight files total. Everything we need for a complete terrain. Let's export!"

---

**[8:30-11:00] EXPORT PROCESS**

*[Click Export button]*

> "I'll save this to 'Stockholm_Complete'."

*[Create folder, click Export]*

*[Show progress dialog with detailed steps]:*

```
[=====>              ] 25%
Step 1/4: Downloading elevation data
Fetching tiles: 8/16
ETA: 6 minutes
```

> "The export happens in stages. First, elevation data..."

*[Progress continues]*

```
[===========>        ] 55%
Step 2/4: Fetching satellite imagery
Downloading tile 18/36
ETA: 3 minutes
```

> "Then satellite imagery - this takes a bit longer because the files are larger..."

*[Progress continues]*

```
[================>   ] 80%
Step 3/4: Fetching OSM features
Downloaded: 2,487 buildings, 156 roads
ETA: 1 minute
```

> "Now OpenStreetMap data - roads, buildings..."

*[Progress continues]*

```
[==================> ] 95%
Step 4/4: Processing & Exporting
Generating material maps...
Writing files...
```

> "And finally, processing everything and writing the files."

*[Progress completes]*

```
Export Complete! ✓

Exported 9.0 km²
Downloaded: 118.3 MB
Time: 7m 42s
Files: 8
```

> "Done! 7 minutes and 42 seconds. Not bad for a complete, production-ready terrain!"

---

**[11:00-13:00] REVIEWING EXPORT FILES**

*[Open export folder]*

```
Stockholm_Complete/
├── terrain_heightmap.png (8.2 MB - 2048x2048 16-bit)
├── terrain_satellite.jpg (42.5 MB - 3072x3072 RGB)
├── terrain_roads.json (1.2 MB - 156 road features)
├── terrain_buildings.json (3.8 MB - 2,487 buildings)
├── terrain_waterways.json (0.5 MB - rivers, lakes)
├── terrain_landuse.json (0.8 MB - parks, forests)
├── terrain_materials.json (2.1 MB - material classification)
└── terrain_metadata.json (0.02 MB - metadata)
```

> "Let's look at what we got. First, the heightmap - 2048 by 2048 pixels of 16-bit elevation data."

*[Open terrain_heightmap.png in image viewer]*

> "You can see the terrain elevation encoded in the grayscale values. Darker is lower, lighter is higher."

*[Open terrain_satellite.jpg]*

> "Here's the satellite imagery - you can see the buildings, streets, water. This will be our base texture."

*[Open terrain_preview.jpg]*

> "And here's a preview image showing what the terrain will look like."

*[Open terrain_roads.json in text editor]*

```json
{
  "roads": [
    {
      "id": 123456,
      "type": "primary",
      "name": "Götgatan",
      "geometry": [
        [18.0650, 59.3150],
        [18.0655, 59.3155],
        ...
      ],
      "tags": {
        "highway": "primary",
        "lanes": "2",
        "surface": "asphalt"
      }
    },
    ...
  ]
}
```

> "The road data is in JSON format with all the details - road type, name, geometry, number of lanes, surface type. Perfect for Unreal Engine splines!"

---

**[13:00-14:30] NEXT STEPS**

*[Screen: RealTerrain Studio panel]*

> "So what do you do with all this data? In the next video, we'll import this into Unreal Engine 5 and you'll see it come to life as a playable level!"

*[Show teaser clip of UE5 with terrain imported]*

> "You'll get the landscape with real elevation, satellite textures, roads as splines, and buildings placed automatically."

*[Show UE5 terrain with character walking around Stockholm]*

> "Pretty cool, right?"

---

**[14:30-15:00] OUTRO**

*[Title card with summary]*

```
What You Learned:
✓ Configure all data sources
✓ Use material classification
✓ Export production-ready terrain
✓ Understand output files

Next Video:
→ Importing to Unreal Engine 5
```

> "Thanks for watching! See you in the next video where we import this terrain into Unreal Engine 5!"

**[END]**

---

### Production Notes

**B-Roll Needed:**
- Stockholm satellite imagery
- UE5 terrain preview
- Character exploring terrain in UE5

**Callouts:**
- Highlight progress percentages
- Zoom in on JSON file structure
- Side-by-side comparisons of heightmap/satellite

---

## 🎬 Video 3: UE5 Import Guide (10 min)

**Target Audience:** Users who completed Video 2
**Goal:** Successfully import terrain into UE5
**Prerequisites:** Exported terrain from Video 2, UE5 installed

### Script

**[0:00-0:30] INTRO**

*[Title card: "RealTerrain Studio - UE5 Import"]*

> "Welcome back! You've exported your terrain - now let's bring it into Unreal Engine 5 and see it come to life!"

*[Show UE5 with blank level]*

---

**[0:30-2:00] PLUGIN INSTALLATION**

*[UE5 Edit menu]*

> "First, we need the RealTerrain Studio plugin for UE5. Go to Edit, then Plugins."

*[Navigate to Edit > Plugins]*

> "Search for 'RealTerrain Studio'."

*[Search box, type "RealTerrain Studio"]*

*[If not installed yet]:*

> "If you don't see it, you'll need to install it manually. Download the plugin from realterrainstudio.com, then extract it to your Engine's Plugins folder."

*[Show folder structure]:*
```
C:\Program Files\Epic Games\UE_5.3\Engine\Plugins\Marketplace\RealTerrainStudio\
```

> "Then restart Unreal Engine, come back to Plugins, and enable it."

*[Check the checkbox, click "Restart Now"]*

*[UE5 restarts]*

---

**[2:00-4:00] IMPORTING TERRAIN**

*[UE5 reopened, blank level]*

> "Great! Now we can import our terrain. Go to Tools, RealTerrain Studio, Import Terrain."

*[Navigate Tools > RealTerrain Studio > Import Terrain]*

*[Import dialog opens]*

> "Click Browse and find your .rterrain file. I exported Stockholm in the last video."

*[Browse to Stockholm_Complete folder]*

*[Select Stockholm.rterrain, click Open]*

*[Show import settings]:*
```
Import Settings:
  Scale: 100 (UE units = 100cm)
  Location: (0, 0, 0)
  Materials:
    ☑ Auto-assign materials
  Roads:
    ☑ Import as landscape splines
  Buildings:
    ☑ Import as procedural meshes
```

> "Let's review the settings. Scale of 100 means 1 Unreal unit equals 1 meter - realistic scale."

> "Location at origin (0, 0, 0). You can change this if you want the terrain elsewhere."

> "Auto-assign materials will apply the materials to your landscape automatically - grass, rock, water, etc."

> "Import roads as landscape splines - perfect for UE5's landscape spline system."

> "And import buildings as procedural meshes."

> "Looks good! Let's import."

*[Click Import button]*

---

**[4:00-7:00] IMPORT PROCESS**

*[Progress bar appears]*

```
Importing Terrain...
[=========>          ] 45%
Creating landscape (2048x2048)...
```

> "The import process has several steps. First, it creates the landscape from the heightmap."

*[Show landscape appearing in viewport, flat at first]*

```
[=============>      ] 65%
Applying elevation data...
```

> "Now applying the elevation data - watch the terrain rise!"

*[Heightmap applied, terrain gets 3D shape]*

```
[================>   ] 80%
Applying materials...
```

> "Materials are being applied based on the material classification we did."

*[Texture appears on terrain - grass, roads, water]*

```
[==================> ] 95%
Generating road splines...
Placing buildings...
```

> "Roads are being created as splines, and buildings as procedural meshes."

*[Roads appear as splines, building boxes appear]*

```
Import Complete! ✓

Landscape: 3x3 km
Roads: 156 splines
Buildings: 2,487 meshes
Import time: 4m 23s
```

> "And... done! 4 minutes and 23 seconds. Let's explore!"

---

**[7:00-9:00] EXPLORING THE TERRAIN**

*[Fly camera around terrain in UE5]*

> "Incredible! This is real Stockholm, with accurate elevation."

*[Show close-ups]:*
- Water (Gamla Stan waterways)
- Roads (splines following real roads)
- Buildings (procedural meshes with correct footprints)
- Terrain textures (grass, asphalt, water)

> "You can see the roads following the real street layout."

*[Select a road spline]*

> "These are landscape splines - you can edit them with UE5's spline tools."

*[Show spline editing mode]*

> "Add points, adjust widths, change materials - full control!"

*[Select a building]*

> "Buildings are procedural meshes. You can replace them with your own custom meshes."

*[Right-click building, show Replace Mesh option]*

> "Or keep the procedural buildings and just adjust their materials and details."

---

**[9:00-10:00] NEXT STEPS & OUTRO**

*[Camera still exploring terrain]*

> "From here, you can:"

*[Show bullet points]:*
```
✓ Add lighting & atmosphere
✓ Place vegetation with foliage tool
✓ Add game logic (player spawn, etc.)
✓ Customize materials
✓ Build your game!
```

*[Show quick example: Adding light source, atmosphere, vegetation]*

> "In the next video, we'll cover advanced features like batch exporting multiple areas, material customization, and performance optimization."

*[Title card]*

> "Thanks for watching! You now know how to bring real-world terrain into Unreal Engine 5!"

**[END]**

---

### Production Notes

**UE5 Settings:**
- High quality preview mode
- Good lighting for screenshots
- Smooth camera movements

**Callouts:**
- Highlight splines when selected
- Show building count in outliner
- Material indicators on terrain

---

## 🎬 Video 4: Advanced Features (20 min)

**Target Audience:** Users comfortable with basic workflow
**Goal:** Master advanced features
**Prerequisites:** Videos 1-3 completed

### Script

**[0:00-0:30] INTRO**

*[Title card: "RealTerrain Studio - Advanced Features"]*

> "Ready to take your terrain creation to the next level? In this video, we'll cover batch processing, custom materials, performance optimization, and Pro features!"

---

**[0:30-4:00] BATCH PROCESSING (PRO)**

*[QGIS with RealTerrain Studio, Pro license active]*

> "Let's say you're creating a large game world. You need multiple terrain tiles. With Pro, you can batch process them!"

*[Click "Batch Mode" button]*

*[Batch mode interface appears]:*
```
Batch Export
Areas:
  [ Empty ]

[+ Add Area] [Import Areas] [Export All]
```

> "Click Add Area for each region you want to export."

*[Click Add Area 4 times, enter coordinates for each]:*
```
Area 1: Downtown (-122.42, 37.77, -122.40, 37.79)
Area 2: Airport (-122.40, 37.61, -122.38, 37.63)
Area 3: Harbor (-122.38, 37.80, -122.36, 37.82)
Area 4: Suburbs (-122.36, 37.75, -122.34, 37.77)
```

> "I've defined 4 areas: downtown, airport, harbor, and suburbs."

*[Show areas highlighted on map]*

> "Now configure shared settings that apply to all areas."

*[Configure]:*
```
Shared Settings:
  Elevation: 10m
  Satellite: 10m
  OSM: Roads + Buildings
  Materials: Enabled
```

> "All areas will use these settings. Click Preview Batch."

*[Show batch summary]:*
```
Batch Summary:
  Total Areas: 4
  Total Area: 36 km²
  Total Download: ~450 MB
  Estimated Time: ~25 minutes
  Output: 4 separate .rterrain files
```

> "36 square kilometers total, about 25 minutes. Let's start!"

*[Click Export Batch]*

*[Show progress with multiple progress bars, one per area]*

> "Each area processes sequentially or in parallel depending on your settings."

*[Fast forward through export, show completion]*

> "Done! Now I have 4 perfectly aligned terrain tiles ready for UE5!"

---

**[4:00-8:00] CUSTOM MATERIAL CLASSIFICATION**

*[Back to single export mode]*

> "The automatic material classification is great, but what if you want custom materials?"

*[Select area, enable Material Classification]*

*[Click "Advanced" button]*

*[Show advanced material settings]:*
```
Material Rules:
  Default Rules:
    Slope > 30° → Rock
    Elevation < 5m + Water tag → Water
    OSM 'grass' → Grass
    OSM 'forest' → Forest

  [+ Add Custom Rule]
```

> "Here are the default rules. Let's add a custom rule. Click Add Custom Rule."

*[Add custom rule dialog]:*
```
Custom Rule:
  Name: Urban Areas
  Condition: OSM tag 'landuse'='commercial' OR 'landuse'='industrial'
  Material: Concrete
  Priority: High
```

> "This rule will assign concrete material to commercial and industrial areas from OSM."

*[Click OK, add another rule]:*
```
Custom Rule:
  Name: Beach Areas
  Condition: Satellite RGB average > 200 AND Elevation < 10m
  Material: Sand
  Priority: Medium
```

> "This uses satellite imagery analysis - bright areas near sea level become sand. Perfect for beaches!"

*[Save rules]*

> "These custom rules are saved and can be reused for other exports."

---

**[8:00-12:00] ADVANCED EXPORT OPTIONS**

*[Export settings, Advanced tab]*

> "Let's look at advanced export options."

*[Show options]:*
```
Advanced Export Options:

Heightmap:
  Format: PNG 16-bit | RAW | GeoTIFF
  Bit Depth: 16-bit | 32-bit
  Endianness: Little | Big

Satellite:
  Format: JPEG | PNG | TGA
  Quality: 0-100 (JPEG)
  Color Space: sRGB | Linear

Processing:
  Fill NoData: ☑ Interpolate
  Smooth Elevation: 0-10 (default: 0)
  Resample Method: Bilinear | Cubic | Lanczos

Output:
  Coordinate System: WGS84 | UTM | Custom
  Power of Two: ☑ Force (for UE5)
  Tile Size: 1024 | 2048 | 4096 | 8192
```

> "Lots of options! Let's go through the important ones."

> "Heightmap format: PNG 16-bit is good for most use cases. GeoTIFF if you need to use the data in GIS software."

> "Fill NoData: This fills gaps in elevation data using interpolation. Usually want this enabled."

> "Power of Two: Essential for UE5! Forces dimensions to powers of 2."

> "Tile Size: Larger tiles = more detail but bigger files. 2048 or 4096 is usually good."

*[Configure for high quality]:*
```
Selected Settings:
  Heightmap: PNG 16-bit
  Satellite: JPEG Quality 95
  Fill NoData: ✓
  Power of Two: ✓
  Tile Size: 4096
```

---

**[12:00-16:00] PERFORMANCE OPTIMIZATION**

*[Screen: Performance tab]*

> "Large terrains can be slow to process and import. Here are optimization strategies."

**Strategy 1: Progressive Detail**

> "Use multiple resolutions - high res near player, lower res at distance."

*[Show example]:*
```
Center Area (Player): 10m resolution
Surrounding Areas: 30m resolution
Distant Areas: 90m resolution
```

**Strategy 2: Streaming**

> "In UE5, use World Partition for level streaming."

*[Show UE5 World Partition setup]*

> "Tiles load and unload based on player position. Essential for large worlds!"

**Strategy 3: Tiling**

> "Export your world as multiple tiles rather than one huge tile."

*[Show tile grid example]:*
```
Game World (30km x 30km):
  Split into: 3x3 grid = 9 tiles
  Each tile: 10km x 10km
```

> "Much easier to manage and better performance."

**Strategy 4: LODs**

> "Use landscape LODs in UE5."

*[Show LOD settings in UE5]:*
```
LOD 0 (Close): Full detail
LOD 1: 50% detail
LOD 2: 25% detail
LOD 3: 10% detail
```

> "Distant terrain renders at lower detail - huge performance boost!"

---

**[16:00-18:00] PRO FEATURES OVERVIEW**

*[Screen: Pro features comparison]*

```
FREE vs PRO:

Resolution:
  Free: Up to 30m
  Pro: Up to 1m (LiDAR)

Export Limit:
  Free: 100 km²/month
  Pro: Unlimited

Batch Processing:
  Free: ✗
  Pro: ✓

Custom Materials:
  Free: Basic
  Pro: Advanced

Satellite Sources:
  Free: Sentinel-2 only
  Pro: Sentinel-2, Landsat, High-res aerial

Support:
  Free: Community (1-3 days)
  Pro: Priority (12-24 hours)
```

> "Pro license unlocks LiDAR data for ultra-high detail, batch processing for large worlds, and priority support."

*[Show example of LiDAR terrain vs SRTM]:*

> "Look at the difference! LiDAR captures every detail - individual buildings, roads, even cars!"

---

**[18:00-19:30] TIPS & TRICKS**

> "Before we wrap up, here are some quick tips:"

**Tip 1: Test Small First**

> "Always test with a small area before exporting a huge region. Verify settings work!"

**Tip 2: Cache is Your Friend**

> "RealTerrain Studio caches downloads. Re-exporting same area is much faster!"

**Tip 3: Check OSM Data**

> "Visit openstreetmap.org to preview data quality before exporting."

**Tip 4: Seasonal Imagery**

> "Use date range for satellite imagery to get different seasons!"

*[Show winter vs summer imagery examples]*

**Tip 5: Material Previews**

> "Enable material preview in QGIS before exporting to verify classifications."

---

**[19:30-20:00] OUTRO**

*[Title card with summary]*

```
What You Learned:
✓ Batch processing (Pro)
✓ Custom material rules
✓ Advanced export options
✓ Performance optimization
✓ Pro features overview
```

> "You're now a RealTerrain Studio expert! Go create amazing worlds!"

> "Next video: Troubleshooting common issues. Thanks for watching!"

**[END]**

---

## 🎬 Video 5: Troubleshooting (8 min)

**Target Audience:** Users encountering problems
**Goal:** Solve common issues independently
**Prerequisites:** Basic familiarity with RealTerrain Studio

### Script

**[0:00-0:30] INTRO**

*[Title card: "RealTerrain Studio - Troubleshooting"]*

> "Running into issues? Don't worry! In this video, we'll solve the most common problems. Let's get your terrain exporting smoothly!"

---

**[0:30-2:00] PROBLEM 1: "PLUGIN WON'T LOAD"**

*[Screen: QGIS with error in log]*

```
Error: Failed to load RealTerrain Studio plugin
ModuleNotFoundError: No module named 'numpy'
```

> "First issue: Plugin won't load, error says 'No module named numpy'."

**Solution:**

*[Open QGIS Python Console]*

> "Open the Python Console in QGIS. We need to install missing packages."

*[Type in console]:*
```python
import subprocess, sys
subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'numpy', 'requests', 'Pillow'])
```

*[Press Enter, packages install]*

> "This installs the required packages. Now restart QGIS."

*[Restart QGIS, plugin loads successfully]*

> "Fixed! The plugin loads now."

---

**[2:00-3:30] PROBLEM 2: "DOWNLOAD FAILS"**

*[Screen: Export dialog with error]*

```
Error: Network timeout downloading elevation tile
Failed after 3 retries
```

> "Export fails with network timeout. This usually means slow connection or server issues."

**Solutions:**

*[Show solutions list]*

**Solution A: Check Internet**

> "First, verify your internet is working. Open a browser, visit google.com."

**Solution B: Try Again**

> "Servers can be temporarily busy. Wait 5 minutes and retry."

**Solution C: Different Data Source**

> "If SRTM fails, try ASTER."

*[Change elevation source from SRTM to ASTER]*

**Solution D: Smaller Area**

> "If large area, try smaller first. Then export in chunks."

*[Reduce bbox size, retry]*

> "Success! Smaller area downloaded fine."

---

**[3:30-4:30] PROBLEM 3: "TERRAIN LOOKS FLAT IN UE5"**

*[Screen: UE5 with flat-looking terrain]*

> "You imported the terrain but it looks flat - no mountains!"

**Solution: Adjust Z Scale**

*[Select landscape in UE5]*

*[Details panel, find Z Scale parameter]*

> "In the landscape details, find Z Scale. It's probably set to 1."

*[Change Z Scale to 2.0]*

> "Increase it to 2 or even 5 for dramatic terrain."

*[Terrain updates, mountains appear]*

> "Much better! Now you can see the elevation!"

---

**[4:30-5:30] PROBLEM 4: "MISSING SATELLITE TEXTURE"**

*[Export folder, terrain_satellite.jpg missing]*

> "Export completed but satellite texture is missing."

**Solution: Verify Settings**

*[Back to QGIS RealTerrain Studio panel]*

> "Check that 'Satellite Imagery' was enabled before export."

*[Show checkbox unchecked]*

> "Ah! It wasn't checked. Enable it."

*[Check Satellite Imagery, export again]*

*[This time terrain_satellite.jpg created]*

> "Fixed! Make sure all desired data sources are checked before exporting."

---

**[5:30-6:30] PROBLEM 5: "LICENSE KEY INVALID"**

*[License activation dialog with error]*

```
Error: Invalid license key
Please check and try again
```

> "License key not accepted."

**Solutions:**

**Solution A: Copy-Paste Carefully**

> "Copy the key from your email and paste - don't type manually."

*[Show copying from email, pasting into dialog]*

**Solution B: Check for Spaces**

> "Make sure there are no extra spaces before or after."

*[Show trimming spaces]*

**Solution C: Verify Key Format**

> "License keys look like: RTSP-XXXX-XXXX-XXXX-XXXX"

**Solution D: Contact Support**

> "If still not working, email support with your purchase receipt."

---

**[6:30-7:30] DIAGNOSTIC TOOL**

*[QGIS Python Console]*

> "If you're not sure what's wrong, run this diagnostic script."

*[Type in console]:*
```python
from realterrain_studio.utils import diagnostics
diagnostics.run_full_check()
```

*[Output shows]:*
```
=== RealTerrain Studio Diagnostics ===
OS: Windows 11 ✓
Python: 3.9.5 ✓
QGIS: 3.34.1 ✓
numpy: 1.24.0 ✓
GDAL: 3.6.2 ✓
Pillow: 9.5.0 ✓
requests: 2.28.0 ✓
Internet: Connected ✓
License: Free Tier Active ✓

All systems operational!
```

> "This checks everything - Python packages, QGIS version, internet connection, license status."

> "If you see a red X, that's your problem!"

---

**[7:30-8:00] OUTRO & RESOURCES**

*[Title card with resources]*

```
Need More Help?

Documentation:
  docs.realterrainstudio.com

Troubleshooting Guide:
  Full guide with 50+ solutions

Community:
  Discord: discord.gg/realterrainstudio
  Forum: forum.realterrainstudio.com

Support:
  support@realterrainstudio.com
```

> "Still stuck? Check the full troubleshooting guide with 50+ solutions, or join our Discord community!"

> "Thanks for watching, and happy terrain building!"

**[END]**

---

## 📝 Production Notes

### General Video Production

**Equipment:**
- Screen recording: OBS Studio or Camtasia
- Resolution: 1920x1080 (1080p)
- Frame rate: 30 or 60 FPS
- Audio: USB condenser microphone

**Software:**
- QGIS 3.34+
- Unreal Engine 5.3+
- OBS Studio (recording)
- DaVinci Resolve (editing)
- Audacity (audio editing)

**Editing:**
- Add smooth transitions between scenes
- Zoom in on important UI elements
- Highlight mouse clicks
- Add text callouts for key points
- Background music at -20dB

**Graphics:**
- Title cards: 3 seconds
- Lower thirds for narrator info
- Bullet point overlays
- Progress indicators

**Export Settings:**
- Format: MP4 (H.264)
- Resolution: 1920x1080
- Bitrate: 8-10 Mbps
- Audio: AAC, 192 kbps

### Accessibility

**Subtitles:**
- Add accurate subtitles to all videos
- Use YouTube's auto-generate then manually correct
- Include speaker labels for clarity

**Closed Captions:**
- Include closed captions file (.srt)
- Upload to YouTube

**Descriptive Audio (Optional):**
- Describe visual elements for visually impaired
- "On screen: The export progress bar shows 45%"

### YouTube Metadata

**Title Format:**
```
RealTerrain Studio Tutorial: [Topic] | [Duration]
```

**Description Template:**
```
Learn how to [main goal] with RealTerrain Studio!

⏱️ Timestamps:
0:00 - Introduction
0:30 - [Section 1]
2:00 - [Section 2]
...

📚 Resources:
- Documentation: https://docs.realterrainstudio.com
- Download: https://realterrainstudio.com/download
- Discord: https://discord.gg/realterrainstudio

#RealTerrainStudio #UnrealEngine #QGIS #GameDev #TerrainGeneration
```

**Tags:**
```
RealTerrain Studio, Unreal Engine 5, UE5, QGIS, terrain generation,
game development, real world terrain, satellite imagery, elevation data,
3D terrain, landscape, gamedev, indie game, environment art
```

**Thumbnail:**
- 1280x720 resolution
- Eye-catching title text
- Screenshot of terrain
- Bright colors, high contrast

---

**Last Updated:** December 13, 2024
**Version:** 1.0.0
**For:** RealTerrain Studio
**By:** RealTerrain Studio Team
