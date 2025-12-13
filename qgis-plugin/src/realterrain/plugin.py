"""
RealTerrain Studio - Main Plugin Class

This file contains the main plugin class that QGIS loads.
It handles:
- Plugin initialization and cleanup
- Adding toolbar buttons and menus
- Opening the main dialog
- Managing plugin lifecycle

Author: RealTerrain Studio
"""

from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction
from qgis.core import QgsMessageLog, Qgis

import os.path


class RealTerrainPlugin:
    """
    QGIS Plugin Implementation for RealTerrain Studio.

    This class manages the plugin lifecycle within QGIS.
    """

    def __init__(self, iface):
        """
        Initialize the plugin.

        Args:
            iface (QgisInterface): A QGIS interface instance.
        """
        # Save reference to the QGIS interface
        self.iface = iface

        # Initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)

        # Declare instance attributes
        self.actions = []
        self.menu = '&RealTerrain Studio'
        self.toolbar = None

        # Will be set when plugin is loaded
        self.pluginIsActive = False
        self.dockwidget = None

        # Initialize license manager
        from .licensing.license_manager import LicenseManager
        self.license_manager = LicenseManager()

        # Log that plugin initialized
        QgsMessageLog.logMessage(
            'RealTerrain Studio Plugin Initialized',
            'RealTerrain',
            Qgis.Info
        )

    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None
    ):
        """
        Add a toolbar icon to the toolbar.

        Args:
            icon_path (str): Path to the icon for this action
            text (str): Text that should be shown in menu items
            callback (function): Function to be called when action is triggered
            enabled_flag (bool): Whether the action should be enabled by default
            add_to_menu (bool): Should this action be added to the menu?
            add_to_toolbar (bool): Should this action be added to the toolbar?
            status_tip (str): Optional text to show in status bar
            whats_this (str): Optional "What's This?" text
            parent: Parent widget for the new action

        Returns:
            QAction: The action that was created
        """
        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            # Adds plugin icon to Plugins toolbar
            self.iface.addToolBarIcon(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action
            )

        self.actions.append(action)

        return action

    def initGui(self):
        """
        Create the menu entries and toolbar icons inside the QGIS GUI.

        This is called by QGIS when the plugin is loaded.
        """
        icon_path = os.path.join(self.plugin_dir, 'icon.png')

        # Add toolbar button and menu item
        self.add_action(
            icon_path,
            text='Export Terrain to UE5',
            callback=self.run,
            parent=self.iface.mainWindow(),
            status_tip='Export real-world terrain to Unreal Engine 5',
            whats_this='Open RealTerrain Studio export dialog'
        )

        # Add license management menu item
        self.add_action(
            icon_path,
            text='Manage License',
            callback=self.show_license_dialog,
            parent=self.iface.mainWindow(),
            add_to_toolbar=False,
            status_tip='Manage your RealTerrain Studio license',
            whats_this='Open license management dialog'
        )

        QgsMessageLog.logMessage(
            'RealTerrain Studio GUI Initialized',
            'RealTerrain',
            Qgis.Info
        )

        # Show license dialog on first run
        if self.license_manager.is_first_run():
            self._show_first_run_license_dialog()

    def unload(self):
        """
        Remove the plugin menu item and icon from QGIS GUI.

        This is called by QGIS when the plugin is unloaded.
        """
        # Remove the plugin menu item and icon
        for action in self.actions:
            self.iface.removePluginMenu(
                '&RealTerrain Studio',
                action
            )
            self.iface.removeToolBarIcon(action)

        QgsMessageLog.logMessage(
            'RealTerrain Studio Unloaded',
            'RealTerrain',
            Qgis.Info
        )

    def show_license_dialog(self):
        """Show the license management dialog."""
        from .ui.license_dialog import LicenseDialog

        dialog = LicenseDialog(self.iface.mainWindow(), show_continue_free=False)
        dialog.exec_()

    def _show_first_run_license_dialog(self):
        """Show license dialog on first run."""
        from .ui.license_dialog import LicenseDialog

        QgsMessageLog.logMessage(
            'First run detected - showing license dialog',
            'RealTerrain',
            Qgis.Info
        )

        dialog = LicenseDialog(self.iface.mainWindow(), show_continue_free=True)
        dialog.exec_()

    def run(self):
        """
        Run method that performs all the real work.

        This is called when the user clicks the toolbar button or menu item.
        """
        # Import and show the main dialog
        from .ui.main_dialog import MainDialog

        dialog = MainDialog(self.iface.mainWindow())
        dialog.export_requested.connect(self._on_export_requested)

        QgsMessageLog.logMessage(
            'RealTerrain Studio Dialog Opening',
            'RealTerrain',
            Qgis.Info
        )

        dialog.exec_()

    def _on_export_requested(self, config):
        """
        Handle export request from the dialog.

        Args:
            config (dict): Export configuration from the dialog
        """
        QgsMessageLog.logMessage(
            f'Export requested with config: {config}',
            'RealTerrain',
            Qgis.Info
        )

        # TODO: Implement actual export logic in future tasks
        self.iface.messageBar().pushMessage(
            'RealTerrain Studio',
            f'Export configured! Profile: {config["profile"]}. Export functionality coming in next tasks.',
            level=Qgis.Success,
            duration=5
        )
