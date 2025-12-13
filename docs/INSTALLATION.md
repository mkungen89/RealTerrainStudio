# RealTerrain Studio - Installation Guide

**Version:** 1.0.0
**Last Updated:** December 13, 2024

---

## 📋 Table of Contents

1. [System Requirements](#system-requirements)
2. [QGIS Installation](#qgis-installation)
3. [Plugin Installation](#plugin-installation)
4. [UE5 Plugin Installation](#ue5-plugin-installation)
5. [License Activation](#license-activation)
6. [Verification](#verification)
7. [Troubleshooting Installation](#troubleshooting-installation)
8. [Updating](#updating)
9. [Uninstallation](#uninstallation)

---

## 💻 System Requirements

### Minimum Requirements

**Hardware:**
- **CPU:** Dual-core 2.0 GHz or better
- **RAM:** 8 GB
- **Storage:** 10 GB free space (SSD recommended)
- **GPU:** Integrated graphics (Intel HD 4000+)
- **Internet:** Broadband connection (10 Mbps+)

**Software:**
- **OS:** Windows 10/11, macOS 10.15+, or Linux (Ubuntu 20.04+)
- **QGIS:** 3.28 or newer (LTR recommended)
- **Python:** 3.9+ (included with QGIS)

### Recommended Requirements

**Hardware:**
- **CPU:** Quad-core 3.0 GHz or better
- **RAM:** 16 GB or more
- **Storage:** 50 GB free space on SSD
- **GPU:** Dedicated GPU with 2GB+ VRAM
- **Internet:** 50 Mbps+ for fast downloads

**Software:**
- **OS:** Windows 11, macOS 13+, or Ubuntu 22.04 LTS
- **QGIS:** 3.34 LTR (Long Term Release)
- **Python:** 3.11

### For Unreal Engine Import

**Additional Requirements:**
- **Unreal Engine:** 5.3 or newer
- **GPU:** NVIDIA GTX 1060 / AMD RX 580 or better
- **RAM:** 16 GB minimum (32 GB recommended)
- **Storage:** Additional 50-100 GB for UE5 project

---

## 📦 QGIS Installation

RealTerrain Studio requires QGIS as the base platform.

### Windows

#### Method 1: Standalone Installer (Recommended)

1. **Download QGIS:**
   - Visit: https://qgis.org/download
   - Click **"Download for Windows"**
   - Choose **"QGIS Standalone Installer Version 3.34"** (LTR)
   - Download the 64-bit installer (~400 MB)

2. **Run Installer:**
   - Double-click `QGIS-OSGeo4W-3.34.x-x.msi`
   - Click **"Next"** on welcome screen
   - Accept license agreement
   - Choose installation location (default: `C:\Program Files\QGIS 3.34\`)
   - Click **"Install"**
   - Wait ~5 minutes for installation

3. **Verify Installation:**
   - Launch QGIS from Start Menu
   - You should see the QGIS splash screen and main window
   - Check version: `Help` → `About` (should show 3.34.x)

#### Method 2: OSGeo4W Network Installer (Advanced)

For users who need custom QGIS components:

1. Download OSGeo4W installer: https://qgis.org/downloads/OSGeo4W-v2.exe
2. Run installer as Administrator
3. Choose **"Advanced Install"**
4. Select **"Install from Internet"**
5. Choose installation directory
6. Select packages:
   - ✅ `qgis-ltr` (QGIS Long Term Release)
   - ✅ `python3-gdal` (GDAL Python bindings)
   - ✅ `python3-pip` (Python package manager)
7. Click **"Next"** and wait for installation

### macOS

1. **Download QGIS:**
   - Visit: https://qgis.org/download
   - Click **"Download for macOS"**
   - Download **"QGIS-LTR-3.34.x.dmg"** (~600 MB)

2. **Install:**
   - Open the downloaded `.dmg` file
   - Drag **QGIS** icon to **Applications** folder
   - Wait for copy to complete

3. **First Launch:**
   - Open QGIS from Applications
   - macOS may show security warning: **"QGIS is from an unidentified developer"**
   - Go to `System Preferences` → `Security & Privacy`
   - Click **"Open Anyway"**
   - QGIS will launch

4. **Grant Permissions:**
   - QGIS may request permissions for:
     - Files and Folders access
     - Network access
   - Click **"Allow"** for each request

### Linux (Ubuntu/Debian)

1. **Add QGIS Repository:**
```bash
# Add QGIS signing key
wget -qO - https://qgis.org/downloads/qgis-2024.gpg.key | sudo gpg --dearmor -o /etc/apt/keyrings/qgis-2024.gpg

# Add repository
sudo sh -c 'echo "deb [arch=amd64 signed-by=/etc/apt/keyrings/qgis-2024.gpg] https://qgis.org/ubuntu $(lsb_release -cs) main" > /etc/apt/sources.list.d/qgis.list'

# Update package list
sudo apt update
```

2. **Install QGIS:**
```bash
sudo apt install qgis qgis-plugin-grass
```

3. **Verify Installation:**
```bash
qgis --version
# Should output: QGIS 3.34.x 'Prizren'
```

---

## 🔌 Plugin Installation

Once QGIS is installed, install the RealTerrain Studio plugin.

### Method 1: Install from QGIS Plugin Repository (Recommended)

1. **Open Plugin Manager:**
   - Launch QGIS
   - Go to: `Plugins` → `Manage and Install Plugins`
   - Or press `Ctrl+Shift+M` (Windows/Linux) / `Cmd+Shift+M` (macOS)

2. **Search for Plugin:**
   - Click **"All"** tab
   - In search box, type: **"RealTerrain Studio"**
   - Click on **"RealTerrain Studio"** in results

3. **Install:**
   - Click **"Install Plugin"** button
   - Wait for download and installation (~30 seconds)
   - You'll see: **"Plugin installed successfully"**

4. **Verify:**
   - Close Plugin Manager
   - Look for RealTerrain Studio icon in toolbar:
     - 🏔️ Mountain icon
   - Or check menu: `Plugins` → `RealTerrain Studio`

### Method 2: Install from ZIP File

If you have the plugin ZIP file (e.g., from a beta release):

1. **Open Plugin Manager:**
   - `Plugins` → `Manage and Install Plugins`

2. **Install from ZIP:**
   - Click **"Install from ZIP"** tab
   - Click **"..."** to browse
   - Select downloaded file: `realterrain_studio_v1.0.0.zip`
   - Click **"Install Plugin"**
   - Wait for installation

3. **Enable Plugin:**
   - Click **"Installed"** tab
   - Find **"RealTerrain Studio"**
   - Check the box to enable it
   - Click **"Close"**

### Method 3: Manual Installation (Advanced)

For developers or custom installations:

1. **Locate QGIS Plugin Directory:**

   **Windows:**
   ```
   C:\Users\<YourUsername>\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\
   ```

   **macOS:**
   ```
   ~/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/
   ```

   **Linux:**
   ```
   ~/.local/share/QGIS/QGIS3/profiles/default/python/plugins/
   ```

2. **Extract Plugin:**
   - Extract `realterrain_studio.zip` to the plugins directory
   - You should have a folder structure like:
   ```
   plugins/
   └── realterrain_studio/
       ├── __init__.py
       ├── metadata.txt
       ├── src/
       └── ...
   ```

3. **Restart QGIS:**
   - Close and reopen QGIS
   - Plugin will appear in `Plugins` → `Manage and Install Plugins` → `Installed`

### Post-Installation: Python Dependencies

RealTerrain Studio requires some Python packages. They'll be installed automatically on first run.

If you get errors, manually install:

**In QGIS Python Console** (`Plugins` → `Python Console`):

```python
import subprocess
import sys

# Get QGIS Python executable
python_exe = sys.executable

# Install dependencies
packages = ['numpy', 'requests', 'Pillow']
for package in packages:
    subprocess.check_call([python_exe, '-m', 'pip', 'install', package])

print("Dependencies installed!")
```

---

## 🎮 UE5 Plugin Installation

The Unreal Engine 5 plugin allows importing exported terrain files.

### Prerequisites

- **Unreal Engine 5.3+** installed
- **RealTerrain Studio QGIS plugin** installed (to export `.rterrain` files)

### Download UE5 Plugin

**Free Tier:**
- Download from: https://realterrainstudio.com/downloads

**Pro License:**
- Download from your account dashboard

You'll get: `RealTerrainStudio_UE5_v1.0.0.zip` (~50 MB)

### Installation

#### Method 1: Marketplace Plugin (Coming Soon)

1. Open Epic Games Launcher
2. Go to **Unreal Engine** → **Library**
3. Search for **"RealTerrain Studio"**
4. Click **"Install to Engine"**
5. Choose UE5 version (5.3+)
6. Wait for installation

#### Method 2: Manual Installation (Current)

1. **Extract Plugin:**
   - Extract `RealTerrainStudio_UE5_v1.0.0.zip`
   - You'll get a `RealTerrainStudio` folder

2. **Choose Installation Location:**

   **Option A: Engine Plugins (All Projects)**
   - Good if you'll use the plugin in multiple projects
   - Location:
     ```
     C:\Program Files\Epic Games\UE_5.3\Engine\Plugins\Marketplace\RealTerrainStudio\
     ```
   - Copy the extracted `RealTerrainStudio` folder here

   **Option B: Project Plugins (Single Project)**
   - Good for per-project management
   - Location:
     ```
     C:\MyUE5Projects\MyProject\Plugins\RealTerrainStudio\
     ```
   - Create `Plugins` folder in your project if it doesn't exist
   - Copy the `RealTerrainStudio` folder here

3. **Restart Unreal Engine:**
   - If UE5 was open, close it completely
   - Reopen your project

4. **Enable Plugin:**
   - Go to: `Edit` → `Plugins`
   - Search for: **"RealTerrain Studio"**
   - Check the box to enable it
   - Click **"Restart Now"**

5. **Verify Installation:**
   - After restart, check menu: `Tools` → `RealTerrain Studio`
   - You should see: **"Import Terrain"** option

### Building from Source (Advanced)

For developers who want to build the plugin:

1. **Prerequisites:**
   - Visual Studio 2022 (Windows)
   - Xcode 14+ (macOS)
   - Unreal Engine 5.3+ source build

2. **Clone Repository:**
```bash
git clone https://github.com/realterrainstudio/ue5-plugin.git
cd ue5-plugin
```

3. **Generate Project Files:**
   - Right-click `RealTerrainStudio.uproject`
   - Click **"Generate Visual Studio project files"**

4. **Build:**
   - Open `RealTerrainStudio.sln` in Visual Studio
   - Set configuration to: **Development Editor**
   - Build solution (F7)

5. **Package Plugin:**
   - In UE5 Editor: `Edit` → `Plugins` → `RealTerrain Studio`
   - Click **"Package"**
   - Choose output directory
   - Plugin will be compiled and packaged

---

## 🔑 License Activation

### Free Tier (No Activation Required)

1. Launch RealTerrain Studio in QGIS
2. Click **"Use Free Tier"** button
3. You're ready to go!

**Free Tier Includes:**
- 100 km² exports per month
- Standard data sources (30m elevation, 10m satellite)
- Roads and buildings
- Personal use only

### Pro License

1. **Purchase License:**
   - Visit: https://realterrainstudio.com/pricing
   - Choose: **Pro License** ($49/month or $499/year)
   - Complete checkout
   - You'll receive license key via email

2. **Activate in QGIS:**
   - Open RealTerrain Studio panel
   - Click **"Enter License Key"**
   - Paste your license key (format: `RTSP-XXXX-XXXX-XXXX-XXXX`)
   - Click **"Activate"**
   - Wait for validation (~2 seconds)
   - You'll see: **"Pro License Activated ✓"**

3. **Verify Activation:**
   - Click **"License Info"** button
   - Should show:
     ```
     License Type: Pro
     Status: Active
     Expires: 2025-01-13
     Usage: Unlimited exports
     ```

### Offline Activation

If you're on a restricted network:

1. **Generate Activation Request:**
   - Click **"Offline Activation"**
   - Click **"Generate Request File"**
   - Save `activation_request.json`

2. **Get Activation Response:**
   - On a computer with internet, visit: https://realterrainstudio.com/offline-activate
   - Upload `activation_request.json`
   - Download `activation_response.json`

3. **Activate:**
   - Back on your restricted computer
   - Click **"Load Response File"**
   - Select `activation_response.json`
   - License will activate offline

### Educational License

Students and educators get 50% off:

1. **Apply for Educational License:**
   - Visit: https://realterrainstudio.com/education
   - Fill out form with:
     - School name
     - Student/Teacher ID
     - School email address
   - Upload proof of enrollment/employment

2. **Receive License:**
   - You'll get approved within 1-2 business days
   - Educational license key sent to your school email

3. **Activate:**
   - Same process as Pro License above
   - License will show: **"Educational License"**

---

## ✅ Verification

After installation, verify everything works:

### QGIS Plugin Verification

1. **Open QGIS**
2. **Check Plugin is Loaded:**
   - Look for 🏔️ icon in toolbar
   - Or: `Plugins` → `RealTerrain Studio` menu exists

3. **Open Panel:**
   - Click the 🏔️ icon
   - Panel should open on right side

4. **Test Basic Function:**
   - Draw a small bounding box anywhere
   - Click **"Preview"**
   - Should show area calculation and data estimate

5. **Check Version:**
   - In panel, click **"About"**
   - Should show: **"Version 1.0.0"**

### UE5 Plugin Verification

1. **Open UE5 Project**
2. **Check Plugin is Enabled:**
   - `Edit` → `Plugins`
   - Search: "RealTerrain Studio"
   - Should be enabled with checkmark

3. **Check Menu:**
   - `Tools` → `RealTerrain Studio` → `Import Terrain`
   - Import window should open

4. **Test Import (Optional):**
   - Use QGIS to export a small test terrain
   - Import it using UE5 plugin
   - Should create landscape in level

---

## 🔧 Troubleshooting Installation

### QGIS Issues

**Problem:** "QGIS won't start after installation"

**Solutions:**
- Windows: Reinstall with "Run as Administrator"
- macOS: Check Security & Privacy settings, allow QGIS
- Linux: Check terminal for errors: `qgis --verbose`

---

**Problem:** "Plugin doesn't appear after installation"

**Solutions:**
1. Restart QGIS completely
2. Check: `Plugins` → `Manage and Install Plugins` → `Installed` → Ensure "RealTerrain Studio" is checked
3. Check QGIS log: `View` → `Panels` → `Log Messages`
4. Look for Python errors

---

**Problem:** "Python error on plugin load"

**Solutions:**
1. Check Python version in QGIS: `Plugins` → `Python Console`:
   ```python
   import sys
   print(sys.version)  # Should be 3.9+
   ```

2. Install missing dependencies:
   ```python
   import subprocess, sys
   subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'numpy', 'requests', 'Pillow'])
   ```

3. Reinstall plugin

---

**Problem:** "GDAL not available"

**Solutions:**
- **Windows:** Reinstall QGIS using standalone installer (includes GDAL)
- **macOS:** Install GDAL framework: `brew install gdal`
- **Linux:** `sudo apt install python3-gdal`

### UE5 Plugin Issues

**Problem:** "Plugin doesn't appear in UE5"

**Solutions:**
1. Verify plugin location is correct
2. Check UE5 version is 5.3+
3. Manually enable: `Edit` → `Plugins` → Search "RealTerrain" → Check box
4. Rebuild plugin from source if needed

---

**Problem:** "Plugin causes UE5 to crash"

**Solutions:**
1. Check UE5 logs: `Saved/Logs/`
2. Disable plugin and re-enable
3. Verify plugin is compiled for your UE5 version
4. Download matching version from website

---

**Problem:** "Cannot import .rterrain files"

**Solutions:**
1. Verify file is valid (not corrupted)
2. Check UE5 console for error messages
3. Try re-exporting from QGIS
4. Update plugin to latest version

### License Issues

**Problem:** "License activation fails"

**Solutions:**
1. Check internet connection
2. Verify license key is correct (copy-paste carefully)
3. Check license hasn't expired
4. Contact support: support@realterrainstudio.com

---

**Problem:** "License shows as expired but I paid"

**Solutions:**
1. Check payment went through (check email receipt)
2. License activates within 24 hours of payment
3. Try deactivating and reactivating
4. Contact billing: billing@realterrainstudio.com

---

## 🔄 Updating

### Updating QGIS Plugin

#### Automatic Update (Recommended)

1. Open QGIS
2. Go to: `Plugins` → `Manage and Install Plugins`
3. Click **"Upgradeable"** tab
4. If update available:
   - **"RealTerrain Studio"** will appear with **"Upgrade Plugin"** button
   - Click **"Upgrade Plugin"**
   - Wait for update (~30 seconds)
   - Restart QGIS

#### Manual Update

1. Download latest version from website
2. `Plugins` → `Manage and Install Plugins` → `Install from ZIP`
3. Select new ZIP file
4. Click **"Install Plugin"** (will overwrite old version)
5. Restart QGIS

### Updating UE5 Plugin

1. **Download new version** from website
2. **Close Unreal Engine** completely
3. **Delete old plugin folder:**
   - Engine plugins: `UE_5.3\Engine\Plugins\Marketplace\RealTerrainStudio\`
   - Project plugins: `MyProject\Plugins\RealTerrainStudio\`
4. **Install new version** (same as installation steps above)
5. **Reopen UE5**

### Update Notifications

Enable update notifications:
- QGIS: `Settings` → `Options` → `Network` → Check "Check for plugin updates daily"
- Updates will show automatically in Plugin Manager

---

## 🗑️ Uninstallation

### Uninstalling QGIS Plugin

1. **Open QGIS**
2. **Go to Plugin Manager:**
   - `Plugins` → `Manage and Install Plugins`
3. **Find Plugin:**
   - Click **"Installed"** tab
   - Find **"RealTerrain Studio"**
4. **Uninstall:**
   - Click **"Uninstall Plugin"** button
   - Confirm: **"Yes, uninstall"**
5. **Restart QGIS**

**Plugin data will remain** in:
- Windows: `C:\Users\<Name>\AppData\Roaming\RealTerrainStudio\`
- macOS: `~/Library/Application Support/RealTerrainStudio/`
- Linux: `~/.config/RealTerrainStudio/`

To delete data:
- Manually delete the folder above
- This removes cache, settings, and license info

### Uninstalling UE5 Plugin

1. **Close Unreal Engine**
2. **Delete Plugin Folder:**
   - Engine: `UE_5.3\Engine\Plugins\Marketplace\RealTerrainStudio\`
   - Project: `MyProject\Plugins\RealTerrainStudio\`
3. **Delete Intermediate Files:**
   - In your project: `MyProject\Intermediate\`
   - In your project: `MyProject\Binaries\`
4. **Regenerate Project Files:**
   - Right-click `MyProject.uproject`
   - Click **"Generate Visual Studio project files"**
5. **Reopen Project**

### Uninstalling QGIS (Complete Removal)

**Windows:**
1. `Settings` → `Apps` → `QGIS 3.34`
2. Click **"Uninstall"**
3. Follow uninstaller prompts
4. Manually delete (if remaining):
   - `C:\Program Files\QGIS 3.34\`
   - `C:\Users\<Name>\AppData\Roaming\QGIS\`

**macOS:**
1. Delete `/Applications/QGIS.app`
2. Delete `~/Library/Application Support/QGIS/`

**Linux:**
```bash
sudo apt remove qgis qgis-plugin-grass
sudo apt autoremove
rm -rf ~/.local/share/QGIS/
```

---

## 📞 Installation Support

If you encounter issues not covered here:

**Email Support:**
- support@realterrainstudio.com
- Include:
  - Operating system and version
  - QGIS version
  - Error messages (screenshots helpful)
  - Steps you've already tried

**Community Support:**
- Discord: https://discord.gg/realterrainstudio
- Forum: https://forum.realterrainstudio.com

**Video Guides:**
- Installation walkthrough: https://youtube.com/...
- Troubleshooting common issues: https://youtube.com/...

---

**Last Updated:** December 13, 2024
**Version:** 1.0.0
**For:** RealTerrain Studio
**By:** RealTerrain Studio Team
