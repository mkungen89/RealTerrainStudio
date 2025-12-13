# 🌍 RealTerrain Studio - Day 1 Complete Setup Guide
## "From Earth to Engine"

**Welcome!** This is your complete guide to start building RealTerrain Studio TODAY!

---

## 📋 **WHAT YOU'RE BUILDING**

**RealTerrain Studio** - The ultimate terrain creation pipeline:
- **QGIS Plugin** (Python) → Exports real-world geodata
- **UE5 Plugin** (C++) → Imports everything automatically
- **Single .rterrain file** → One file contains everything
- **13 Game Profiles** → One-click configuration
- **Hardware Validation** → Prevents crashes before they happen

---

## ✅ **PREREQUISITES (Install These First)**

### 1. **Claude Pro** ($20/month) ⭐ REQUIRED
```
Visit: https://claude.ai
Click: "Upgrade to Pro"
Pay: $20/month

Why needed:
- Claude Code access (builds everything for you!)
- Opus 4 + Sonnet 4.5 (best AI models)
- High message limits
```

### 2. **VS Code** (Free)
```
Download: https://code.visualstudio.com/
Install: Standard installation

Extensions to install:
- Python (Microsoft)
- Pylance (Microsoft)
- C/C++ (Microsoft)
- GitLens (Optional but recommended)
```

### 3. **Python 3.9+** (Free)
```
Download: https://www.python.org/downloads/
Install: Check "Add Python to PATH"

Verify:
python --version
(Should show: Python 3.9 or higher)
```

### 4. **Git** (Free)
```
Download: https://git-scm.com/
Install: Standard installation

Verify:
git --version
```

### 5. **QGIS 3.22+** (Free)
```
Download: https://qgis.org/
Install: Long Term Release (LTR) version

Why: This is where you'll develop and test the plugin
```

### 6. **Unreal Engine 5.3+** (Free)
```
Install Epic Games Launcher
Download UE5.3 or later

Why: This is where terrain will be imported
Note: Large download (~50 GB), can do later
```

---

## 🚀 **DAY 1 - SETUP (TODAY!)**

### **Step 1: Install Claude Code** (5 minutes)

**On Windows (PowerShell as Admin):**
```powershell
irm https://cli.claude.ai/install.ps1 | iex
```

**On Mac/Linux:**
```bash
curl -fsSL https://cli.claude.ai/install.sh | sh
```

**Verify installation:**
```bash
claude-code --version
```

**Authenticate:**
```bash
claude-code auth
```
(Opens browser, log in with Claude Pro account)

---

### **Step 2: Create Project Structure** (2 minutes)

**Create project folder:**
```bash
# Choose a location (e.g., C:/Projects/ or ~/Projects/)
cd C:/Projects/  # Windows
# OR
cd ~/Projects/   # Mac/Linux

# Create project
mkdir RealTerrainStudio
cd RealTerrainStudio

# Open in VS Code
code .
```

**In VS Code terminal (Ctrl + `):**
```bash
# Verify you're in the right place
pwd
# Should show: .../RealTerrainStudio
```

---

### **Step 3: Initialize Git** (1 minute)

```bash
git init
git config user.name "Your Name"
git config user.email "your.email@example.com"
```

**Create .gitignore:**
```bash
# In VS Code, create new file: .gitignore
# Add this content:
```

```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/

# QGIS
*.qgs~
*.qgz~

# UE5
Binaries/
DerivedDataCache/
Intermediate/
Saved/
*.sln
*.suo

# IDEs
.vscode/
.idea/

# OS
.DS_Store
Thumbs.db

# RealTerrain specific
exports/
*.rterrain
test_data/
```

---

### **Step 4: Start Claude Code** (NOW!)

**In VS Code terminal:**
```bash
claude-code
```

**You'll see:**
```
Claude Code v1.0.0
Connected to Claude Pro
Model: claude-sonnet-4.5

What would you like to build?
>
```

---

## 🎯 **YOUR FIRST PROMPT TO CLAUDE CODE**

**Copy and paste this EXACTLY:**

```
I'm building RealTerrain Studio - a terrain creation pipeline from QGIS to Unreal Engine 5.

PROJECT CONTEXT:
- I cannot code myself, so guide me step-by-step
- Read AGENT_RULES.md for development guidelines
- Read TASKS.md for the complete task list
- We're starting with TASK-001: Initialize Project Structure

FIRST TASK:
Create the complete folder structure for RealTerrain Studio with these components:
1. QGIS plugin (Python)
2. UE5 plugin (C++)
3. Supabase backend
4. Website (Next.js)
5. Documentation
6. All necessary config files

Requirements:
- Follow the structure defined in TASKS.md
- Create README.md files in each major folder
- Add .gitignore for each component
- Create placeholder files where needed
- Explain what you're creating as you go

Start now with TASK-001.
```

---

## 📁 **WHAT CLAUDE CODE WILL CREATE**

Claude will build this structure:

```
RealTerrainStudio/
├── README.md                    ← Project overview
├── CHANGELOG.md                 ← Version history
├── LICENSE                      ← Software license
├── .gitignore                   ← Git ignore rules
│
├── qgis-plugin/                 ← QGIS Plugin (Python)
│   ├── realterrain_studio/
│   │   ├── __init__.py
│   │   ├── metadata.txt
│   │   ├── icon.png
│   │   ├── core/                ← Core functionality
│   │   ├── pro/                 ← Pro features
│   │   ├── licensing/           ← License system
│   │   ├── ui/                  ← User interface
│   │   ├── utils/               ← Utilities
│   │   └── tests/               ← Unit tests
│   ├── requirements.txt
│   ├── setup.py
│   └── README.md
│
├── ue5-plugin/                  ← UE5 Plugin (C++)
│   ├── RealTerrainStudio/
│   │   ├── RealTerrainStudio.uplugin
│   │   ├── Source/
│   │   │   ├── RealTerrainStudio/      ← Runtime
│   │   │   ├── RealTerrainStudioEditor/ ← Editor
│   │   │   └── RealTerrainStudioPro/   ← Pro features
│   │   ├── Content/
│   │   │   ├── Materials/
│   │   │   ├── Blueprints/
│   │   │   └── UI/
│   │   ├── Resources/
│   │   └── Config/
│   └── README.md
│
├── backend/                     ← Supabase Backend
│   ├── supabase/
│   │   ├── config.toml
│   │   ├── migrations/          ← SQL schema
│   │   │   ├── 00001_initial_schema.sql
│   │   │   ├── 00002_licenses.sql
│   │   │   ├── 00003_hardware_activations.sql
│   │   │   └── ...
│   │   └── functions/           ← Edge functions
│   │       ├── validate_license/
│   │       ├── activate_license/
│   │       └── stripe_webhook/
│   └── README.md
│
├── website/                     ← Marketing Website
│   ├── public/
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.tsx         ← Landing page
│   │   │   ├── pricing/
│   │   │   ├── docs/
│   │   │   ├── download/
│   │   │   └── dashboard/
│   │   ├── components/
│   │   └── lib/
│   ├── package.json
│   └── README.md
│
├── docs/                        ← Documentation
│   ├── user-guide/
│   │   ├── getting-started.md
│   │   ├── qgis-plugin/
│   │   └── ue5-plugin/
│   ├── api/
│   │   └── rterrain-format.md
│   ├── tutorials/
│   └── development/
│
└── tests/                       ← Integration tests
    ├── integration/
    ├── e2e/
    └── performance/
```

---

## ⏱️ **TIMELINE FOR TODAY**

```
Hour 1: Setup & Installation
├─ Install Claude Pro ✓
├─ Install VS Code ✓
├─ Install Python ✓
├─ Install Claude Code ✓
└─ Create project folder ✓

Hour 2: Project Structure
├─ Start Claude Code
├─ TASK-001: Create folder structure
├─ Review what Claude created
└─ First git commit

Hour 3: QGIS Plugin Skeleton
├─ TASK-101: Create plugin skeleton
├─ Test loading in QGIS
└─ "Hello World" popup

Hour 4: Review & Plan
├─ Understand what was built
├─ Review TASKS.md
├─ Plan tomorrow's work
└─ Celebrate! 🎉

Total: 4 hours to working plugin skeleton!
```

---

## 🎯 **AFTER EACH TASK**

Claude Code will:
1. ✅ Create all files
2. ✅ Explain what was created
3. ✅ Show you how to test
4. ✅ Mark task as DONE in TASKS.md
5. ✅ Update CHANGELOG.md

**Your job:**
1. 👀 Read Claude's explanation
2. 🧪 Test what was built (Claude gives instructions)
3. ✅ Approve if it works
4. 📝 Ask questions if confused
5. ➡️ Move to next task

---

## 🧪 **TESTING YOUR FIRST PLUGIN**

After TASK-101 is complete, test it:

**Step 1: Copy plugin to QGIS**
```bash
# Windows
cp -r qgis-plugin/realterrain_studio "C:/Users/YourName/AppData/Roaming/QGIS/QGIS3/profiles/default/python/plugins/"

# Mac
cp -r qgis-plugin/realterrain_studio "~/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/"

# Linux
cp -r qgis-plugin/realterrain_studio "~/.local/share/QGIS/QGIS3/profiles/default/python/plugins/"
```

**Step 2: Open QGIS**
```
1. Launch QGIS
2. Go to: Plugins → Manage and Install Plugins
3. Click: "Installed" tab
4. Find: "RealTerrain Studio"
5. Check the checkbox to enable
6. Look in menu bar: You should see "Plugins → RealTerrain Studio"
7. Click it!
```

**Expected result:**
```
A dialog appears saying:
"RealTerrain Studio - From Earth to Engine
Welcome! Plugin loaded successfully!"

[OK]
```

**✅ If you see this = SUCCESS!**

---

## 💡 **TIPS FOR WORKING WITH CLAUDE CODE**

### **1. Be Specific**
```
❌ Bad: "Make it better"
✅ Good: "Add error handling for network failures"
```

### **2. One Task at a Time**
```
❌ Bad: "Build the whole plugin now"
✅ Good: "Complete TASK-101: Create plugin skeleton"
```

### **3. Ask Questions**
```
If confused:
"Explain what this file does in simple terms"
"How do I test this feature?"
"What does this error mean?"
```

### **4. Use Opus for Complex Tasks**
```
When starting a new major feature:
"Use Opus 4 for this task: Create terrain export system"

For simple fixes:
"Use Sonnet 4.5 for this: Fix typo in README"
```

### **5. Review Before Moving On**
```
After each task:
1. Read what Claude built
2. Test it yourself
3. Understand it (ask if not clear)
4. Then move to next task
```

---

## 🐛 **TROUBLESHOOTING**

### **Problem: Claude Code won't start**
```
Solution:
1. Check Claude Pro subscription is active
2. Re-authenticate: claude-code auth
3. Restart terminal
4. Try again
```

### **Problem: Python version wrong**
```
Check version:
python --version

If wrong:
- Windows: Reinstall Python, check "Add to PATH"
- Mac: Use brew install python@3.9
- Linux: Use pyenv to manage versions
```

### **Problem: QGIS won't load plugin**
```
Check:
1. Plugin copied to correct folder
2. __init__.py exists
3. metadata.txt has correct info
4. QGIS version is 3.22+
5. Python errors in QGIS log (View → Panels → Log Messages)
```

### **Problem: Git not working**
```
Verify installation:
git --version

Configure:
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
```

---

## 📚 **RESOURCES**

### **Documentation**
- AGENT_RULES.md - How Claude should code
- TASKS.md - All 80 tasks
- Your project's docs/ folder

### **QGIS Development**
- https://docs.qgis.org/
- https://plugins.qgis.org/

### **UE5 Development**
- https://docs.unrealengine.com/
- https://dev.epicgames.com/

### **Supabase**
- https://supabase.com/docs

### **Get Help**
- Ask Claude Code (it knows everything!)
- QGIS forums
- Unreal Engine forums

---

## 🎯 **SUCCESS CRITERIA FOR DAY 1**

By end of today, you should have:

✅ Claude Pro subscription active
✅ VS Code installed and working
✅ Claude Code authenticated
✅ Project folder created
✅ Git initialized
✅ TASK-001 complete (folder structure)
✅ TASK-101 complete (plugin skeleton)
✅ Plugin loads in QGIS
✅ "Hello World" dialog appears

**If you have all these = PERFECT START!** 🎉

---

## ➡️ **WHAT'S NEXT (DAY 2)**

Tomorrow you'll build:
- TASK-102: Main UI with Game Profile wizard
- TASK-103: License activation dialog
- Test the complete UI flow

**Estimated time:** 4-6 hours

---

## 🎉 **YOU'RE READY!**

**Open VS Code terminal and type:**
```bash
claude-code
```

**Then paste the first prompt above and START BUILDING!**

Remember:
- Claude Code does ALL the coding
- You just guide it with tasks
- Test everything it builds
- Ask questions when confused
- Have fun! 🚀

**From Earth to Engine - Let's make it happen!** 🌍→🎮

---

*Last Updated: December 2024*  
*RealTerrain Studio - Day 1 Guide*  
*Total estimated time: 4 hours*