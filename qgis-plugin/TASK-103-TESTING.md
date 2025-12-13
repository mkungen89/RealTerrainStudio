# TASK-103: License Validation UI - Testing Guide

## ✅ Task Status: READY FOR TESTING

The license validation and management system has been implemented.

---

## 📋 What Was Created

### Core Files:

1. **`src/realterrain/licensing/__init__.py`** - Licensing module initialization

2. **`src/realterrain/licensing/hardware_fingerprint.py`** - Hardware fingerprint generation
   - Generates unique 32-character hardware ID
   - Uses MAC address, machine name, processor info, system info
   - Stable across reboots

3. **`src/realterrain/licensing/license_manager.py`** - License management core
   - License validation and storage
   - Hardware fingerprint integration
   - Free tier limits enforcement
   - License status checking
   - Supabase validation (mock for now)

4. **`src/realterrain/ui/license_dialog.py`** - License dialog UI
   - Two tabs: Activate and License Info
   - License key input and validation
   - Hardware ID display and copy
   - Pro features list
   - Current status display
   - Deactivate functionality

5. **Updated `src/realterrain/plugin.py`** - Plugin integration
   - Shows license dialog on first run
   - "Manage License" menu item added
   - License manager initialization

6. **Updated `src/realterrain/ui/main_dialog.py`** - Main dialog integration
   - License status displayed in header
   - "Manage License" button added
   - Export restrictions based on license
   - Area size validation

---

## 🎯 License System Features

### License Tiers:

**Free Tier:**
- Maximum area: 10 km²
- Monthly exports: 10
- Max resolution: 30m
- Basic features only

**Pro Tier:**
- Unlimited area
- Unlimited monthly exports
- Up to 1m resolution
- All special features
- Priority support
- Commercial use

---

## 🧪 Testing Instructions

### Step 1: Copy Updated Plugin

Copy the updated plugin files to QGIS:

**Windows PowerShell:**
```powershell
Copy-Item -Path "qgis-plugin\src\realterrain\*" -Destination "$env:APPDATA\QGIS\QGIS3\profiles\default\python\plugins\realterrain\" -Recurse -Force
```

### Step 2: Reset First Run (Optional)

To test the first-run experience:

**Windows:**
1. Press Windows + R
2. Type `regedit` and press Enter
3. Navigate to: `HKEY_CURRENT_USER\Software\RealTerrainStudio\QGIS`
4. Delete the `app/first_run` key (or set it to `true`)

**Or use Python in QGIS:**
```python
from qgis.PyQt.QtCore import QSettings
settings = QSettings("RealTerrainStudio", "QGIS")
settings.setValue("app/first_run", True)
settings.sync()
```

### Step 3: Restart QGIS

1. Close QGIS completely
2. Reopen QGIS
3. Enable RealTerrain Studio plugin (if not already enabled)

---

## 🔍 Test Scenarios

### Scenario 1: First Run Experience

**Expected:**
1. Plugin loads
2. **License dialog appears automatically**
3. Two tabs visible: "Activate" and "License Info"
4. "Continue with Free Version" button visible at bottom

**Test Actions:**
1. Click "Continue with Free Version"
2. Dialog closes
3. Plugin ready to use with Free tier

### Scenario 2: View Hardware ID

**Steps:**
1. If not already open, go to **Plugins → RealTerrain Studio → Manage License**
2. Go to "Activate" tab
3. Look at "Hardware ID" section

**Expected:**
- 32-character hexadecimal string displayed
- Can select text with mouse
- "Copy" button works
- Hardware ID copied to clipboard when clicked

### Scenario 3: Activate with Invalid Key

**Steps:**
1. Open license dialog
2. Enter invalid key: `INVALID-KEY-1234`
3. Click "Activate"

**Expected:**
- ❌ Error message: "Invalid license key format" OR "Invalid license key. Please check and try again."
- Key remains in input field
- No changes to license status

### Scenario 4: Activate with Test Key

**Test Keys (Mock validation):**
- `TEST-1234-5678-ABCD`
- `DEMO-ABCD-1234-EFGH`
- Any key starting with `PRO-` (e.g., `PRO-TEST-1234-ABCD`)

**Steps:**
1. Open license dialog
2. Enter test key: `TEST-1234-5678-ABCD`
3. Click "Activate"

**Expected:**
- ✅ Success message: "License activated successfully!"
- Input field clears
- Automatically switches to "License Info" tab
- Status shows "Pro" in green
- License key displayed (partially masked)

### Scenario 5: View License Status (Free)

**Steps:**
1. Start fresh (no license activated)
2. Open license dialog
3. Go to "License Info" tab

**Expected:**
```
License Status: Free
Using free version with limited features
Hardware ID: [your hardware id]

Current Limits:
- Area limit: 10 km²
- Monthly exports: 10
- Max resolution: 30m
```

- "Deactivate License" button disabled

### Scenario 6: View License Status (Pro)

**Steps:**
1. Activate with test key (see Scenario 4)
2. Open license dialog
3. Go to "License Info" tab

**Expected:**
```
License Status: Pro
Pro license active
License Key: TEST-1234-****-****
Activated: [date/time]
Email: user@example.com
Hardware ID: [your hardware id]

Current Limits:
- Area limit: Unlimited
- Monthly exports: Unlimited
- Max resolution: 1m (highest available)
```

- "Deactivate License" button enabled

### Scenario 7: Deactivate License

**Steps:**
1. Activate a Pro license first
2. Go to "License Info" tab
3. Click "Deactivate License"
4. Confirm in the dialog

**Expected:**
- Confirmation dialog appears
- After confirming, license is deactivated
- Status changes back to "Free"
- "Deactivate License" button disabled

### Scenario 8: License Status in Main Dialog (Free)

**Steps:**
1. Ensure using Free tier (no license or deactivated)
2. Click main plugin button to open export dialog

**Expected:**
- Header shows: "License: Free" (in gray color)
- "Manage License" button present in header
- All other functionality works

### Scenario 9: License Status in Main Dialog (Pro)

**Steps:**
1. Activate Pro license
2. Click main plugin button

**Expected:**
- Header shows: "License: Pro" (in green, bold)
- "Manage License" button present
- All features available

### Scenario 10: Manage License from Main Dialog

**Steps:**
1. Open main export dialog
2. Click "Manage License" button in header

**Expected:**
- License dialog opens
- Can activate/deactivate
- After closing, header updates with new license status

### Scenario 11: Export Restriction (Free Tier - Small Area)

**Steps:**
1. Use Free tier
2. Set area to small size (< 10 km²):
   - Min Lon: -122.5, Min Lat: 37.7
   - Max Lon: -122.4, Max Lat: 37.75
3. Click "Export Terrain"

**Expected:**
- Export allowed
- Success message shows
- No license warning

### Scenario 12: Export Restriction (Free Tier - Large Area)

**Steps:**
1. Use Free tier
2. Set area to large size (> 10 km²):
   - Min Lon: -122.5, Min Lat: 37.7
   - Max Lon: -122.0, Max Lat: 38.0
3. Click "Export Terrain"

**Expected:**
- **Warning message:** "Free tier limited to 10 km². Upgrade to Pro for unlimited exports."
- Export does NOT proceed
- Orange/yellow warning bar at top of QGIS

### Scenario 13: Export with Pro License (Large Area)

**Steps:**
1. Activate Pro license
2. Set large area (> 10 km²)
3. Click "Export Terrain"

**Expected:**
- Export allowed
- Success message
- No restrictions

### Scenario 14: Menu Items

**Steps:**
1. Go to **Plugins** menu
2. Hover over **RealTerrain Studio**

**Expected Menu Items:**
- ✅ Export Terrain to UE5
- ✅ Manage License (new!)

**Test:**
- Click "Export Terrain to UE5" → Opens main dialog
- Click "Manage License" → Opens license dialog

---

## ✅ Acceptance Criteria Verification

- [ ] **License dialog shows on first run** - Auto-appears when plugin first loaded
- [ ] **Can activate with valid license key** - Test keys work
- [ ] **Can use Free version without key** - "Continue with Free" button works
- [ ] **License status shown in main UI** - Header displays tier and color
- [ ] **Invalid keys rejected with friendly message** - Clear error messages

---

## 🔧 Mock Validation Keys

For testing, these keys will be accepted (mock validation):

✅ **Accepted:**
- `TEST-1234-5678-ABCD`
- `DEMO-ABCD-1234-EFGH`
- `PRO-XXXX-XXXX-XXXX` (anything starting with PRO-)

❌ **Rejected:**
- `INVALID-KEY-1234` (wrong format)
- `FAKE-1234-5678-9999` (not in mock list)
- Short keys or wrong format

---

## 📝 License Storage

Licenses are stored using QSettings (platform-specific):

**Windows:** Registry at `HKEY_CURRENT_USER\Software\RealTerrainStudio\QGIS`

**Mac/Linux:** INI file in appropriate user config directory

**Stored Keys:**
- `license/key` - License key
- `license/activated_date` - Activation timestamp
- `license/hardware_id` - Hardware fingerprint
- `license/user_email` - User email
- `app/first_run` - First run flag

---

## 🐛 Known Limitations (By Design)

1. **Supabase Validation** - Currently using mock validation
   - Real backend integration in future task
   - Test keys work for development

2. **Monthly Export Counting** - Not yet implemented
   - Free tier monthly limit not enforced yet
   - Will be added when backend is connected

3. **Encryption** - Basic storage via QSettings
   - More robust encryption in future version
   - Sufficient for development/testing

---

## 🎨 Visual Expectations

### License Dialog - Activate Tab:
```
┌────────────────────────────────────────────────┐
│         License Activation                      │
├────────────────────────────────────────────────┤
│  [Activate] [License Info]                     │
│                                                 │
│  Enter your license key...                     │
│                                                 │
│  License Key                                   │
│  ┌──────────────────────┐                     │
│  │ XXXX-XXXX-XXXX-XXXX  │ [Activate]          │
│  └──────────────────────┘                     │
│                                                 │
│  Hardware ID                                   │
│  ┌──────────────────────────────┐             │
│  │ 1a2b3c4d5e6f7g8h9i0j1k2l3m4n │ [Copy]      │
│  └──────────────────────────────┘             │
│                                                 │
│  Pro Features                                  │
│  • Unlimited area exports                      │
│  • Highest resolution                          │
│  • All special features                        │
│                                                 │
│  [Continue with Free Version]         [Close] │
└────────────────────────────────────────────────┘
```

### Main Dialog Header (Free):
```
┌────────────────────────────────────────────────┐
│ 🗺️ Open World / RPG                            │
│ Vast explorable worlds                         │
│ License: Free                    [Change Profile]│
│                                 [Manage License]│
└────────────────────────────────────────────────┘
```

### Main Dialog Header (Pro):
```
┌────────────────────────────────────────────────┐
│ 🗺️ Open World / RPG                            │
│ Vast explorable worlds                         │
│ License: Pro  (green)            [Change Profile]│
│                                 [Manage License]│
└────────────────────────────────────────────────┘
```

---

## 🎯 Next Steps

Once license system is verified:

1. **TASK-201:** Implement SRTM Data Fetcher
2. Connect to real Supabase backend for validation
3. Implement monthly export tracking
4. Add payment/purchase flow

---

## 💡 Testing Tips

1. **Reset between tests:**
   - Deactivate license before testing free tier
   - Clear settings to test first-run

2. **Check logs:**
   - View → Panels → Log Messages → RealTerrain
   - Look for activation/validation messages

3. **Hardware ID stays the same:**
   - Should be consistent across restarts
   - Only changes if hardware significantly changes

4. **License persists:**
   - Once activated, survives QGIS restart
   - Stored in system settings

---

**Need Help?** Check QGIS Log Messages panel for detailed error information.
