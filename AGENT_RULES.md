# 🤖 CLAUDE CODE AGENT RULES & GUIDELINES
## RealTerrain Studio - "From Earth to Engine"

---

## 🎯 PROJECT OVERVIEW

**Product:** RealTerrain Studio  
**Tagline:** "From Earth to Engine"  
**Purpose:** Professional terrain creation pipeline from real-world geodata to Unreal Engine 5  
**User:** Non-technical founder who cannot code  

---

## ⚠️ CRITICAL AGENT RULES

### 1. **ASSUME ZERO CODING KNOWLEDGE**
- Explain EVERY technical decision in simple terms
- Never assume user knows programming concepts
- Always provide context for why you're doing something
- Use analogies and simple language

### 2. **BE EXTREMELY EXPLICIT**
- Every file you create: explain what it does
- Every function: explain in plain English
- Every error: explain what went wrong and how to fix
- Never use jargon without explanation

### 3. **ALWAYS TEST & VERIFY**
- Create test files for every feature
- Provide instructions on how to test manually
- Catch errors before user encounters them
- Include helpful error messages

### 4. **GUIDE STEP-BY-STEP**
- Break complex tasks into small steps
- Number steps clearly (Step 1, Step 2...)
- Wait for confirmation before moving to next major feature
- Never overwhelm with too much at once

### 5. **DOCUMENT EVERYTHING**
- Add comments in code explaining what each part does
- Create README files for each module
- Keep a changelog of what you've built
- Document any prerequisites or dependencies

### 6. **SAFETY FIRST**
- Always backup before major changes
- Never delete files without asking
- Validate all inputs
- Handle errors gracefully with user-friendly messages

### 7. **FOLLOW THE ROADMAP**
- Check TASKS.md before starting work
- Mark tasks as complete when done
- Don't skip ahead without approval
- Stay focused on current sprint

---

## 🏗️ PROJECT STRUCTURE RULES

### Folder Organization:
```
RealTerrainStudio/
├── AGENT_RULES.md          ← This file
├── TASKS.md                ← Task list (check here first!)
├── CHANGELOG.md            ← What's been built
├── README.md               ← Project overview
├── qgis-plugin/
├── ue5-plugin/
├── backend/
├── website/
├── docs/
└── tests/
```

### File Naming:
- Use `snake_case` for Python files: `terrain_exporter.py`
- Use `PascalCase` for C++ files: `TerrainImporter.cpp`
- Use descriptive names: `fetch_elevation_data.py` not `fed.py`
- Include comments at top of each file explaining purpose

---

## 💻 CODING STANDARDS

### Python (QGIS Plugin):
```python
"""
Module: terrain_exporter.py
Purpose: Exports terrain elevation data from various sources
Author: RealTerrain Studio (via Claude Code)
"""

# Always include docstrings
def fetch_elevation_data(bbox, resolution):
    """
    Fetch elevation data for a given area.
    
    Args:
        bbox (tuple): Bounding box (min_lon, min_lat, max_lon, max_lat)
        resolution (int): Resolution in meters (e.g., 30 for 30m)
    
    Returns:
        numpy.ndarray: Elevation data as 2D array
        
    Raises:
        ConnectionError: If data source is unavailable
        ValueError: If bbox is invalid
    """
    # Implementation with helpful comments
    pass
```

### Error Handling:
```python
# ALWAYS wrap risky operations in try-except
try:
    data = fetch_data()
except ConnectionError as e:
    # User-friendly error message
    logger.error(f"Could not connect to server: {e}")
    show_error_dialog("Cannot download data. Check internet connection.")
    return None
```

### Logging:
```python
# ALWAYS add logging for debugging
import logging
logger = logging.getLogger(__name__)

logger.info("Starting terrain export...")
logger.debug(f"Using bbox: {bbox}")
logger.warning("Low resolution selected, results may be pixelated")
logger.error("Failed to fetch data from source")
```

---

## 🎨 UI/UX GUIDELINES

### User Interface Principles:
1. **Simple & Clear**: No technical jargon in UI
2. **Helpful Tooltips**: Explain every option
3. **Progress Feedback**: Always show what's happening
4. **Error Recovery**: Suggest solutions, not just error codes
5. **Sensible Defaults**: Work out-of-box with minimal config

### Example Good UI:
```python
# ✅ GOOD: Clear and helpful
export_button = QPushButton("Export Terrain")
export_button.setToolTip(
    "Click to export terrain data to Unreal Engine format.\n"
    "This will download elevation and satellite imagery."
)

# ❌ BAD: Technical and unclear
export_button = QPushButton("Init DEM proc")
```

---

## 🔐 SECURITY RULES

### Licensing System:
- NEVER store API keys in code
- Use environment variables or config files
- Encrypt sensitive data
- Validate all license inputs server-side
- Hardware fingerprinting must be privacy-respectful

### Data Handling:
- Validate all user inputs
- Sanitize file paths
- Never execute arbitrary code
- Rate limit API calls
- Cache data to avoid re-downloads

---

## 📦 DEPENDENCY MANAGEMENT

### Python Dependencies:
```python
# requirements.txt - Always pin versions
qgis==3.22.0
PyQt5==5.15.9
requests==2.31.0
supabase==1.0.3
cryptography==41.0.0
numpy==1.24.0
gdal==3.4.0
```

### Installation Instructions:
Always provide in README:
```bash
# For user to run (explain each step)
pip install -r requirements.txt
```

---

## 🧪 TESTING REQUIREMENTS

### Every Feature Needs:
1. **Unit tests**: Test individual functions
2. **Integration tests**: Test feature end-to-end
3. **Manual test instructions**: For user to verify
4. **Error case tests**: What happens when things fail

### Test Example:
```python
# tests/test_terrain_exporter.py
def test_fetch_elevation_basic():
    """Test basic elevation data fetching"""
    bbox = (-122.5, 37.7, -122.4, 37.8)  # San Francisco
    data = fetch_elevation_data(bbox, resolution=30)
    
    assert data is not None
    assert data.shape[0] > 0
    assert data.shape[1] > 0
    
def test_fetch_elevation_invalid_bbox():
    """Test error handling for invalid bbox"""
    bbox = (200, 200, 300, 300)  # Invalid coordinates
    data = fetch_elevation_data(bbox, resolution=30)
    
    assert data is None  # Should return None, not crash
```

---

## 📚 DOCUMENTATION RULES

### Code Comments:
```python
# GOOD: Explain WHY, not just WHAT
# Calculate aspect ratio to maintain correct terrain proportions
aspect_ratio = width / height

# BAD: States the obvious
# Set aspect ratio
aspect_ratio = width / height
```

### README Structure (for each module):
```markdown
# Module Name

## What it does
Simple explanation in plain English

## How to use it
Step by step instructions

## Dependencies
What needs to be installed

## Troubleshooting
Common issues and solutions
```

---

## 🚀 DEVELOPMENT WORKFLOW

### Before Starting a Task:
1. Read the task in TASKS.md
2. Check if dependencies are met
3. Plan the approach (explain to user)
4. Get user approval if major decision needed

### While Working:
1. Create files with clear structure
2. Add comments explaining logic
3. Handle errors gracefully
4. Test as you go

### After Completing:
1. Mark task as DONE in TASKS.md
2. Update CHANGELOG.md
3. Create/update documentation
4. Provide testing instructions to user

---

## 🎯 FEATURE PRIORITY RULES

### Phase 1 (MVP): Core functionality
- Basic terrain export
- Simple UI
- Licensing system
- Basic import to UE5

### Phase 2: Enhancement
- Advanced materials
- OSM integration
- Batch processing

### Phase 3: Polish
- Performance optimization
- Advanced features
- Pro features

**NEVER skip ahead without completing current phase!**

---

## 💬 COMMUNICATION STYLE

### When Creating Features:
```
✅ GOOD:
"I'm now creating the terrain exporter module. This will:
1. Connect to SRTM data source (free elevation data)
2. Download elevation for your selected area
3. Convert to format UE5 can read

Creating these files:
- terrain_exporter.py (main logic)
- data_sources/srtm.py (SRTM downloader)
- tests/test_exporter.py (tests)

This will take about 2 minutes..."

❌ BAD:
"Implementing DEM acquisition pipeline via SRTM API integration"
```

### When Errors Occur:
```
✅ GOOD:
"I encountered an error while downloading data. This usually means:
1. No internet connection, or
2. The SRTM server is busy

Let's add a retry mechanism and better error message for users.
Fixed! Now it will try 3 times and show helpful message."

❌ BAD:
"ConnectionError: errno 111"
```

---

## 🔧 TECHNICAL STACK DECISIONS

### Already Decided (Don't Change):
- ✅ QGIS Plugin: Python 3.9+
- ✅ UE5 Plugin: C++
- ✅ Backend: Supabase (PostgreSQL + Edge Functions)
- ✅ Payments: Stripe
- ✅ UI: PyQt5 (QGIS), Slate (UE5)

### When Choosing Libraries:
1. Prefer well-maintained, popular libraries
2. Check license compatibility (MIT, Apache 2.0, BSD)
3. Avoid libraries with many dependencies
4. Always explain why you chose it

---

## 📊 PROGRESS TRACKING

### Always Update:
1. **TASKS.md**: Mark tasks as IN_PROGRESS or DONE
2. **CHANGELOG.md**: Document what was built
3. **README.md**: Update if structure changes

### Regular Checkpoints:
- End of each feature: Summary of what was built
- End of each day: Progress report
- End of each sprint: Demo-ready milestone

---

## 🎓 LEARNING OPPORTUNITIES

### When User Asks "How does this work?":
Explain in layers:
1. Simple analogy
2. What it does for the project
3. Technical details (optional)

Example:
```
User: "What's an API?"

Agent: 
"Think of an API like a waiter at a restaurant:
- You (the app) tell the waiter (API) what you want
- Waiter goes to kitchen (server) 
- Waiter brings back your food (data)

For RealTerrain Studio:
- We ask SRTM API for elevation data
- It fetches it from NASA's servers
- Returns the height map we need

Technical: API = Application Programming Interface, 
a set of rules for programs to talk to each other."
```

---

## ⚡ PERFORMANCE RULES

### Optimization Priorities:
1. **Correctness** first (does it work?)
2. **Usability** second (is it easy to use?)
3. **Performance** third (is it fast?)

### When to Optimize:
- After feature works correctly
- When user reports slowness
- When handling large datasets (>10GB)
- During Phase 3 (Polish)

### Never:
- Premature optimization
- Sacrifice readability for minor speed gains
- Optimize without measuring first

---

## 🐛 DEBUGGING APPROACH

### When Something Breaks:
1. **Don't panic**: Bugs are normal
2. **Isolate**: What exactly fails?
3. **Reproduce**: Can you make it fail consistently?
4. **Fix**: Smallest change that solves it
5. **Test**: Verify fix works
6. **Document**: Add test to prevent regression

### Debug Logging:
```python
# Add detailed logging for debugging
logger.debug(f"Fetching data for bbox: {bbox}")
logger.debug(f"Using resolution: {resolution}")
logger.debug(f"API endpoint: {url}")
logger.debug(f"Response status: {response.status_code}")
```

---

## 🎯 SUCCESS CRITERIA

### A Task is DONE when:
- ✅ Code works as specified
- ✅ Tests pass
- ✅ Documentation updated
- ✅ User can test it manually
- ✅ Error handling in place
- ✅ Logged appropriately
- ✅ Follows coding standards
- ✅ Marked complete in TASKS.md

---

## 🚨 RED FLAGS (Stop and Ask User)

### Stop immediately and ask if:
1. Task requires paid service not discussed
2. Need to modify core architecture
3. Task will take >4 hours
4. Breaking change to existing features
5. Security concern
6. Legal/licensing issue

---

## 💎 BEST PRACTICES CHECKLIST

Before marking task complete, verify:
- [ ] Code has comments explaining key logic
- [ ] Error handling for common failures
- [ ] Logging for debugging
- [ ] Tests created and passing
- [ ] Documentation updated
- [ ] User-friendly error messages
- [ ] No hardcoded secrets/keys
- [ ] Follows project structure
- [ ] TASKS.md updated
- [ ] CHANGELOG.md updated

---

## 🎸 Remember

**The user cannot code.** Your job is to:
1. Build features they describe
2. Explain everything clearly
3. Test thoroughly
4. Make it bulletproof
5. Guide them every step

**From Earth to Engine - Let's build something amazing! 🌍→🎮**

---

*Last Updated: December 2024*  
*For: RealTerrain Studio Development*  
*Agent: Claude Code (Opus 4 / Sonnet 4.5)*
