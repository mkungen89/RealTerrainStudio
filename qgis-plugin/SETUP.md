# 🚀 QGIS Plugin Setup Instructions

**Step-by-step guide for setting up the RealTerrain Studio QGIS plugin development environment.**

---

## ✅ Prerequisites Check

Before starting, make sure you have:
- ✅ Python 3.9 or higher installed (You have **Python 3.13.7** ✓)
- ✅ Git installed
- ✅ QGIS 3.22+ installed (optional for now, needed later)

---

## 📦 Step 1: Activate Virtual Environment

The virtual environment has already been created for you! Now you just need to activate it.

### On Windows:

Open a terminal in the `qgis-plugin` folder and run:

```bash
# Navigate to the plugin folder
cd C:\RealTerrainStudio\qgis-plugin

# Activate the virtual environment
venv\Scripts\activate
```

**How do you know it worked?**
- Your terminal prompt will change to show `(venv)` at the beginning
- Example: `(venv) C:\RealTerrainStudio\qgis-plugin>`

### On Mac/Linux:

```bash
# Navigate to the plugin folder
cd /path/to/RealTerrainStudio/qgis-plugin

# Activate the virtual environment
source venv/bin/activate
```

---

## 📥 Step 2: Install Dependencies

Once the virtual environment is activated, install the required packages:

### Install Core Dependencies:

```bash
pip install -r requirements.txt
```

This installs:
- HTTP libraries (requests)
- Supabase client
- Security packages (cryptography, JWT)
- Image processing (Pillow)
- Data format handlers (h5py)

**This will take 2-3 minutes.** You'll see packages being downloaded and installed.

### Install Development Dependencies (Optional):

If you want to run tests or contribute to development:

```bash
pip install -r requirements-dev.txt
```

This additionally installs:
- Testing framework (pytest)
- Code formatter (black)
- Linter (flake8)
- Type checker (mypy)
- Documentation tools (sphinx)

---

## 🔧 Step 3: Install Plugin in Development Mode

This creates a link so any code changes are immediately active:

```bash
pip install -e .
```

The `-e` flag means "editable mode" - perfect for development!

---

## ✅ Step 4: Verify Installation

Check that everything installed correctly:

```bash
# Check Python version
python --version

# Check pip version
pip --version

# List installed packages
pip list

# Verify key packages are installed
pip show supabase
pip show requests
pip show Pillow
```

---

## 🎯 Quick Reference Commands

### Activate Environment:
```bash
# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

### Deactivate Environment:
```bash
deactivate
```

### Update Dependencies:
```bash
pip install --upgrade -r requirements.txt
```

### Install New Package:
```bash
pip install package-name
pip freeze > requirements.txt  # Update requirements file
```

---

## 📝 What is a Virtual Environment?

**In simple terms:**
A virtual environment is like a separate, isolated Python installation just for this project.

**Why do we use it?**
- ✅ Keeps this project's packages separate from other Python projects
- ✅ Prevents conflicts between different package versions
- ✅ Makes it easy to install/uninstall packages without affecting your system
- ✅ Allows different projects to use different Python package versions

**Analogy:**
Think of it like having separate toolboxes for different projects. Your woodworking toolbox doesn't mix with your electronics toolbox!

---

## 🐛 Troubleshooting

### Problem: "venv\Scripts\activate" not found
**Solution:**
- Make sure you're in the `qgis-plugin` folder
- Check that the `venv` folder exists: `dir venv` (Windows) or `ls venv` (Mac/Linux)

### Problem: "pip: command not found"
**Solution:**
- Make sure virtual environment is activated (you should see `(venv)` in prompt)
- Try `python -m pip` instead of just `pip`

### Problem: "Permission denied" when activating
**Solution (Windows):**
```powershell
# Run PowerShell as Administrator and execute:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Problem: Package installation fails
**Solution:**
1. Make sure you have internet connection
2. Try upgrading pip first: `python -m pip install --upgrade pip`
3. Try installing packages one at a time
4. Check error messages - they usually explain what's missing

### Problem: "No module named 'supabase'" when running code
**Solution:**
- Make sure virtual environment is activated
- Run `pip install -r requirements.txt` again
- Verify installation: `pip show supabase`

---

## 🎓 Next Steps

After completing this setup:

1. ✅ Virtual environment is ready
2. ✅ Dependencies are installed
3. ✅ Plugin is in development mode

**You're now ready to:**
- Run the plugin code
- Make changes to the code
- Run tests
- Continue to TASK-003: Setup Supabase Project

---

## 🆘 Need Help?

If you get stuck:
1. Check the troubleshooting section above
2. Read the error message carefully (it usually explains the problem!)
3. Check that virtual environment is activated
4. Make sure you're in the correct folder

---

## 📋 Summary Checklist

Before moving to the next task, verify:

- [ ] Virtual environment created (`venv` folder exists)
- [ ] Virtual environment activated (see `(venv)` in terminal)
- [ ] Core dependencies installed (`pip list` shows packages)
- [ ] No error messages during installation
- [ ] Can run `python --version` successfully

**If all boxes are checked, you're ready for TASK-003!** ✨

---

**Created:** 2024-12-08
**Python Version:** 3.13.7
**Platform:** Windows
