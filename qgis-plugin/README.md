# 🗺️ QGIS Plugin - RealTerrain Studio

This is the QGIS plugin component of RealTerrain Studio. It allows users to select areas on Earth and export them as terrain packages for Unreal Engine 5.

---

## 📁 Folder Structure

```
qgis-plugin/
├── src/
│   ├── realterrain/           ← Main plugin code
│   │   ├── __init__.py        ← Plugin initialization
│   │   ├── plugin.py          ← Main plugin class
│   │   └── metadata.txt       ← Plugin metadata for QGIS
│   │
│   ├── ui/                    ← User interface files
│   │   ├── main_dialog.py     ← Main export dialog
│   │   ├── main_dialog.ui     ← Qt Designer UI file
│   │   └── resources.qrc      ← Qt resources (icons, images)
│   │
│   ├── data_sources/          ← Data fetching modules
│   │   ├── __init__.py
│   │   ├── srtm.py           ← SRTM elevation data (NASA)
│   │   ├── aster.py          ← ASTER elevation data
│   │   ├── sentinel.py       ← Sentinel-2 satellite imagery
│   │   └── osm.py            ← OpenStreetMap data
│   │
│   ├── exporters/             ← Export format handlers
│   │   ├── __init__.py
│   │   ├── heightmap.py      ← Export elevation as heightmap
│   │   ├── textures.py       ← Export satellite imagery
│   │   ├── osm_export.py     ← Export OSM features (roads, buildings)
│   │   └── package.py        ← Create final .rterrain package
│   │
│   └── utils/                 ← Utility functions
│       ├── __init__.py
│       ├── geo_utils.py      ← Geographic calculations
│       ├── file_utils.py     ← File operations
│       ├── api_client.py     ← Backend API communication
│       └── licensing.py      ← License validation
│
├── tests/                     ← Unit tests
│   ├── test_srtm.py
│   ├── test_exporters.py
│   └── test_licensing.py
│
├── requirements.txt           ← Python dependencies
├── setup.py                   ← Plugin installation script
└── README.md                  ← This file
```

---

## 🚀 Installation

### Prerequisites
- QGIS 3.22 or higher
- Python 3.9+
- Internet connection (for downloading data)

### Step 1: Setup Python Environment
```bash
# Navigate to the plugin folder
cd qgis-plugin

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Install Plugin in QGIS
```bash
# Copy plugin to QGIS plugins folder
# Windows:
cp -r src/realterrain/ %APPDATA%\QGIS\QGIS3\profiles\default\python\plugins\

# Mac:
cp -r src/realterrain/ ~/Library/Application\ Support/QGIS/QGIS3/profiles/default/python/plugins/

# Linux:
cp -r src/realterrain/ ~/.local/share/QGIS/QGIS3/profiles/default/python/plugins/
```

### Step 3: Enable Plugin in QGIS
1. Open QGIS
2. Go to: **Plugins** → **Manage and Install Plugins**
3. Click **Installed** tab
4. Find **RealTerrain Studio**
5. Check the box to enable it

---

## 🎯 Features

### Data Sources
- ✅ **SRTM** - 30m/90m elevation data (worldwide)
- ✅ **ASTER GDEM** - 30m elevation data (worldwide)
- ✅ **Sentinel-2** - 10m satellite imagery (Europe)
- ✅ **OpenStreetMap** - Roads, buildings, water, forests

### Export Options
- 📏 **Heightmaps** - 16-bit PNG, RAW, or TIFF
- 🖼️ **Textures** - Satellite imagery, landcover maps
- 🛣️ **Roads** - Spline data for UE5
- 🏗️ **Buildings** - 3D models and placement data
- 🌳 **Vegetation** - Tree and foliage placement data

### Licensing
- 🔐 Hardware-based activation
- ☁️ Cloud license validation
- 📦 Free tier: 10km² per month
- 💎 Pro tier: Unlimited exports

---

## 🧪 Testing

Run tests to verify everything works:

```bash
# Run all tests
pytest tests/

# Run specific test
pytest tests/test_srtm.py

# Run with coverage
pytest --cov=src/realterrain tests/
```

---

## 📖 Usage

### Basic Export Workflow

1. **Open QGIS** and load a basemap
2. **Select Area**: Use the RealTerrain Studio tool to draw a rectangle on the map
3. **Configure Export**:
   - Choose resolution (10m, 30m, 90m)
   - Select data sources (SRTM, Sentinel, OSM)
   - Set output folder
4. **Export**: Click "Export Terrain"
5. **Wait**: Plugin downloads and processes data
6. **Result**: Get a `.rterrain` package ready for UE5

---

## 🔧 Development

### Code Style
- Follow PEP 8 (Python style guide)
- Use type hints where appropriate
- Add docstrings to all functions
- Keep functions small and focused

### Adding a New Data Source

1. Create new file in `src/data_sources/`
2. Implement `DataSource` base class
3. Add tests in `tests/`
4. Update `requirements.txt` if needed
5. Document in this README

Example:
```python
# src/data_sources/my_source.py
from .base import DataSource

class MyDataSource(DataSource):
    """
    Fetch data from My Data Source.
    """

    def fetch(self, bbox, resolution):
        """
        Fetch data for given bounding box.

        Args:
            bbox: (min_lon, min_lat, max_lon, max_lat)
            resolution: Resolution in meters

        Returns:
            numpy.ndarray: The fetched data
        """
        # Implementation here
        pass
```

---

## 🐛 Troubleshooting

### Plugin doesn't appear in QGIS
- Check that files are in correct QGIS plugins folder
- Verify QGIS version is 3.22+
- Check QGIS Python console for errors

### Data download fails
- Check internet connection
- Verify data source is available
- Check API rate limits
- Try different data source

### License validation fails
- Check internet connection
- Verify license key is correct
- Contact support if issue persists

---

## 📝 License Requirements

**Environment Variables:**
Create a `.env` file (NOT tracked by git):
```
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key-here
```

---

## 🆘 Support

- Check troubleshooting section above
- Read main project documentation
- Open an issue on GitHub
- Email: support@realterrainstudio.com

---

**Built with Python + QGIS + PyQt5**
