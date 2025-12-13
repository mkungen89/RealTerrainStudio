# 🤖 CLAUDE.MD - AI Assistant Context Guide
## RealTerrain Studio - "From Earth to Engine"

> **Purpose:** This file provides context for AI assistants (like Claude Code) working on the RealTerrain Studio project.

---

## 🎯 PROJECT SUMMARY

**RealTerrain Studio** is a professional terrain creation pipeline that converts real-world geodata into production-ready Unreal Engine 5 landscapes.

- **Tagline:** "From Earth to Engine"
- **Target Users:** Game developers, architects, filmmakers, simulation developers
- **Core Value:** Transform satellite data, elevation maps, and OpenStreetMap data into UE5 in minutes
- **Key Innovation:** Single `.rterrain` file contains everything needed

---

## 📁 PROJECT STRUCTURE

```
RealTerrainStudio/
├── qgis-plugin/          # Python QGIS plugin (data export)
│   ├── src/realterrain/  # Main plugin source
│   ├── tests/            # Python tests
│   └── venv/             # Python virtual environment
├── ue5-plugin/           # C++ UE5 plugin (terrain import)
│   ├── Source/           # C++ source files
│   └── Resources/        # Plugin resources
├── backend/              # Supabase backend (licensing, payments)
│   ├── supabase/         # Supabase configuration
│   └── config/           # Backend config files
├── website/              # Next.js website (marketing, docs)
│   ├── src/              # Website source
│   └── public/           # Static assets
├── docs/                 # Documentation
├── tests/                # Integration tests
└── .claude/              # Claude Code configuration
```

---

## 🔑 KEY COMPONENTS

### 1. **QGIS Plugin** (Python 3.9+)
**Location:** `qgis-plugin/`
**Purpose:** Export real-world terrain data to `.rterrain` format

**Key Features:**
- Fetch elevation data (SRTM, ASTER, LiDAR)
- Download satellite imagery (Sentinel-2, Mapbox)
- Query OpenStreetMap data (roads, buildings, POIs)
- 13 game profile presets (FPS, RPG, Flight Sim, etc.)
- Hardware validation system
- License management with Supabase
- Single compressed `.rterrain` file output

**Tech Stack:**
- Python 3.9+
- PyQt5 (UI)
- QGIS API
- GDAL/OGR (geospatial)
- Supabase (backend)
- NumPy, Pillow, Requests

### 2. **UE5 Plugin** (C++)
**Location:** `ue5-plugin/`
**Purpose:** Import `.rterrain` files into Unreal Engine 5

**Key Features:**
- One-click import
- Automatic landscape generation
- Material application (PBR materials)
- Road spline generation
- Building placement
- Vegetation spawning
- World Partition configuration

**Tech Stack:**
- C++ (UE5 API)
- Unreal Engine 5.3+
- Slate UI framework

### 3. **Backend** (Supabase)
**Location:** `backend/`
**Purpose:** License validation, user management, payments

**Key Features:**
- User authentication
- License key generation and validation
- Hardware fingerprint tracking (3 activations per license)
- Stripe payment integration
- Cloud processing queue
- Analytics and usage tracking

**Tech Stack:**
- Supabase (PostgreSQL + Edge Functions)
- Python (API scripts)
- Stripe API

### 4. **Website** (Next.js)
**Location:** `website/`
**Purpose:** Marketing, documentation, user dashboard

**Key Features:**
- Product landing page
- Pricing and plans
- User dashboard
- Download portal
- Documentation
- Blog/tutorials

**Tech Stack:**
- Next.js 14
- React
- Tailwind CSS
- Supabase Auth

---

## 🎮 .RTERRAIN FILE FORMAT

**Extension:** `.rterrain`
**Format:** ZIP archive with specific structure
**Compression:** ~75% reduction

### File Structure:
```
terrain.rterrain (ZIP Archive)
├── metadata.json         # Terrain metadata, bounds, profile
├── elevation.png         # 16-bit grayscale heightmap
├── satellite.png         # RGB satellite imagery
├── materials/
│   ├── base_color.png
│   ├── normal.png
│   ├── roughness.png
│   └── mask.png         # Material blend mask
├── osm/
│   ├── roads.json       # Road data with types
│   ├── buildings.json   # Building footprints
│   ├── vegetation.json  # Tree/forest areas
│   └── pois.json        # Points of interest
└── tactical/ (optional)
    ├── sightlines.json
    └── cover_map.png
```

---

## 🚀 DEVELOPMENT PHASES

### **Phase 1: MVP** (Current - Q1 2025)
- [x] Project structure setup
- [x] Supabase backend configured
- [ ] QGIS plugin core functionality
- [ ] Basic terrain export
- [ ] UE5 import system
- [ ] License validation

### **Phase 2: Enhancement** (Q2 2025)
- [ ] Advanced materials
- [ ] OSM integration (roads, buildings)
- [ ] Game profile presets
- [ ] Batch processing
- [ ] Cloud processing

### **Phase 3: Polish** (Q3 2025)
- [ ] Performance optimization
- [ ] Pro features (tactical data, advanced materials)
- [ ] Advanced customization
- [ ] Plugin marketplace submission

---

## 💼 BUSINESS MODEL

### Pricing Tiers:

**Hobby:** $29/month or $249/year
- 10 exports/month
- Up to 25km² area
- 30m elevation resolution
- Basic satellite imagery
- Standard materials

**Professional:** $99/month or $849/year
- Unlimited exports
- Up to 100km² area
- 10m elevation resolution (1m with LiDAR)
- High-res satellite imagery
- Advanced materials
- OSM integration
- Priority support

**Enterprise:** Custom pricing
- Unlimited everything
- Custom processing
- Dedicated support
- Custom integrations
- Bulk licensing

---

## 🔧 DEVELOPER GUIDELINES

### Important Files to Check:
- **AGENT_RULES.md** - Claude Code agent rules and guidelines
- **TASKS.md** - Current task list and priorities
- **CHANGELOG.md** - What has been built so far
- **SUPABASE.md** - Supabase backend documentation

### Coding Standards:

**Python (QGIS Plugin):**
- Use `snake_case` for files and functions
- Type hints required
- Docstrings for all public functions
- Error handling with user-friendly messages
- Logging for debugging

**C++ (UE5 Plugin):**
- Follow Unreal Engine coding standards
- Use `PascalCase` for classes
- UPROPERTY/UFUNCTION macros where appropriate
- Log with UE_LOG
- Blueprintable where useful

**General:**
- **Explain everything** - User is non-technical
- **Test thoroughly** - Create tests for all features
- **Document** - Comments, READMEs, docstrings
- **User-friendly** - Simple language, helpful errors
- **Security first** - Never hardcode keys, validate inputs

### Communication Style:
- Use plain English, avoid jargon
- Explain technical decisions simply
- Provide step-by-step instructions
- Use analogies when helpful
- Always provide context for changes

---

## 🧪 TESTING

**Test Locations:**
- `qgis-plugin/tests/` - Python plugin tests
- `ue5-plugin/Tests/` - UE5 plugin tests
- `tests/` - Integration tests
- Individual `TASK-XXX-TESTING.md` files for feature tests

**Test Requirements:**
- Unit tests for all functions
- Integration tests for features
- Manual test instructions
- Error case coverage

**Running Tests:**
```bash
# Python tests
cd qgis-plugin
venv\Scripts\activate
pytest tests/

# Integration tests
cd tests
pytest
```

---

## 🔐 SECURITY & LICENSING

**License System:**
- Hardware fingerprint validation (3 activations per license)
- Server-side validation via Supabase
- Encrypted license keys
- Grace period for expired licenses

**Security Rules:**
- NEVER hardcode API keys or secrets
- Use environment variables (.env files)
- Validate all inputs (file paths, coordinates)
- Sanitize user data
- Rate limit API calls
- HTTPS only for API calls

---

## 📊 CURRENT STATUS

**Version:** 0.1.0 (Pre-Alpha)
**Phase:** MVP Development
**Last Updated:** December 2024

**Completed:**
- ✅ Project structure
- ✅ Supabase backend setup
- ✅ Database schema
- ✅ Initial Python environment
- ✅ Documentation framework

**In Progress:**
- 🔄 QGIS plugin core functionality
- 🔄 License validation system
- 🔄 Terrain export pipeline

**Next Up:**
- ⏳ Satellite imagery download
- ⏳ OSM data integration
- ⏳ UE5 plugin scaffolding

---

## 🎯 USER PROFILE

**Project Owner:**
- Non-technical founder
- Cannot code
- Needs clear explanations
- Appreciates step-by-step guidance
- Requires thorough testing

**AI Assistant Role:**
1. Build features from descriptions
2. Explain all technical decisions clearly
3. Test everything thoroughly
4. Provide bulletproof code
5. Guide user at every step
6. Use simple language (no jargon)
7. Always provide context

---

## 🛠️ USEFUL COMMANDS

### Python (QGIS Plugin):
```bash
# Activate virtual environment
cd qgis-plugin
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run tests
pytest tests/

# Check Supabase connection
python test_connection.py
```

### Backend:
```bash
cd backend

# Test database connection
python test_connection.py

# Run migrations
python run_migrations.py
```

### Common Tasks:
```bash
# Check project structure
tree /F /A

# View git status
git status

# View recent commits
git log --oneline -10
```

---

## 📚 EXTERNAL RESOURCES

**Data Sources:**
- **SRTM** - NASA elevation data (30m resolution)
- **ASTER** - Elevation data (30m resolution)
- **Sentinel-2** - Satellite imagery (10m resolution)
- **OpenStreetMap** - Roads, buildings, POIs
- **Overpass API** - OSM data query service

**APIs Used:**
- Supabase API (backend)
- Stripe API (payments)
- Overpass API (OSM data)
- QGIS Python API
- Unreal Engine C++ API

**Documentation:**
- QGIS Plugin Development: https://docs.qgis.org/
- Unreal Engine API: https://docs.unrealengine.com/
- Supabase Docs: https://supabase.io/docs
- Stripe API: https://stripe.com/docs/api

---

## ⚡ QUICK REFERENCE

### Project Goal:
Build a professional terrain pipeline from real-world data to UE5.

### Core Philosophy:
**Simple, powerful, bulletproof.** Make complex GIS workflows accessible to everyone.

### Success Criteria:
1. User selects area on map
2. Clicks "Export"
3. Gets single `.rterrain` file
4. Imports to UE5 with one click
5. Gets production-ready terrain

### Key Differentiators:
- ✅ Single file format (not dozens of files)
- ✅ One-click workflow (not complex GIS steps)
- ✅ Game-optimized (not generic terrain)
- ✅ Complete package (elevation + textures + objects)
- ✅ No GIS knowledge required

---

## 🎨 BRAND IDENTITY

**Tagline:** "From Earth to Engine"

**Voice:** Professional yet approachable
**Aesthetic:** Modern, clean, earth tones
**Promise:** Make the complex simple

---

## 📞 PROJECT CONTACTS

**Repository:** (Private GitHub repo)
**Website:** realterrainstudio.com (planned)
**Support:** support@realterrainstudio.com (planned)
**Discord:** (planned for community)

---

## 🔄 KEEPING THIS FILE UPDATED

**Update this file when:**
- Project structure changes significantly
- New major features are added
- Technology stack changes
- Development phase changes
- Business model adjustments
- New pricing tiers added

**Who Updates:** Claude Code (AI assistant) or project owner

---

## 💡 TIPS FOR AI ASSISTANTS

1. **Always read AGENT_RULES.md first** - Contains critical guidelines
2. **Check TASKS.md** - Know what to work on
3. **Review CHANGELOG.md** - Understand what's been built
4. **Test everything** - User cannot debug code
5. **Explain clearly** - User is non-technical
6. **Ask if unsure** - Better to clarify than assume
7. **Follow the roadmap** - Don't skip ahead
8. **Document as you go** - Update docs with code
9. **Security matters** - Validate everything
10. **Make it bulletproof** - Handle all error cases

---

**Last Updated:** December 13, 2024
**For:** RealTerrain Studio Development
**By:** Claude Code Assistant

---

🌍 **From Earth to Engine** 🎮
