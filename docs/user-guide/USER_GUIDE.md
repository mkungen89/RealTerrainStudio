# RealTerrain Studio - User Guide

**Version:** 1.0.0
**Last Updated:** December 13, 2024

---

## 📋 Table of Contents

1. [Welcome](#welcome)
2. [Getting Started](#getting-started)
3. [Basic Workflow](#basic-workflow)
4. [Step-by-Step Tutorials](#step-by-step-tutorials)
5. [Feature Guides](#feature-guides)
6. [Export Settings](#export-settings)
7. [Tips & Best Practices](#tips--best-practices)
8. [Troubleshooting](#troubleshooting)
9. [FAQ](#faq)

---

## 👋 Welcome

Welcome to **RealTerrain Studio**! This guide will help you create beautiful, realistic 3D terrain for Unreal Engine 5 from real-world geographic data.

### What Can You Do?

- **Export Real Terrain** - Download elevation data from anywhere in the world
- **Add Satellite Imagery** - Apply real satellite textures to your terrain
- **Include Roads & Buildings** - Automatically generate roads, buildings, and landmarks
- **Material Classification** - Terrain automatically textured with appropriate materials
- **One-Click Export** - Import directly into Unreal Engine 5

### Who Is This For?

- **Game Developers** - Create realistic game worlds based on real locations
- **Architects** - Visualize buildings in their actual geographic context
- **Urban Planners** - Model city developments
- **Film & VFX** - Recreate real locations for movies and commercials
- **Educators** - Teaching geography, geology, or environmental science

---

## 🚀 Getting Started

### Prerequisites

Before you begin, make sure you have:

- ✅ **QGIS 3.28+** installed ([Download here](https://qgis.org))
- ✅ **Internet connection** (for downloading data)
- ✅ **Unreal Engine 5.3+** installed (if importing to UE5)
- ✅ **RealTerrain Studio license key** (or use Free tier)

### Installation

See the [Installation Guide](INSTALLATION.md) for detailed setup instructions.

**Quick Start:**
1. Download the QGIS plugin zip file
2. Open QGIS
3. Go to `Plugins` → `Manage and Install Plugins`
4. Click `Install from ZIP`
5. Select the downloaded file
6. Activate RealTerrain Studio

### First Launch

1. After installation, you'll see the RealTerrain Studio icon in the QGIS toolbar
2. Click it to open the main panel
3. Enter your license key (or click "Use Free Tier")
4. You're ready to start!

---

## 🎯 Basic Workflow

The typical workflow follows these steps:

```
1. SELECT AREA
   └─> Draw bounding box on map or enter coordinates

2. CHOOSE DATA SOURCES
   └─> Enable elevation, satellite, roads, buildings, etc.

3. CONFIGURE SETTINGS
   └─> Set resolution, quality, materials

4. PREVIEW & VALIDATE
   └─> Check area size, estimated data usage

5. EXPORT
   └─> Download data and generate terrain files

6. IMPORT TO UE5
   └─> Drag & drop into Unreal Engine
```

**Estimated Time:** 5-15 minutes for a typical 10km² area

---

## 📚 Step-by-Step Tutorials

### Tutorial 1: Your First Terrain Export (Beginner)

**Goal:** Export a simple 2km × 2km terrain with elevation data.

**Time Required:** ~5 minutes

#### Step 1: Select Your Area

1. Open QGIS and activate RealTerrain Studio
2. Navigate to your desired location on the map
3. Click the **"Draw Bounding Box"** tool
4. Click and drag to create a rectangle on the map
5. The coordinates will automatically populate

**Tip:** Start small! A 2km × 2km area is perfect for learning.

#### Step 2: Configure Data Sources

1. In the RealTerrain Studio panel, find **"Data Sources"**
2. Check **☑ Elevation Data**
3. Leave other options unchecked for now
4. Select resolution: **30m** (good balance of quality and speed)

#### Step 3: Preview

1. Click **"Preview"** button
2. Review the information:
   - Area: ~4 km²
   - Resolution: 30m
   - Estimated download: ~5 MB
   - Estimated time: ~30 seconds

#### Step 4: Export

1. Click **"Export"** button
2. Choose save location (create a folder like `C:\Terrains\MyFirstTerrain\`)
3. Click **"Start Export"**
4. Watch the progress bar

**You'll see:**
```
[========>           ] 45%
Downloading elevation tiles...
Processing tile 3/8
```

5. When complete, you'll see: **"Export Complete! ✓"**

#### Step 5: Check Your Files

Navigate to your export folder. You should see:

```
MyFirstTerrain/
├── terrain_heightmap.png     # Elevation data as 16-bit PNG
├── terrain_metadata.json      # Geographic info, scale, bounds
└── terrain_preview.jpg        # Quick preview image
```

**Congratulations!** 🎉 You've created your first terrain export.

---

### Tutorial 2: Adding Satellite Imagery (Beginner)

**Goal:** Export terrain with realistic satellite texture.

**Time Required:** ~8 minutes

#### Step 1: Select Area

1. Use the same process as Tutorial 1
2. Draw your bounding box

#### Step 2: Enable Satellite Data

1. Check **☑ Elevation Data** (30m resolution)
2. Check **☑ Satellite Imagery** (NEW!)
3. Select imagery resolution: **10m** (Sentinel-2 quality)

#### Step 3: Preview

1. Click **"Preview"**
2. Note the larger download size (~25 MB for 4 km²)

#### Step 4: Export

1. Click **"Export"**
2. Choose save location
3. Wait for completion (~2-3 minutes)

#### Step 5: Review Files

You should now see:

```
MyTerrain/
├── terrain_heightmap.png      # Elevation
├── terrain_satellite.jpg      # Satellite texture!
├── terrain_metadata.json
└── terrain_preview.jpg
```

**Next Step:** Import these files into Unreal Engine! (See Tutorial 5)

---

### Tutorial 3: Complete Terrain with Roads & Buildings (Intermediate)

**Goal:** Export a realistic urban terrain with all features.

**Time Required:** ~15 minutes

#### Step 1: Select Urban Area

1. Navigate to a city location (e.g., downtown Stockholm)
2. Draw a bounding box around an interesting area
3. Recommended size: 3km × 3km

#### Step 2: Enable All Data Sources

1. **☑ Elevation Data** - Resolution: 10m (high quality)
2. **☑ Satellite Imagery** - Resolution: 10m
3. **☑ OpenStreetMap Data** - Enable all features:
   - ☑ Roads
   - ☑ Buildings
   - ☑ Waterways
   - ☑ Landuse (parks, forests, etc.)
   - ☑ Landmarks

#### Step 3: Configure Export Settings

1. **Export Format:** `.rterrain` (RealTerrain Studio format)
2. **Coordinate System:** Keep default (WGS84)
3. **Height Scale:** 1.0 (realistic scale)
4. **Material Classification:** Enable ☑

#### Step 4: Preview

Review the estimated stats:
```
Area: 9 km²
Elevation tiles: 16
Satellite tiles: 36
OSM features: ~2,500 buildings, ~150 km roads
Estimated download: ~120 MB
Estimated time: ~8 minutes
```

#### Step 5: Export

1. Click **"Export"**
2. Choose save location
3. Monitor progress:
   ```
   [=====>              ] 25%
   Downloading elevation data...
   [============>       ] 60%
   Fetching satellite imagery...
   [==================> ] 95%
   Processing buildings and roads...
   ```

#### Step 6: Review Complete Export

Your export folder should contain:

```
CompleteUrbanTerrain/
├── terrain_heightmap.png          # 16-bit elevation
├── terrain_satellite.jpg          # Satellite texture
├── terrain_roads.json             # Road splines with metadata
├── terrain_buildings.json         # Building footprints & heights
├── terrain_waterways.json         # Rivers, lakes
├── terrain_landuse.json           # Parks, forests, etc.
├── terrain_materials.json         # Material classification
├── terrain_metadata.json          # All geographic info
└── terrain_preview.jpg            # Overview
```

**Amazing!** 🚀 You now have a complete dataset ready for UE5.

---

### Tutorial 4: Material Classification & Texturing (Intermediate)

**Goal:** Understand how materials are automatically assigned.

#### Material Classification System

RealTerrain Studio analyzes your terrain and automatically assigns materials based on:

1. **Satellite Imagery Analysis**
   - Color patterns (green = vegetation, blue = water, gray = urban)
   - Texture patterns (smooth = water, rough = forest)

2. **OpenStreetMap Data**
   - Landuse tags (forest, grass, farmland)
   - Natural features (water, beach, rock)
   - Surface types (paved, unpaved, gravel)

3. **Elevation Analysis**
   - Slope (steep = rock/cliff, flat = grass/water)
   - Height (high elevation = rock/snow, low = water/vegetation)

#### Material Categories

The system classifies terrain into these materials:

| Material | When Applied | UE5 Material |
|----------|-------------|--------------|
| **Grass** | Flat areas, parks, lawns | `M_Grass_Realistic` |
| **Forest** | Dense vegetation, forests | `M_Forest_Floor` |
| **Rock** | Steep slopes (>30°), cliffs | `M_Rock_Cliff` |
| **Sand** | Beaches, deserts | `M_Sand_Beach` |
| **Water** | Rivers, lakes, ocean | `M_Water_Lake` |
| **Snow** | High elevation (>2000m) | `M_Snow_Alpine` |
| **Asphalt** | Roads, parking lots | `M_Asphalt_Road` |
| **Concrete** | Urban areas, buildings | `M_Concrete_Urban` |
| **Dirt** | Unpaved paths, farmland | `M_Dirt_Ground` |

#### How to Use Materials in UE5

1. Import the `.rterrain` file using the UE5 plugin
2. Materials are automatically applied to the landscape
3. Material blend maps are included for smooth transitions
4. Customize materials in UE5's Material Editor if needed

**Example Terrain:**

```
Ocean (Water) → Beach (Sand) → Grass → Forest → Mountain (Rock) → Peak (Snow)
```

Each transition is smoothly blended for realistic appearance.

---

### Tutorial 5: Importing to Unreal Engine 5 (Intermediate)

**Goal:** Import your exported terrain into UE5.

**Prerequisites:**
- Completed Tutorial 2 or 3
- RealTerrain Studio UE5 plugin installed

#### Step 1: Install UE5 Plugin

1. Download the UE5 plugin from your account dashboard
2. Copy to: `C:\Program Files\Epic Games\UE_5.3\Engine\Plugins\Marketplace\RealTerrainStudio\`
3. Restart Unreal Engine
4. Enable plugin: `Edit` → `Plugins` → Search "RealTerrain Studio" → ☑ Enable

#### Step 2: Import Terrain

1. In UE5, open your project
2. Go to **Tools** → **RealTerrain Studio** → **Import Terrain**
3. Click **"Browse"** and select your `.rterrain` file
4. Review import settings:
   - Scale: 100 (UE5 units = 100cm)
   - Location: (0, 0, 0) or choose custom
   - Materials: Auto-assign ☑
5. Click **"Import"**

#### Step 3: Wait for Import

You'll see:
```
Importing terrain...
[=============>      ] 65%
Creating landscape...
Applying materials...
Generating road splines...
```

**Import time:** ~2-5 minutes for a 10km² terrain

#### Step 4: Review Your Terrain

Your UE5 level now contains:

1. **Landscape** - Terrain with elevation and materials
2. **Roads** - Landscape splines following real roads
3. **Buildings** - Procedural building meshes
4. **Water** - Lakes and rivers with water material
5. **Vegetation** - Foliage placement based on landuse

#### Step 5: Customize

Now you can:
- Adjust materials (double-click to edit)
- Modify road widths
- Replace building meshes with your own
- Add lighting, atmosphere, etc.

**You're done!** 🎮 Your real-world terrain is now in UE5.

---

### Tutorial 6: Batch Export Multiple Areas (Advanced - Pro License)

**Goal:** Export multiple terrain tiles for a large game world.

**Prerequisites:**
- Pro license activated
- Understanding of basic export workflow

#### Step 1: Define Multiple Areas

1. Open RealTerrain Studio
2. Click **"Batch Mode"** (Pro only)
3. Click **"Add Area"** for each region:
   - Area 1: Downtown (Coordinates: ...)
   - Area 2: Airport (Coordinates: ...)
   - Area 3: Harbor (Coordinates: ...)
   - Area 4: Suburbs (Coordinates: ...)

#### Step 2: Configure Shared Settings

1. Set resolution: **10m** (applies to all)
2. Enable data sources (applies to all):
   - ☑ Elevation
   - ☑ Satellite
   - ☑ Roads
   - ☑ Buildings

#### Step 3: Review Batch

Batch summary shows:
```
Total areas: 4
Total area: 36 km²
Total download: ~450 MB
Estimated time: ~25 minutes
Output: 4 separate .rterrain files
```

#### Step 4: Export Batch

1. Click **"Export Batch"**
2. Choose base output folder: `C:\GameWorld\Terrains\`
3. Click **"Start"**

The system processes each area sequentially (or in parallel with Pro):
```
[=====>              ] 25%
Exporting Area 1/4: Downtown
ETA: 18 minutes
```

#### Step 5: Import to UE5

Each exported area can be imported separately into UE5:
1. Import Area 1 at location (0, 0, 0)
2. Import Area 2 at location (10000, 0, 0)
3. Import Area 3 at location (0, 10000, 0)
4. Import Area 4 at location (10000, 10000, 0)

The terrains will align perfectly to create a seamless large world!

---

## 🎨 Feature Guides

### Elevation Data

**Sources:**
- **SRTM (30m resolution)** - Global coverage, free
- **ASTER GDEM (30m)** - Alternative global source
- **ALOS World 3D (30m)** - High-quality for mountainous regions
- **LiDAR (1-5m)** - Ultra-high quality, limited coverage (Pro only)

**Choosing Resolution:**

| Resolution | Best For | File Size (10km²) | Quality |
|------------|----------|-------------------|---------|
| **90m** | Preview, large areas | ~2 MB | Low |
| **30m** | Standard game terrain | ~8 MB | Good ✓ |
| **10m** | High-detail landscapes | ~70 MB | Excellent |
| **1-5m** | Architectural visualization | ~500 MB | Ultra (Pro) |

**Tips:**
- Start with 30m for testing
- Use 10m for final production
- LiDAR only available in some regions

### Satellite Imagery

**Sources:**
- **Sentinel-2 (10m resolution)** - Free, updated every 5 days
- **Landsat 8 (15m)** - Free, global coverage
- **High-res aerial (0.5-2m)** - Limited coverage (Pro only)

**Image Quality Settings:**

| Quality | Resolution | File Size (10km²) | Use Case |
|---------|-----------|-------------------|----------|
| **Low** | 20m | ~15 MB | Quick preview |
| **Medium** | 10m | ~60 MB | Standard ✓ |
| **High** | 5m | ~240 MB | Detailed |
| **Ultra** | 0.5-2m | ~1 GB | Photorealistic (Pro) |

**Tips:**
- Enable "Cloud filtering" to get clearest images
- Use "Date range" to get seasonal imagery
- Enable "Color correction" for balanced colors

### Roads & Infrastructure

**What's Included:**
- Road centerlines (all types: highways, streets, paths)
- Lane counts and widths
- Road surface types (paved, gravel, dirt)
- Bridges and tunnels (marked)
- Sidewalks (where available)

**Road Types Supported:**

| OSM Highway Type | Generated As | Details |
|------------------|--------------|---------|
| `motorway` | 4-6 lane highway | Barriers, no sidewalks |
| `trunk` | Major road | 2-4 lanes |
| `primary` | Main street | 2 lanes, sidewalks |
| `secondary` | Street | 2 lanes, sidewalks |
| `residential` | Residential street | 1-2 lanes, sidewalks |
| `service` | Driveway/parking | 1 lane |
| `path` | Walking path | Narrow |

**In Unreal Engine:**
- Roads imported as Landscape Splines
- Width and material assigned automatically
- Can be edited with UE5's spline tools

### Buildings

**Data Includes:**
- Building footprints (2D polygon)
- Height information (where available)
- Building type (residential, commercial, industrial)
- Address information (where available)

**Building Generation:**

In UE5, buildings are procedurally generated using the footprint and height:

1. **Simple Box** - Default for generic buildings
2. **Procedural Detail** - Windows, doors, roofs (if Pro plugin enabled)
3. **Custom Meshes** - Replace with your own (e.g., hero buildings)

**Customization:**
```cpp
// In UE5, you can customize building generation:
BuildingActor->SetMeshType(EProcBuildingType::Residential);
BuildingActor->SetFloorHeight(350.0f);  // cm
BuildingActor->RegenerateMesh();
```

### Material Classification

See Tutorial 4 for details on how materials are assigned.

**Manual Override:**

You can override material assignments:
1. Open `terrain_materials.json` after export
2. Edit material assignments:
```json
{
  "material_map": {
    "0,0": "grass",      // Change to "sand"
    "0,1": "forest",     // Change to "grass"
    ...
  }
}
```
3. Re-import to UE5

---

## ⚙️ Export Settings

### Export Formats

**1. `.rterrain` (Recommended)**
- RealTerrain Studio native format
- Includes all data: elevation, textures, roads, buildings
- Best for UE5 import

**2. Separate Files**
- Heightmap: PNG (16-bit) or RAW
- Texture: JPEG, PNG, or TGA
- Vector data: JSON or Shapefile
- Best for custom workflows

**3. FBX (Geometry)**
- Exports terrain as 3D mesh
- Includes materials
- Best for other 3D software (Blender, Maya)

### Coordinate Systems

**Default: WGS84 (EPSG:4326)**
- Standard GPS coordinates
- Works worldwide

**Custom Projections:**
- UTM zones (for specific regions)
- Local coordinate systems
- Choose in "Advanced Settings"

### Height Scale

Adjust vertical exaggeration:

| Scale | Effect | Use Case |
|-------|--------|----------|
| **0.5x** | Flatten terrain | Subtle hills |
| **1.0x** | Realistic ✓ | Accurate elevation |
| **2.0x** | Exaggerate | Dramatic mountains |
| **5.0x** | Extreme | Stylized terrain |

### Quality vs. Speed

**Fast Export (Low Quality):**
- 90m elevation
- 20m satellite
- Roads only (no buildings)
- ~2 minutes for 10km²

**Balanced (Recommended):**
- 30m elevation
- 10m satellite
- Roads + Buildings
- ~8 minutes for 10km²

**High Quality:**
- 10m elevation
- 5m satellite
- All features + materials
- ~20 minutes for 10km²

**Ultra (Pro Only):**
- 1-5m LiDAR elevation
- 0.5m aerial imagery
- Detailed infrastructure
- ~45 minutes for 10km²

---

## 💡 Tips & Best Practices

### Performance Tips

1. **Start Small**
   - First export: 2km × 2km
   - Test workflow before large exports

2. **Use Appropriate Resolution**
   - Don't use 10m resolution for a 100km² area
   - Match resolution to your needs

3. **Cache Your Data**
   - RealTerrain Studio caches downloaded tiles
   - Re-exporting the same area is much faster

4. **Batch Processing** (Pro)
   - Export multiple areas overnight
   - Set up queue and let it run

### Quality Tips

1. **Check Satellite Image Date**
   - Use "Date range" to avoid cloudy images
   - Different seasons give different looks

2. **Verify Elevation Data**
   - Click "Preview" to see data quality
   - Some areas have better coverage than others

3. **Inspect OSM Data**
   - Urban areas: excellent road/building data
   - Rural areas: may have incomplete data
   - Can supplement with manual additions in UE5

4. **Material Tuning**
   - Auto-classification is ~90% accurate
   - Review and adjust in UE5 if needed

### Workflow Tips

1. **Organize Your Exports**
```
MyProject/
├── Terrains/
│   ├── Downtown/
│   │   ├── downtown_v1.rterrain
│   │   └── downtown_v2.rterrain
│   ├── Airport/
│   └── Harbor/
└── UE5_Project/
```

2. **Version Your Exports**
   - Add date or version number
   - Keep track of different settings

3. **Document Your Settings**
   - Save a text file with export settings
   - Makes it easy to recreate later

### Common Mistakes to Avoid

❌ **Don't:**
- Export huge areas (>50km²) without testing smaller areas first
- Use maximum quality for early prototyping
- Ignore license limits (Free tier: 100km²/month)

✅ **Do:**
- Test with small areas
- Use progressive quality (low → medium → high)
- Monitor your data usage

---

## 🔧 Troubleshooting

### Export Issues

**Problem:** "Download failed" error

**Solutions:**
1. Check internet connection
2. Try again (transient network errors are common)
3. Reduce area size
4. Try different data source (e.g., ASTER instead of SRTM)

---

**Problem:** "No elevation data available"

**Solutions:**
1. Check if area is over ocean (no land elevation)
2. Try alternative data source
3. Verify coordinates are correct

---

**Problem:** "Export is very slow"

**Solutions:**
1. Reduce area size
2. Lower resolution (use 30m instead of 10m)
3. Disable satellite imagery for testing
4. Check disk space (SSD is much faster)

---

**Problem:** "Out of memory"

**Solutions:**
1. Close other applications
2. Reduce export area
3. Lower resolution
4. Export elevation and satellite separately

### Import Issues (UE5)

**Problem:** "Cannot import .rterrain file"

**Solutions:**
1. Verify UE5 plugin is installed and enabled
2. Check UE5 version (requires 5.3+)
3. Verify .rterrain file is not corrupted (re-export if needed)

---

**Problem:** "Terrain appears flat"

**Solutions:**
1. Check height scale in import settings (try 2.0x)
2. Verify elevation data was included in export
3. Check terrain_heightmap.png is valid

---

**Problem:** "Materials are wrong/missing"

**Solutions:**
1. Re-import with "Auto-assign materials" enabled
2. Check that UE5 material assets are installed
3. Manually assign materials in UE5

### Data Quality Issues

**Problem:** "Buildings are missing"

**Solutions:**
1. Check that area has OSM building data (urban areas best)
2. Enable "Buildings" in data sources
3. Some rural areas may not have building data

---

**Problem:** "Roads look incorrect"

**Solutions:**
1. OSM data quality varies by region
2. Can manually edit roads in UE5 using Landscape Splines
3. Report incorrect OSM data to OpenStreetMap

---

**Problem:** "Satellite image is cloudy"

**Solutions:**
1. Use "Date range" to select different time period
2. Enable "Cloud filtering" (Pro)
3. Try different satellite source

### License Issues

**Problem:** "License key invalid"

**Solutions:**
1. Copy-paste license key carefully (no extra spaces)
2. Check license is not expired
3. Contact support: support@realterrainstudio.com

---

**Problem:** "Monthly limit exceeded"

**Solutions:**
1. Wait until next month (limit resets)
2. Upgrade to Pro license
3. Delete old exports to free up quota

---

**Problem:** "Feature not available"

**Solution:**
- Check if feature requires Pro license
- Upgrade at: https://realterrainstudio.com/pricing

For more issues, see [Troubleshooting Guide](TROUBLESHOOTING.md)

---

## ❓ FAQ

### General

**Q: Is RealTerrain Studio free?**
A: Yes! Free tier allows 100km² exports per month. Pro license removes limits and adds advanced features.

**Q: What operating systems are supported?**
A: Windows 10/11, macOS 10.15+, Linux (Ubuntu 20.04+). Requires QGIS.

**Q: Can I use exported terrains commercially?**
A: Yes! With Pro license. Free tier is for personal/educational use only.

**Q: How accurate is the elevation data?**
A: SRTM data is ±16m vertical accuracy. Higher-resolution sources (LiDAR) are ±0.5m.

### Technical

**Q: What resolution should I use?**
A: Start with 30m for testing, use 10m for production. LiDAR (1-5m) only if you need extreme detail.

**Q: How large an area can I export?**
A: Technically unlimited with Pro. Practically, 10-20km² is ideal for game levels. Larger areas should use tiling.

**Q: Does RealTerrain Studio work offline?**
A: No, it requires internet to download elevation and satellite data. However, cached data can be re-used offline.

**Q: Can I edit the terrain after export?**
A: Yes! Edit in UE5 using Landscape tools. The exported data is a starting point.

### Data Sources

**Q: Where does the data come from?**
A:
- Elevation: NASA SRTM, JAXA ALOS, USGS LiDAR
- Satellite: ESA Sentinel-2, NASA Landsat
- Roads/Buildings: OpenStreetMap
- All data is free and open-source!

**Q: Can I use my own elevation data?**
A: Yes! Pro license allows custom data import (GeoTIFF, LAS, LAZ).

**Q: How often is satellite imagery updated?**
A: Sentinel-2: Every 5 days. You can choose date range to get latest images.

**Q: Is the OSM data complete?**
A: Varies by region. Urban areas (Europe, North America) are excellent. Rural areas may be incomplete.

### Unreal Engine

**Q: What UE5 version is required?**
A: UE5.3 or newer. Plugin may work on UE5.1+, but not officially supported.

**Q: Can I use with UE4?**
A: No. UE5 only. (UE4 export possible but not officially supported)

**Q: How do I edit roads in UE5?**
A: Roads are imported as Landscape Splines. Use UE5's Landscape Spline tools to edit.

**Q: Can I replace building meshes?**
A: Yes! Buildings are actors that can be replaced with custom meshes.

### Licensing

**Q: What's included in Free tier?**
A:
- ✅ 100km² exports per month
- ✅ 30m elevation data
- ✅ 10m satellite imagery
- ✅ Roads and buildings
- ❌ No LiDAR
- ❌ No batch processing
- ❌ Personal use only

**Q: What's included in Pro license?**
A:
- ✅ Unlimited exports
- ✅ All data sources (including LiDAR)
- ✅ Batch processing
- ✅ Priority support
- ✅ Commercial use
- ✅ Advanced materials
- **$49/month or $499/year**

**Q: Can I share my license key?**
A: No, license is per-user. Each developer needs their own license.

**Q: Do you offer educational discounts?**
A: Yes! 50% off for students and educators. Email: edu@realterrainstudio.com

---

## 📞 Getting Help

### Documentation

- **User Guide** (this document)
- [Installation Guide](INSTALLATION.md)
- [Troubleshooting Guide](TROUBLESHOOTING.md)
- [API Documentation](API_DOCUMENTATION.md)
- [Developer Guide](DEVELOPER_GUIDE.md)

### Support

- **Email:** support@realterrainstudio.com
- **Discord:** https://discord.gg/realterrainstudio
- **Forum:** https://forum.realterrainstudio.com
- **Bug Reports:** https://github.com/realterrainstudio/issues

### Video Tutorials

- [Getting Started (5 min)](https://youtube.com/...)
- [Complete Workflow (15 min)](https://youtube.com/...)
- [UE5 Import Guide (10 min)](https://youtube.com/...)
- [Advanced Features (20 min)](https://youtube.com/...)

### Community

- **Discord:** Share your creations, get help from other users
- **Forum:** In-depth discussions, feature requests
- **Twitter:** [@RealTerrainStudio](https://twitter.com/realterrainstudio) - Updates and showcase

---

## 🎓 Next Steps

Now that you've learned the basics:

1. **Complete the tutorials** - Practice with different terrain types
2. **Experiment** - Try different settings and data sources
3. **Import to UE5** - See your terrain come to life
4. **Join the community** - Share your creations on Discord
5. **Read advanced guides** - Learn about material customization, optimization, etc.

**Happy terrain building!** 🏔️

---

**Last Updated:** December 13, 2024
**Version:** 1.0.0
**For:** RealTerrain Studio
**By:** RealTerrain Studio Team
