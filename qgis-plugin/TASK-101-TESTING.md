# TASK-101: QGIS Plugin Skeleton - Testing Guide

## ✅ Task Status: READY FOR TESTING

The QGIS plugin skeleton has been created with all required components.

---

## 📋 What Was Created

### Core Files:
1. **`src/realterrain/metadata.txt`** - Plugin metadata for QGIS
2. **`src/realterrain/__init__.py`** - Plugin entry point with classFactory
3. **`src/realterrain/plugin.py`** - Main RealTerrainPlugin class
4. **`src/realterrain/ICON_INSTRUCTIONS.md`** - Instructions for adding an icon

### Plugin Features Implemented:
- ✅ Plugin initialization and cleanup
- ✅ Menu entry in QGIS Plugins menu
- ✅ Toolbar button (will show placeholder until icon is added)
- ✅ Message bar notification when activated
- ✅ Logging to QGIS message log

---

## 🧪 Testing Instructions (For User)

### Step 1: Locate Your QGIS Plugins Directory

**Windows:**
```
%APPDATA%\QGIS\QGIS3\profiles\default\python\plugins\
```
Usually: `C:\Users\YourUsername\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\`

**Mac:**
```
~/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/
```

**Linux:**
```
~/.local/share/QGIS/QGIS3/profiles/default/python/plugins/
```

### Step 2: Copy Plugin to QGIS

**Option A - Manual Copy (Windows PowerShell):**
```powershell
# Create plugins directory if it doesn't exist
New-Item -ItemType Directory -Force -Path "$env:APPDATA\QGIS\QGIS3\profiles\default\python\plugins"

# Copy the plugin folder
Copy-Item -Path "qgis-plugin\src\realterrain" -Destination "$env:APPDATA\QGIS\QGIS3\profiles\default\python\plugins\realterrain" -Recurse -Force
```

**Option B - Manual Copy (Windows Command Prompt):**
```cmd
xcopy /E /I /Y "qgis-plugin\src\realterrain" "%APPDATA%\QGIS\QGIS3\profiles\default\python\plugins\realterrain"
```

**Option C - File Explorer:**
1. Navigate to `qgis-plugin/src/realterrain/`
2. Copy the entire `realterrain` folder
3. Paste it into your QGIS plugins directory

### Step 3: Enable Plugin in QGIS

1. **Open QGIS Desktop**
2. Go to: **Plugins → Manage and Install Plugins**
3. Click the **Installed** tab
4. Look for **"RealTerrain Studio"** in the list
5. **Check the box** next to it to enable
6. Click **Close**

### Step 4: Verify Plugin Loaded

**Expected Results:**

1. **Toolbar Icon:**
   - Should see a new icon in the QGIS toolbar (may be placeholder without icon.png)

2. **Menu Entry:**
   - Go to **Plugins** menu
   - Should see **"RealTerrain Studio"** submenu
   - Should have **"Export Terrain to UE5"** option

3. **Test Activation:**
   - Click the toolbar button OR
   - Go to **Plugins → RealTerrain Studio → Export Terrain to UE5**
   - Should see a yellow message bar at top: **"Plugin loaded successfully! UI coming soon..."**

4. **Check Logs:**
   - Go to **View → Panels → Log Messages**
   - Select **"RealTerrain"** tab
   - Should see:
     - "RealTerrain Studio Plugin Initialized"
     - "RealTerrain Studio GUI Initialized"
     - "RealTerrain Studio Run" (when clicked)

---

## ✅ Acceptance Criteria Verification

- [ ] **Plugin loads without errors in QGIS** - Check Log Messages panel for no errors
- [ ] **Appears in QGIS Plugins menu** - Look for "RealTerrain Studio" menu item
- [ ] **Has proper metadata** - Shows correct name, version, description in Plugin Manager
- [ ] **Shows message when activated** - Yellow info bar appears saying "Plugin loaded successfully!"

---

## 🐛 Troubleshooting

### Plugin Doesn't Appear in List

**Problem:** RealTerrain Studio not visible in Plugin Manager

**Solutions:**
1. Verify files are in correct location
2. Check folder is named exactly `realterrain` (lowercase)
3. Restart QGIS completely
4. Check QGIS Python Console for errors: **Plugins → Python Console**

### Plugin Shows Errors

**Problem:** Errors appear when enabling plugin

**Solutions:**
1. Open QGIS Python Console: **Plugins → Python Console**
2. Check for import errors or missing dependencies
3. Verify all required files exist:
   - `__init__.py`
   - `plugin.py`
   - `metadata.txt`

### Icon Not Showing

**Expected:** This is normal - icon.png doesn't exist yet

**Solutions:**
- See `src/realterrain/ICON_INSTRUCTIONS.md` for how to add an icon
- Plugin still works without an icon

### Plugin Loads but Button Does Nothing

**Problem:** Clicking button/menu shows no message

**Solutions:**
1. Check View → Panels → Log Messages → RealTerrain tab
2. Look for error messages
3. Verify PyQt5 is installed in QGIS Python environment

---

## 📸 What You Should See

### Plugin Manager:
- Name: **RealTerrain Studio**
- Version: **0.1.0**
- Description: "Export real-world terrain to Unreal Engine 5"
- Status: **Experimental** (checked)

### Message When Activated:
```
[Info Icon] RealTerrain Studio
Plugin loaded successfully! UI coming soon...
```

### Log Messages:
```
RealTerrain Studio Plugin Initialized
RealTerrain Studio GUI Initialized
RealTerrain Studio Run
```

---

## 🎯 Next Steps

Once you've verified the plugin loads successfully:

1. **TASK-102:** Create Main Dialog UI with Game Profile System
2. Add actual functionality to the plugin
3. Create the UI for area selection and export options

---

## ℹ️ Notes

- Plugin is in **experimental** mode (expected for v0.1.0)
- No UI dialog yet - just shows info message
- Icon is missing but plugin still functions
- All core QGIS plugin infrastructure is in place
- Ready for UI development in next task

---

**Need Help?** Check the main README.md in the qgis-plugin folder for more detailed installation instructions.
