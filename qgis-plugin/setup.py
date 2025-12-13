"""
RealTerrain Studio - QGIS Plugin Setup
========================================

This setup.py file makes it easy to install the plugin in development mode.

Installation:
    pip install -e .

This creates a symbolic link so code changes are immediately reflected.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

# Read requirements
requirements_file = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_file.exists():
    with open(requirements_file, 'r', encoding='utf-8') as f:
        requirements = [
            line.strip()
            for line in f
            if line.strip() and not line.startswith('#')
        ]

setup(
    # Basic package information
    name="realterrain-qgis-plugin",
    version="0.1.0",
    description="QGIS plugin for exporting real-world terrain to Unreal Engine 5",
    long_description=long_description,
    long_description_content_type="text/markdown",

    # Author information
    author="RealTerrain Studio",
    author_email="support@realterrainstudio.com",
    url="https://realterrainstudio.com",

    # License
    license="Proprietary",

    # Package discovery
    packages=find_packages(where="src"),
    package_dir={"": "src"},

    # Include non-Python files
    include_package_data=True,
    package_data={
        "realterrain": [
            "*.txt",
            "*.ui",
            "*.qrc",
            "*.png",
            "*.jpg",
            "*.svg",
        ]
    },

    # Dependencies
    install_requires=requirements,

    # Python version requirement
    python_requires=">=3.9",

    # Classifiers
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: GIS",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
    ],

    # Keywords
    keywords="qgis terrain elevation unreal-engine gis srtm osm",

    # Entry points (if needed for command-line tools)
    entry_points={
        "console_scripts": [
            # Add command-line scripts here if needed
            # "realterrain-cli=realterrain.cli:main",
        ],
    },

    # Additional URLs
    project_urls={
        "Documentation": "https://docs.realterrainstudio.com",
        "Source": "https://github.com/yourusername/RealTerrainStudio",
        "Bug Reports": "https://github.com/yourusername/RealTerrainStudio/issues",
    },
)
