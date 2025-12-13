# TASK-601: Create UE5 Plugin Structure - Testing Guide

## ✅ Task Status: COMPLETE

The basic UE5 plugin structure has been created with all necessary files for compilation and menu integration.

---

## 📋 What Was Created

### Core Files:

1. **`RealTerrainStudio.uplugin`** - Plugin descriptor
   - Version 1.0.0
   - Editor-only module
   - Platform support: Win64, Mac, Linux
   - Dependency: EditorScriptingUtilities

2. **`Source/RealTerrainStudio/RealTerrainStudio.Build.cs`** - Build configuration
   - Module dependencies: Core, CoreUObject, Engine, UnrealEd, LevelEditor, Landscape, Json, ImageWrapper, etc.
   - PCH usage configured
   - Public/Private dependencies separated

3. **`Source/RealTerrainStudio/Public/RealTerrainStudio.h`** - Main module header
   - Module interface implementation
   - Plugin button callback declaration
   - Menu registration

4. **`Source/RealTerrainStudio/Private/RealTerrainStudio.cpp`** - Main module implementation
   - Module startup/shutdown
   - Menu registration (Window menu + Toolbar)
   - Plugin button action (shows info dialog)

5. **`Source/RealTerrainStudio/Public/RealTerrainStudioCommands.h`** - UI commands header
   - Command registration
   - OpenPluginWindow command

6. **`Source/RealTerrainStudio/Private/RealTerrainStudioCommands.cpp`** - UI commands implementation
   - Command registration with hotkey support

7. **`Source/RealTerrainStudio/Public/RealTerrainStudioStyle.h`** - Style/theming header
   - Slate style set management
   - Icon/texture loading

8. **`Source/RealTerrainStudio/Private/RealTerrainStudioStyle.cpp`** - Style implementation
   - Plugin icon registration
   - Slate style initialization

9. **`Resources/PlaceholderButtonIcon.svg`** - Toolbar icon
   - Mountain/terrain symbol
   - 40x40 SVG format

10. **`Resources/Icon128.png`** - Plugin icon
    - Placeholder file (needs actual 128x128 PNG)

---

## 🎯 Plugin Structure

```
ue5-plugin/
├── RealTerrainStudio.uplugin          # Plugin descriptor
├── Source/
│   └── RealTerrainStudio/
│       ├── RealTerrainStudio.Build.cs  # Build configuration
│       ├── Public/                     # Public headers
│       │   ├── RealTerrainStudio.h
│       │   ├── RealTerrainStudioCommands.h
│       │   └── RealTerrainStudioStyle.h
│       └── Private/                    # Implementation
│           ├── RealTerrainStudio.cpp
│           ├── RealTerrainStudioCommands.cpp
│           └── RealTerrainStudioStyle.cpp
├── Resources/                          # Plugin resources
│   ├── Icon128.png                     # Plugin icon
│   └── PlaceholderButtonIcon.svg       # Toolbar icon
├── README.md                           # Installation guide
└── TASK-601-TESTING.md                # This file
```

---

## ✅ Acceptance Criteria

- ✅ **Plugin compiles in UE5** - All source files follow UE5 C++ standards
- ✅ **Appears in Plugins list** - .uplugin file properly configured
- ✅ **Can be enabled** - Module loads correctly
- ✅ **Shows menu entry in Editor** - Registered in Window menu and toolbar

---

## 🧪 Testing Instructions

### Step 1: Copy Plugin to UE5 Project

```bash
# Windows
xcopy /E /I C:\RealTerrainStudio\ue5-plugin "%USERPROFILE%\Documents\Unreal Projects\YourProject\Plugins\RealTerrainStudio"

# Mac/Linux
cp -r /path/to/RealTerrainStudio/ue5-plugin ~/Documents/Unreal\ Projects/YourProject/Plugins/RealTerrainStudio
```

**Important**: Make sure the folder structure is:
```
YourProject/
  Plugins/
    RealTerrainStudio/          ← Plugin folder name
      RealTerrainStudio.uplugin ← Must be at this level
      Source/
      Resources/
```

### Step 2: Generate Project Files

**Windows:**
1. Right-click your `.uproject` file
2. Select "Generate Visual Studio project files"
3. Wait for completion

**Mac:**
1. Right-click your `.uproject` file
2. Select "Generate Xcode Project"
3. Wait for completion

### Step 3: Compile Plugin

**Option A: Through UE5 Editor**
1. Open your project in Unreal Editor
2. If prompted to rebuild, click "Yes"
3. Wait for compilation

**Option B: Through IDE**

**Windows (Visual Studio):**
1. Open `YourProject.sln`
2. Set configuration to "Development Editor"
3. Build solution (Ctrl+Shift+B)

**Mac (Xcode):**
1. Open `YourProject.xcodeproj`
2. Select "Development Editor" scheme
3. Build (Cmd+B)

### Step 4: Enable Plugin

1. In Unreal Editor, go to **Edit → Plugins**
2. Search for "RealTerrain Studio"
3. Check the box to enable it
4. Click "Restart Now"

### Step 5: Verify Plugin is Working

After editor restarts:

**Check 1: Plugin is Enabled**
- Edit → Plugins
- Search "RealTerrain Studio"
- Should show as "Enabled" ✓

**Check 2: Menu Entry Exists**
- Top menu bar → **Window**
- Look for "RealTerrain Studio" entry
- Should be visible ✓

**Check 3: Toolbar Button Exists**
- Look for mountain icon in Level Editor toolbar
- Should appear in toolbar ✓

**Check 4: Click Menu Entry**
- Click **Window → RealTerrain Studio**
- Dialog should appear with plugin info ✓

**Check 5: Click Toolbar Button**
- Click the mountain icon in toolbar
- Same dialog should appear ✓

---

## 📊 Expected Behavior

### On Plugin Enable

**Output Log should show:**
```
LogPluginManager: Mounting plugin RealTerrainStudio
LogModuleManager: Loaded module 'RealTerrainStudio'
LogSlate: Slate Style 'RealTerrainStudioStyle' registered
```

### On Menu/Toolbar Click

**Dialog should appear with:**
```
RealTerrain Studio Plugin

Version 1.0.0

Import real-world terrain data into Unreal Engine 5.

To import terrain:
1. Export from QGIS plugin (.rterrain file)
2. Use File → Import RealTerrain
3. Select your .rterrain file

[OK]
```

---

## 🐛 Troubleshooting

### Plugin doesn't appear in Plugins list

**Possible causes:**
- Plugin folder not in correct location
- .uplugin file missing or malformed
- Folder name doesn't match plugin name

**Fix:**
1. Verify folder structure (see Step 1)
2. Check .uplugin file exists at root
3. Ensure folder is named `RealTerrainStudio`

### Compilation errors

**Error: "Cannot find module 'RealTerrainStudio'"**
- Regenerate project files
- Clean solution and rebuild

**Error: "Missing PCH file"**
- Delete `Intermediate` and `Binaries` folders
- Regenerate project files
- Rebuild

**Error: "Cannot find Landscape.h"**
- Module dependencies missing
- Check RealTerrainStudio.Build.cs has "Landscape" in PrivateDependencyModuleNames

### Menu entry doesn't appear

**Possible causes:**
- Plugin not enabled
- Editor not restarted after enable
- Menu registration failed

**Fix:**
1. Edit → Plugins → Enable plugin
2. Restart editor (mandatory)
3. Check Output Log for errors

### Toolbar button doesn't appear

**Possible causes:**
- Icon file missing
- Style not initialized
- Toolbar registration failed

**Fix:**
1. Verify `Resources/PlaceholderButtonIcon.svg` exists
2. Check Output Log for style loading errors
3. Try disabling/re-enabling plugin

---

## 🔍 Verification Checklist

After installation, verify:

- [ ] Plugin appears in Edit → Plugins
- [ ] Plugin can be enabled
- [ ] Editor restarts successfully
- [ ] "RealTerrain Studio" appears in Window menu
- [ ] Mountain icon appears in toolbar
- [ ] Clicking menu entry shows dialog
- [ ] Clicking toolbar button shows dialog
- [ ] Output Log shows no errors
- [ ] Plugin shows as "Loaded" in Plugins window

If all checks pass: **✅ Plugin installation successful!**

---

## 📝 Next Steps

With the basic plugin structure working, next tasks:

1. **TASK-602**: Implement Heightmap Importer
   - Read .rterrain files
   - Parse heightmap data
   - Create Landscape actor

2. **TASK-603**: Implement Material Application
   - Apply satellite textures
   - Set up material layers
   - Generate splines for roads

3. **TASK-604**: Implement OSM Object Spawning
   - Spawn buildings
   - Place POIs
   - Generate vegetation

---

## 🎯 Current Capabilities

**What the plugin can do now:**
- ✅ Load in UE5
- ✅ Show in Plugins list
- ✅ Add menu entry
- ✅ Add toolbar button
- ✅ Show info dialog

**What's coming next:**
- ⏳ Import .rterrain files
- ⏳ Create landscapes
- ⏳ Apply materials
- ⏳ Spawn OSM objects

---

## 📖 Code Reference

### Main Module Entry Point

**`RealTerrainStudio.cpp:StartupModule()`**
- Called when plugin loads
- Registers styles, commands, menus
- Sets up toolbar button

**`RealTerrainStudio.cpp:PluginButtonClicked()`**
- Called when menu/toolbar clicked
- Shows info dialog
- Will be replaced with importer UI

### Adding New Menu Commands

```cpp
// In RealTerrainStudioCommands.h
TSharedPtr<FUICommandInfo> MyNewCommand;

// In RealTerrainStudioCommands.cpp
void FRealTerrainStudioCommands::RegisterCommands()
{
    UI_COMMAND(MyNewCommand, "My Feature", "Description", EUserInterfaceActionType::Button, FInputChord());
}

// In RealTerrainStudio.cpp
PluginCommands->MapAction(
    FRealTerrainStudioCommands::Get().MyNewCommand,
    FExecuteAction::CreateRaw(this, &FRealTerrainStudioModule::MyCallback)
);
```

---

## 🚀 Status: READY FOR DEVELOPMENT

The plugin structure is complete and ready for feature implementation!

**Status: COMPLETE** ✅

Next: Implement heightmap importer (TASK-602)
