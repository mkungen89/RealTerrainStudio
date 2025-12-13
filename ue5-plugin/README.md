# 🎮 Unreal Engine 5 Plugin - RealTerrain Studio

This is the UE5 plugin component of RealTerrain Studio. It imports terrain packages created by the QGIS plugin and generates landscapes in Unreal Engine.

---

## 📁 Folder Structure

```
ue5-plugin/
└── RealTerrain/                 ← Plugin root
    ├── Source/
    │   └── RealTerrain/
    │       ├── Public/          ← Public header files
    │       │   ├── RealTerrain.h
    │       │   ├── TerrainImporter.h
    │       │   ├── LandscapeGenerator.h
    │       │   ├── MaterialApplicator.h
    │       │   └── OSMImporter.h
    │       │
    │       ├── Private/         ← Private implementation files
    │       │   ├── RealTerrain.cpp
    │       │   ├── TerrainImporter.cpp
    │       │   ├── LandscapeGenerator.cpp
    │       │   ├── MaterialApplicator.cpp
    │       │   └── OSMImporter.cpp
    │       │
    │       └── RealTerrain.Build.cs  ← Build configuration
    │
    ├── Content/                 ← Unreal assets
    │   ├── Materials/          ← Terrain materials
    │   ├── Textures/           ← Texture assets
    │   ├── Blueprints/         ← Blueprint utilities
    │   └── UI/                 ← Editor UI widgets
    │
    ├── Resources/               ← Plugin resources
    │   └── Icon128.png         ← Plugin icon
    │
    ├── RealTerrain.uplugin     ← Plugin descriptor
    └── README.md               ← This file
```

---

## 🚀 Installation

### Prerequisites
- Unreal Engine 5.3 or higher
- Visual Studio 2022 (Windows) or Xcode (Mac)
- C++ development tools
- Git (for version control)

### Step 1: Install Plugin
```bash
# Windows
# Copy plugin to UE5 plugins folder:
xcopy /E /I ue5-plugin\RealTerrain "%USERPROFILE%\Documents\Unreal Engine\Projects\YourProject\Plugins\RealTerrain"

# Mac
cp -r ue5-plugin/RealTerrain ~/Documents/Unreal\ Projects/YourProject/Plugins/RealTerrain

# Alternative: Engine-wide installation
# Windows: Copy to C:\Program Files\Epic Games\UE_5.3\Engine\Plugins\Marketplace\
# Mac: Copy to /Users/Shared/Epic Games/UE_5.3/Engine/Plugins/Marketplace/
```

### Step 2: Enable Plugin in UE5
1. Open your UE5 project
2. Go to: **Edit** → **Plugins**
3. Search for "RealTerrain Studio"
4. Check the box to enable it
5. Restart Unreal Engine

### Step 3: Compile Plugin (if needed)
If the plugin needs recompilation:
1. Right-click your `.uproject` file
2. Select "Generate Visual Studio project files" (Windows) or "Generate Xcode project" (Mac)
3. Open the solution/project
4. Build in Development Editor configuration

---

## 🎯 Features

### Terrain Import
- ✅ Import `.rterrain` packages
- ✅ Auto-generate Landscape actor
- ✅ World Composition support
- ✅ LOD optimization
- ✅ Streaming support for large terrains

### Material System
- 🎨 Auto-apply satellite textures
- 🗺️ Normal map generation
- 🌄 PBR material setup
- 📊 Weight-blended layers
- 🔧 Customizable material templates

### OSM Integration
- 🛣️ Road splines with proper width
- 🏗️ Building placement
- 💧 Water bodies
- 🌳 Vegetation zones
- 🏞️ Landcover types

### Editor Tools
- 🖱️ Import wizard UI
- 📐 Scale and position tools
- 🔍 Preview before import
- ⚙️ Batch processing
- 📊 Statistics display

---

## 🧪 Usage

### Basic Import Workflow

1. **In QGIS**: Export terrain as `.rterrain` package
2. **In UE5**: Open your project
3. **Import**:
   - Click **RealTerrain** toolbar button
   - Or go to: **Tools** → **RealTerrain Studio** → **Import Terrain**
4. **Select File**: Browse to your `.rterrain` file
5. **Configure**:
   - Set landscape scale
   - Choose material template
   - Enable/disable OSM features
6. **Import**: Click "Import"
7. **Wait**: Plugin processes data and generates landscape
8. **Done**: Terrain appears in your level!

### Advanced Options

**Landscape Settings:**
- Resolution: Quads per section (7, 15, 31, 63, 127, 255)
- Sections per component: 1x1 or 2x2
- Component count: Grid size (e.g., 8x8)
- Scale: X, Y, Z scaling factors

**Material Options:**
- Base material: Choose template
- Texture resolution: 1K, 2K, 4K, 8K
- Normal map strength: 0.0 - 2.0
- Roughness multiplier: 0.0 - 2.0

**OSM Options:**
- Import roads: Yes/No
- Road spline type: Landscape Spline or Blueprint Spline
- Import buildings: Yes/No
- Building LODs: 0-3
- Import vegetation: Yes/No

---

## 🔧 Development

### Building from Source

```bash
# Generate project files
cd YourUE5Project
%UE5_ROOT%\Engine\Build\BatchFiles\GenerateProjectFiles.bat

# Build (Windows)
msbuild YourProject.sln /p:Configuration="Development Editor" /p:Platform=Win64

# Build (Mac)
xcodebuild -project YourProject.xcodeproj -scheme YourProject -configuration "Development Editor"
```

### Code Style
- Follow Epic's [Coding Standard](https://docs.unrealengine.com/5.3/en-US/epic-cplusplus-coding-standard-for-unreal-engine/)
- Use Unreal's naming conventions:
  - Classes: `UMyClass` (UObject), `AMyActor` (Actor), `FMyStruct` (struct)
  - Interfaces: `IMyInterface`
  - Enums: `EMyEnum`
  - Booleans: `bIsEnabled`

### Adding New Features

1. Add header to `Source/RealTerrain/Public/`
2. Add implementation to `Source/RealTerrain/Private/`
3. Update `RealTerrain.Build.cs` if new dependencies needed
4. Test in editor
5. Document in this README

Example:
```cpp
// Public/MyFeature.h
#pragma once

#include "CoreMinimal.h"
#include "MyFeature.generated.h"

UCLASS()
class REALTERRAIN_API UMyFeature : public UObject
{
    GENERATED_BODY()

public:
    // Your code here
};
```

---

## 🐛 Troubleshooting

### Plugin doesn't load
- Check UE5 version (need 5.3+)
- Verify plugin is in Plugins folder
- Check Output Log for errors
- Try rebuilding plugin

### Import fails
- Verify `.rterrain` file is valid
- Check file isn't corrupted
- Ensure enough disk space
- Check Output Log for specific error

### Landscape looks wrong
- Check Z-scale (may need adjustment)
- Verify heightmap resolution
- Check material is applied correctly
- Try reimporting

### Performance issues
- Enable World Composition for large terrains
- Reduce texture resolution
- Enable LOD streaming
- Optimize OSM feature count

---

## 📖 API Reference

### Main Classes

**`URealTerrainImporter`**
- Main importer class
- Handles `.rterrain` package parsing
- Coordinates landscape generation

**`ALandscapeGenerator`**
- Generates Landscape actor
- Applies heightmap data
- Sets up World Composition

**`UMaterialApplicator`**
- Creates material instances
- Applies textures to landscape
- Sets up weight maps

**`UOSMImporter`**
- Imports OpenStreetMap features
- Generates road splines
- Places buildings

---

## 📝 Blueprint Support

The plugin exposes functions to Blueprint:

```cpp
// Import terrain from Blueprint
UFUNCTION(BlueprintCallable, Category = "RealTerrain")
void ImportTerrainFromFile(const FString& FilePath);

// Get import progress
UFUNCTION(BlueprintPure, Category = "RealTerrain")
float GetImportProgress() const;
```

---

## 🆘 Support

- Check troubleshooting section above
- Read UE5 Output Log for errors
- Check main project documentation
- Email: support@realterrainstudio.com

---

## 📄 License

Copyright © 2024-2025 RealTerrain Studio
All rights reserved.

---

**Built with C++ + Unreal Engine 5**
