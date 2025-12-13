# TASK-102: Main Dialog UI with Game Profile System - Testing Guide

## ✅ Task Status: READY FOR TESTING

The main dialog UI with the intelligent Game Profile wizard has been implemented.

---

## 📋 What Was Created

### Core Files:

1. **`src/realterrain/game_profiles.py`** - Game profile configuration system
   - 13 predefined profiles (9 game + 4 non-game)
   - Complete configuration for each profile type
   - Auto-configuration of all settings based on profile

2. **`src/realterrain/ui/__init__.py`** - UI module initialization

3. **`src/realterrain/ui/profile_wizard.py`** - Profile selection wizard
   - Beautiful card-based interface
   - Two categories: Game Profiles and Non-Game Profiles
   - Each profile shows icon, name, description, and examples

4. **`src/realterrain/ui/main_dialog.py`** - Main export dialog
   - Tabbed interface with 4 sections
   - Profile-aware configuration
   - Auto-applies settings based on selected profile
   - Tips panel shows profile-specific guidance

5. **Updated `src/realterrain/plugin.py`** - Integration
   - Launches main dialog instead of simple message
   - Handles export configuration

---

## 🎮 Available Profiles

### Game Profiles:
1. **🎖️ Military Simulation / Tactical Shooter** - Arma, Squad, Ground Branch
2. **🗺️ Open World / RPG** - Skyrim, Witcher, GTA, RDR2
3. **🏎️ Racing / Driving Game** - Forza Horizon, Gran Turismo
4. **⛺ Survival / Crafting** - Rust, DayZ, The Forest
5. **✈️ Flight Simulator** - MSFS, X-Plane, DCS
6. **🎯 Battle Royale** - PUBG, Fortnite, Apex Legends
7. **🏙️ City Builder / Strategy** - Cities Skylines, Anno
8. **👻 Horror / Atmospheric** - Silent Hill, Resident Evil
9. **🔫 Multiplayer Shooter** - Battlefield, Call of Duty

### Non-Game Profiles:
10. **🏗️ Architectural Visualization** - Real estate, urban planning
11. **🎬 Film / Virtual Production** - Background plates, LED walls
12. **🎓 Education / Research** - Geography, geology, teaching
13. **🔧 Custom / Advanced** - Full manual control

---

## 🧪 Testing Instructions

### Step 1: Copy Updated Plugin to QGIS

Since you've already installed the plugin from TASK-101, you need to update it:

**Windows PowerShell:**
```powershell
# Copy updated plugin files
Copy-Item -Path "qgis-plugin\src\realterrain\*" -Destination "$env:APPDATA\QGIS\QGIS3\profiles\default\python\plugins\realterrain\" -Recurse -Force
```

**Or manually:**
1. Navigate to `qgis-plugin/src/realterrain/`
2. Copy all files and folders
3. Paste into your QGIS plugins directory (overwrite existing files)

### Step 2: Reload Plugin in QGIS

**Option A - Restart QGIS (Recommended):**
1. Close QGIS completely
2. Reopen QGIS
3. Plugin will load with new changes

**Option B - Use Plugin Reloader (if installed):**
1. Install "Plugin Reloader" from QGIS Plugin Manager
2. Use it to reload RealTerrain Studio

### Step 3: Launch the Plugin

1. Click the **RealTerrain Studio** toolbar button, OR
2. Go to **Plugins → RealTerrain Studio → Export Terrain to UE5**

### Step 4: Test Profile Wizard

**Should see:**
- Dialog titled "RealTerrain Studio - Select Your Project Type"
- Question: "What type of project are you creating?"
- Two sections:
  - 🎮 GAME PROFILES (9 cards)
  - 🎨 NON-GAME PROFILES (4 cards)

**Test interactions:**
1. **Hover over cards** - Should highlight
2. **Click a profile card** - Should turn blue with blue border
3. **Click different cards** - Selection should change
4. **Try clicking Next without selection** - Button should be disabled
5. **Select a profile and click Next** - Should open main dialog

### Step 5: Test Main Dialog

**Should see:**
- Main dialog titled "RealTerrain Studio - Export Terrain"
- Header showing selected profile (icon, name, description)
- "Change Profile" button in header
- 4 tabs:
  - 📍 Area Selection
  - 🗺️ Data Sources
  - ⚙️ Features
  - 📦 Export

**Test Profile Application:**
1. Note the settings in each tab
2. Click "Change Profile" button
3. Select a different profile
4. Verify settings change to match new profile

**Test Area Selection Tab:**
1. Should see coordinate inputs (Min/Max Lon/Lat)
2. Default coordinates should be visible
3. "Draw Rectangle on Map" button (shows "coming soon" message)

**Test Data Sources Tab:**
1. Elevation section:
   - Enable/disable checkbox
   - Resolution spinner
   - Source dropdown
2. Satellite imagery section:
   - Enable/disable checkbox
   - Resolution spinner
   - "Prefer recent imagery" checkbox
3. OpenStreetMap section:
   - Enable/disable checkbox
   - Feature checkboxes (roads, buildings, water, forests)

**Test Features Tab:**
1. Material generation checkbox
2. Special features (varies by profile):
   - Tactical analysis
   - Fortifications
   - Cover analysis
   - Vegetation distribution
   - Procedural buildings
3. Tips panel shows profile-specific tips

**Test Export Tab:**
1. Output folder selector with Browse button
2. Project name input
3. Engine dropdown (Unreal Engine 5)

**Test Profile Switching:**
1. Select "Military Simulation" profile
   - Should enable: Tactical, Fortifications, Cover analysis
   - Resolution should be 5m for elevation
2. Switch to "Open World / RPG"
   - Should enable: Vegetation, Procedural buildings
   - Should show different tips
3. Switch to "Racing"
   - Different features enabled
   - Tips mention roads and tracks

### Step 6: Test Export Button

1. Configure settings (any profile)
2. Click **"Export Terrain"** button at bottom
3. Should see info message:
   - "Export configured! Profile: [profile_name]"
   - "Export functionality coming in next tasks"

---

## ✅ Acceptance Criteria Verification

- [ ] **Profile wizard shows on first run** - Opens automatically when dialog launches
- [ ] **13 profiles available** - All profiles visible in wizard
- [ ] **Clear descriptions** - Each card shows name, description, examples
- [ ] **Auto-configuration works** - Settings change when profile selected
- [ ] **User can customize** - All settings manually adjustable
- [ ] **Tips shown based on profile** - Tips panel updates with profile
- [ ] **"Change Profile" accessible** - Button in header works
- [ ] **Dialog opens when plugin clicked** - Replaces "coming soon" message
- [ ] **All UI elements present** - All tabs, inputs, buttons visible
- [ ] **Buttons respond correctly** - Browse, Change Profile, Export all work
- [ ] **Dialog closes properly** - Close button and X button work

---

## 🎨 UI Features to Test

### Profile Wizard:
- ✅ Responsive card layout (3 columns)
- ✅ Hover effects on cards
- ✅ Selection highlighting (blue border)
- ✅ Scrollable content area
- ✅ Next button enables/disables
- ✅ Cancel button works

### Main Dialog:
- ✅ Header updates with profile info
- ✅ Tabbed navigation works
- ✅ All input widgets functional
- ✅ Browse button opens folder dialog
- ✅ Tips panel shows HTML formatted tips
- ✅ Export button styled (blue background)
- ✅ Settings respect profile defaults

---

## 🐛 Known Limitations (By Design)

1. **"Draw Rectangle on Map"** - Shows "coming soon" message
   - Actual map interaction will be implemented in future tasks
   - For now, users enter coordinates manually

2. **Export Button** - Shows informational message only
   - Actual data fetching/export logic comes in TASK-201+
   - Configuration is collected and logged correctly

3. **Icon in plugin list** - Still shows placeholder
   - This is from TASK-101 and is expected

---

## 🔍 What to Look For

### Good Signs:
✅ Wizard opens with all 13 profiles
✅ Clicking profiles updates selection visually
✅ Main dialog shows profile name and icon
✅ Settings auto-fill based on profile
✅ Tips panel updates with each profile
✅ All tabs are accessible
✅ Form inputs work (spinners, checkboxes, text fields)
✅ Browse button opens folder picker
✅ Export button shows success message

### Potential Issues:

**If wizard doesn't appear:**
- Check Python Console for import errors
- Verify all files copied correctly
- Check game_profiles.py has no syntax errors

**If dialog is blank/broken:**
- Check Log Messages panel for PyQt errors
- Verify PyQt5 is available in QGIS
- Try restarting QGIS

**If settings don't change with profile:**
- Check _apply_profile() method is being called
- Look for errors in Log Messages

**If export button does nothing:**
- Check _on_export_clicked() is connected
- Look for signals in Log Messages

---

## 📸 Expected Appearance

### Profile Wizard:
```
┌─────────────────────────────────────────────────────────┐
│    What type of project are you creating?              │
│    Choose a profile to automatically configure...       │
│                                                          │
│  🎮 GAME PROFILES                                        │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐         │
│  │ 🎖️ Military│ │ 🗺️ Open    │ │ 🏎️ Racing  │         │
│  │ Simulation │ │ World / RPG│ │ / Driving  │         │
│  │            │ │            │ │            │         │
│  │ Arma, Squad│ │ Skyrim, GTA│ │ Forza, GT  │         │
│  └────────────┘ └────────────┘ └────────────┘         │
│                                                          │
│  🎨 NON-GAME PROFILES                                    │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐         │
│  │ 🏗️ Arch Viz│ │ 🎬 Film /  │ │ 🎓 Education│        │
│  │            │ │ Virtual Prod│ │ / Research │         │
│  └────────────┘ └────────────┘ └────────────┘         │
│                                                          │
│                          [Cancel] [Next]                │
└─────────────────────────────────────────────────────────┘
```

### Main Dialog:
```
┌──────────────────────────────────────────────────────┐
│  🎖️ Military Simulation / Tactical Shooter           │
│  Realistic terrain for tactical games                │
│                               [Change Profile]        │
├──────────────────────────────────────────────────────┤
│  [📍 Area Selection] [🗺️ Data Sources] [⚙️ Features] │
│  [📦 Export]                                          │
│ ┌────────────────────────────────────────────────┐  │
│ │                                                 │  │
│ │  Tab content here (forms, inputs, checkboxes)  │  │
│ │                                                 │  │
│ └────────────────────────────────────────────────┘  │
│                                                       │
│                          [Close] [Export Terrain]    │
└──────────────────────────────────────────────────────┘
```

---

## 🎯 Next Steps

Once UI is verified working:

1. **TASK-103:** Implement License Validation UI
2. **TASK-201:** Implement SRTM Data Fetcher
3. Connect export button to actual data fetching logic

---

## 📝 Notes

- All 13 game profiles are fully configured
- Each profile has unique settings optimized for its use case
- Users can select a profile then customize any setting
- Profile choice guides the export process
- UI is fully functional for configuration
- Ready for data fetching implementation in next tasks

---

## ℹ️ Developer Notes

### Architecture:
- **game_profiles.py**: Defines GameProfile dataclass and PROFILES dict
- **profile_wizard.py**: ProfileCard widget + ProfileWizard dialog
- **main_dialog.py**: MainDialog with tabs + profile integration
- **plugin.py**: Launches dialog, handles export_requested signal

### Profile System:
- Profile selected → Auto-configures all settings
- User can still manually adjust any setting
- Tips panel provides context-specific guidance
- Export config includes profile ID for backend processing

---

**Need Help?** Check the QGIS Python Console and Log Messages panel for error details.
