"""
RealTerrain Studio - QGIS Plugin
=================================

This is the main entry point for the QGIS plugin.

Author: RealTerrain Studio
License: Proprietary
Python Version: 3.9+
QGIS Version: 3.22+
"""

# Plugin metadata - QGIS reads this
def classFactory(iface):
    """
    Load RealTerrainPlugin class from plugin.py

    This function is required by QGIS to initialize the plugin.

    Args:
        iface: QgisInterface - QGIS interface object

    Returns:
        RealTerrainPlugin: Instance of the plugin
    """
    from .plugin import RealTerrainPlugin
    return RealTerrainPlugin(iface)
