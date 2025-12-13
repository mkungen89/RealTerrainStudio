"""
Main Export Dialog

The primary user interface for configuring and exporting terrain.
"""

import os
from qgis.PyQt.QtCore import Qt, pyqtSignal
from qgis.PyQt.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QSpinBox, QDoubleSpinBox, QCheckBox, QGroupBox,
    QFileDialog, QTabWidget, QWidget, QTextEdit, QProgressBar,
    QComboBox, QScrollArea, QFrame
)
from qgis.PyQt.QtGui import QFont

from ..game_profiles import get_profile, GameProfile
from .profile_wizard import ProfileWizard
from ..licensing.license_manager import LicenseManager, LicenseStatus


class MainDialog(QDialog):
    """Main dialog for RealTerrain Studio export configuration."""

    export_requested = pyqtSignal(dict)  # Emits export configuration

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_profile = None
        self.profile_config = {}
        self.license_manager = LicenseManager()

        self.setWindowTitle("RealTerrain Studio - Export Terrain")
        self.setMinimumSize(800, 700)

        self._init_ui()

        # Show profile wizard on first use
        self._show_profile_wizard()

    def _init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        # Header with profile info
        self.header_widget = self._create_header()
        layout.addWidget(self.header_widget)

        # Tab widget for different configuration sections
        self.tab_widget = QTabWidget()

        # Area Selection Tab
        self.area_tab = self._create_area_tab()
        self.tab_widget.addTab(self.area_tab, "📍 Area Selection")

        # Data Sources Tab
        self.data_tab = self._create_data_sources_tab()
        self.tab_widget.addTab(self.data_tab, "🗺️ Data Sources")

        # Features Tab
        self.features_tab = self._create_features_tab()
        self.tab_widget.addTab(self.features_tab, "⚙️ Features")

        # Export Tab
        self.export_tab = self._create_export_tab()
        self.tab_widget.addTab(self.export_tab, "📦 Export")

        layout.addWidget(self.tab_widget, 1)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        # Bottom buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.close_button = QPushButton("Close")
        self.close_button.setMinimumWidth(100)
        self.close_button.clicked.connect(self.reject)

        self.export_button = QPushButton("Export Terrain")
        self.export_button.setMinimumWidth(150)
        self.export_button.setStyleSheet("""
            QPushButton {
                background-color: #2196f3;
                color: white;
                font-weight: bold;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #1976d2;
            }
        """)
        self.export_button.clicked.connect(self._on_export_clicked)

        button_layout.addWidget(self.close_button)
        button_layout.addWidget(self.export_button)

        layout.addLayout(button_layout)

        self.setLayout(layout)

    def _create_header(self) -> QWidget:
        """Create the header with profile information."""
        widget = QFrame()
        widget.setFrameStyle(QFrame.StyledPanel)
        widget.setStyleSheet("background-color: #f5f5f5; border-radius: 5px;")

        layout = QHBoxLayout()
        layout.setContentsMargins(15, 10, 15, 10)

        self.profile_icon_label = QLabel("🔧")
        font = QFont()
        font.setPointSize(20)
        self.profile_icon_label.setFont(font)

        info_layout = QVBoxLayout()
        info_layout.setSpacing(2)

        self.profile_name_label = QLabel("No Profile Selected")
        name_font = QFont()
        name_font.setPointSize(12)
        name_font.setBold(True)
        self.profile_name_label.setFont(name_font)

        self.profile_desc_label = QLabel("Select a profile to get started")
        desc_font = QFont()
        desc_font.setPointSize(9)
        self.profile_desc_label.setFont(desc_font)
        self.profile_desc_label.setStyleSheet("color: #666;")

        info_layout.addWidget(self.profile_name_label)
        info_layout.addWidget(self.profile_desc_label)

        # License status
        license_info = self.license_manager.get_license_info()
        self.license_status_label = QLabel(f"License: {license_info['tier']}")
        license_font = QFont()
        license_font.setPointSize(8)
        self.license_status_label.setFont(license_font)

        if license_info['status'] == LicenseStatus.PRO:
            self.license_status_label.setStyleSheet("color: green; font-weight: bold;")
        elif license_info['status'] == LicenseStatus.FREE:
            self.license_status_label.setStyleSheet("color: #666;")
        else:
            self.license_status_label.setStyleSheet("color: red;")

        info_layout.addWidget(self.license_status_label)

        # Buttons
        button_layout = QVBoxLayout()
        button_layout.setSpacing(5)

        self.change_profile_button = QPushButton("Change Profile")
        self.change_profile_button.setMaximumWidth(130)
        self.change_profile_button.clicked.connect(self._show_profile_wizard)
        button_layout.addWidget(self.change_profile_button)

        self.manage_license_button = QPushButton("Manage License")
        self.manage_license_button.setMaximumWidth(130)
        self.manage_license_button.clicked.connect(self._show_license_dialog)
        button_layout.addWidget(self.manage_license_button)

        layout.addWidget(self.profile_icon_label)
        layout.addLayout(info_layout, 1)
        layout.addLayout(button_layout)

        widget.setLayout(layout)
        return widget

    def _create_area_tab(self) -> QWidget:
        """Create the area selection tab."""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)

        # Area input group
        area_group = QGroupBox("Area Selection")
        area_layout = QVBoxLayout()

        desc_label = QLabel(
            "Define the area to export. You can draw a rectangle on the map "
            "or enter coordinates manually."
        )
        desc_label.setWordWrap(True)
        area_layout.addWidget(desc_label)

        # Bounding box inputs
        bbox_layout = QHBoxLayout()

        bbox_layout.addWidget(QLabel("Min Longitude:"))
        self.min_lon_input = QDoubleSpinBox()
        self.min_lon_input.setRange(-180, 180)
        self.min_lon_input.setDecimals(6)
        self.min_lon_input.setValue(-122.5)
        bbox_layout.addWidget(self.min_lon_input)

        bbox_layout.addWidget(QLabel("Min Latitude:"))
        self.min_lat_input = QDoubleSpinBox()
        self.min_lat_input.setRange(-90, 90)
        self.min_lat_input.setDecimals(6)
        self.min_lat_input.setValue(37.7)
        bbox_layout.addWidget(self.min_lat_input)

        area_layout.addLayout(bbox_layout)

        bbox_layout2 = QHBoxLayout()

        bbox_layout2.addWidget(QLabel("Max Longitude:"))
        self.max_lon_input = QDoubleSpinBox()
        self.max_lon_input.setRange(-180, 180)
        self.max_lon_input.setDecimals(6)
        self.max_lon_input.setValue(-122.4)
        bbox_layout2.addWidget(self.max_lon_input)

        bbox_layout2.addWidget(QLabel("Max Latitude:"))
        self.max_lat_input = QDoubleSpinBox()
        self.max_lat_input.setRange(-90, 90)
        self.max_lat_input.setDecimals(6)
        self.max_lat_input.setValue(37.8)
        bbox_layout2.addWidget(self.max_lat_input)

        area_layout.addLayout(bbox_layout2)

        # Draw on map button (TODO: implement)
        draw_button = QPushButton("Draw Rectangle on Map")
        draw_button.clicked.connect(self._on_draw_rectangle)
        area_layout.addWidget(draw_button)

        # Area size display
        self.area_size_label = QLabel("Area: ~0 km²")
        area_layout.addWidget(self.area_size_label)

        area_group.setLayout(area_layout)
        layout.addWidget(area_group)

        layout.addStretch()

        widget.setLayout(layout)
        return widget

    def _create_data_sources_tab(self) -> QWidget:
        """Create the data sources configuration tab."""
        widget = QWidget()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        content = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)

        # Elevation group
        elev_group = QGroupBox("Elevation Data")
        elev_layout = QVBoxLayout()

        self.elevation_enabled_check = QCheckBox("Enable elevation data export")
        self.elevation_enabled_check.setChecked(True)
        elev_layout.addWidget(self.elevation_enabled_check)

        res_layout = QHBoxLayout()
        res_layout.addWidget(QLabel("Resolution (meters):"))
        self.elevation_resolution_spin = QSpinBox()
        self.elevation_resolution_spin.setRange(1, 90)
        self.elevation_resolution_spin.setValue(10)
        res_layout.addWidget(self.elevation_resolution_spin)
        res_layout.addStretch()
        elev_layout.addLayout(res_layout)

        source_layout = QHBoxLayout()
        source_layout.addWidget(QLabel("Source:"))
        self.elevation_source_combo = QComboBox()
        self.elevation_source_combo.addItems(["SRTM", "ASTER", "Best Available"])
        source_layout.addWidget(self.elevation_source_combo)
        source_layout.addStretch()
        elev_layout.addLayout(source_layout)

        elev_group.setLayout(elev_layout)
        layout.addWidget(elev_group)

        # Satellite imagery group
        sat_group = QGroupBox("Satellite Imagery")
        sat_layout = QVBoxLayout()

        self.satellite_enabled_check = QCheckBox("Enable satellite imagery export")
        self.satellite_enabled_check.setChecked(True)
        sat_layout.addWidget(self.satellite_enabled_check)

        sat_res_layout = QHBoxLayout()
        sat_res_layout.addWidget(QLabel("Resolution (meters):"))
        self.satellite_resolution_spin = QSpinBox()
        self.satellite_resolution_spin.setRange(1, 30)
        self.satellite_resolution_spin.setValue(2)
        sat_res_layout.addWidget(self.satellite_resolution_spin)
        sat_res_layout.addStretch()
        sat_layout.addLayout(sat_res_layout)

        self.satellite_recent_check = QCheckBox("Prefer most recent imagery")
        sat_layout.addWidget(self.satellite_recent_check)

        sat_group.setLayout(sat_layout)
        layout.addWidget(sat_group)

        # OSM data group
        osm_group = QGroupBox("OpenStreetMap Data")
        osm_layout = QVBoxLayout()

        self.osm_enabled_check = QCheckBox("Enable OSM data export")
        self.osm_enabled_check.setChecked(True)
        osm_layout.addWidget(self.osm_enabled_check)

        osm_desc = QLabel("Export roads, buildings, and other features:")
        osm_layout.addWidget(osm_desc)

        self.osm_roads_check = QCheckBox("Roads and highways")
        self.osm_roads_check.setChecked(True)
        osm_layout.addWidget(self.osm_roads_check)

        self.osm_buildings_check = QCheckBox("Buildings")
        self.osm_buildings_check.setChecked(True)
        osm_layout.addWidget(self.osm_buildings_check)

        self.osm_water_check = QCheckBox("Water bodies")
        self.osm_water_check.setChecked(True)
        osm_layout.addWidget(self.osm_water_check)

        self.osm_forests_check = QCheckBox("Forests and vegetation")
        osm_layout.addWidget(self.osm_forests_check)

        osm_group.setLayout(osm_layout)
        layout.addWidget(osm_group)

        layout.addStretch()

        content.setLayout(layout)
        scroll.setWidget(content)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)
        widget.setLayout(main_layout)

        return widget

    def _create_features_tab(self) -> QWidget:
        """Create the special features configuration tab."""
        widget = QWidget()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        content = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)

        # Materials
        mat_group = QGroupBox("Material Generation")
        mat_layout = QVBoxLayout()

        self.materials_enabled_check = QCheckBox("Generate material layers")
        self.materials_enabled_check.setChecked(True)
        mat_layout.addWidget(self.materials_enabled_check)

        mat_group.setLayout(mat_layout)
        layout.addWidget(mat_group)

        # Special features (profile-dependent)
        features_group = QGroupBox("Special Features")
        features_layout = QVBoxLayout()

        self.tactical_check = QCheckBox("Tactical analysis (MILSIM)")
        features_layout.addWidget(self.tactical_check)

        self.fortifications_check = QCheckBox("Auto-place fortifications")
        features_layout.addWidget(self.fortifications_check)

        self.cover_check = QCheckBox("Cover & concealment analysis")
        features_layout.addWidget(self.cover_check)

        self.vegetation_check = QCheckBox("Vegetation distribution")
        features_layout.addWidget(self.vegetation_check)

        self.procedural_buildings_check = QCheckBox("Procedural building generation")
        features_layout.addWidget(self.procedural_buildings_check)

        features_group.setLayout(features_layout)
        layout.addWidget(features_group)

        # Tips area
        tips_group = QGroupBox("💡 Tips for Your Profile")
        tips_layout = QVBoxLayout()

        self.tips_text = QTextEdit()
        self.tips_text.setReadOnly(True)
        self.tips_text.setMaximumHeight(150)
        tips_layout.addWidget(self.tips_text)

        tips_group.setLayout(tips_layout)
        layout.addWidget(tips_group)

        layout.addStretch()

        content.setLayout(layout)
        scroll.setWidget(content)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)
        widget.setLayout(main_layout)

        return widget

    def _create_export_tab(self) -> QWidget:
        """Create the export configuration tab."""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)

        # Output group
        output_group = QGroupBox("Output Settings")
        output_layout = QVBoxLayout()

        folder_layout = QHBoxLayout()
        folder_layout.addWidget(QLabel("Output Folder:"))
        self.output_folder_input = QLineEdit()
        self.output_folder_input.setText(os.path.expanduser("~/RealTerrainStudio"))
        folder_layout.addWidget(self.output_folder_input, 1)

        browse_button = QPushButton("Browse...")
        browse_button.clicked.connect(self._on_browse_output)
        folder_layout.addWidget(browse_button)

        output_layout.addLayout(folder_layout)

        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Project Name:"))
        self.project_name_input = QLineEdit()
        self.project_name_input.setText("MyTerrain")
        name_layout.addWidget(self.project_name_input)
        output_layout.addLayout(name_layout)

        output_group.setLayout(output_layout)
        layout.addWidget(output_group)

        # Format group
        format_group = QGroupBox("Export Format")
        format_layout = QVBoxLayout()

        format_layout.addWidget(QLabel("Target Engine:"))
        self.engine_combo = QComboBox()
        self.engine_combo.addItems(["Unreal Engine 5", "Unity (Coming Soon)", "Godot (Coming Soon)"])
        format_layout.addWidget(self.engine_combo)

        format_group.setLayout(format_layout)
        layout.addWidget(format_group)

        layout.addStretch()

        widget.setLayout(layout)
        return widget

    def _show_profile_wizard(self):
        """Show the profile selection wizard."""
        wizard = ProfileWizard(self)
        wizard.profile_selected.connect(self._on_profile_selected)

        if wizard.exec_() == QDialog.Accepted:
            profile_id = wizard.get_selected_profile()
            if profile_id:
                self._apply_profile(profile_id)

    def _on_profile_selected(self, profile_id: str):
        """Handle profile selection from wizard."""
        self._apply_profile(profile_id)

    def _apply_profile(self, profile_id: str):
        """Apply a game profile to the UI."""
        profile = get_profile(profile_id)
        self.current_profile = profile

        # Update header
        self.profile_icon_label.setText(profile.icon)
        self.profile_name_label.setText(profile.name)
        self.profile_desc_label.setText(profile.description)

        # Apply data source settings
        self.elevation_enabled_check.setChecked(profile.elevation_enabled)
        self.elevation_resolution_spin.setValue(profile.elevation_resolution)

        self.satellite_enabled_check.setChecked(profile.satellite_enabled)
        self.satellite_resolution_spin.setValue(profile.satellite_resolution)
        self.satellite_recent_check.setChecked(profile.satellite_prefer_recent)

        self.osm_enabled_check.setChecked(profile.osm_enabled)
        self.osm_roads_check.setChecked("roads" in profile.osm_features)
        self.osm_buildings_check.setChecked("buildings" in profile.osm_features)
        self.osm_water_check.setChecked("water" in profile.osm_features)
        self.osm_forests_check.setChecked("forests" in profile.osm_features)

        # Apply feature settings
        self.materials_enabled_check.setChecked(profile.materials_enabled)
        self.tactical_check.setChecked(profile.tactical_analysis)
        self.fortifications_check.setChecked(profile.fortifications_enabled)
        self.cover_check.setChecked(profile.cover_analysis)
        self.vegetation_check.setChecked(profile.vegetation_distribution)
        self.procedural_buildings_check.setChecked(profile.procedural_buildings_enabled)

        # Update tips
        tips_html = "<ul>"
        for tip in profile.tips:
            tips_html += f"<li>{tip}</li>"
        tips_html += "</ul>"
        self.tips_text.setHtml(tips_html)

    def _on_draw_rectangle(self):
        """Handle draw rectangle button (TODO: implement)."""
        from qgis.core import Qgis
        from qgis.utils import iface

        iface.messageBar().pushMessage(
            "Info",
            "Draw rectangle feature coming soon! Please enter coordinates manually.",
            level=Qgis.Info,
            duration=3
        )

    def _on_browse_output(self):
        """Handle browse button for output folder."""
        folder = QFileDialog.getExistingDirectory(
            self,
            "Select Output Folder",
            self.output_folder_input.text()
        )
        if folder:
            self.output_folder_input.setText(folder)

    def _show_license_dialog(self):
        """Show the license management dialog."""
        from .license_dialog import LicenseDialog

        dialog = LicenseDialog(self, show_continue_free=False)
        dialog.exec_()

        # Refresh license status after dialog closes
        license_info = self.license_manager.get_license_info()
        self.license_status_label.setText(f"License: {license_info['tier']}")

        if license_info['status'] == LicenseStatus.PRO:
            self.license_status_label.setStyleSheet("color: green; font-weight: bold;")
        elif license_info['status'] == LicenseStatus.FREE:
            self.license_status_label.setStyleSheet("color: #666;")
        else:
            self.license_status_label.setStyleSheet("color: red;")

    def _on_export_clicked(self):
        """Handle export button click."""
        # Calculate area size (rough approximation)
        min_lon = self.min_lon_input.value()
        min_lat = self.min_lat_input.value()
        max_lon = self.max_lon_input.value()
        max_lat = self.max_lat_input.value()

        # Rough calculation: 1 degree = ~111km at equator
        width_km = abs(max_lon - min_lon) * 111 * abs((max_lat + min_lat) / 2)
        height_km = abs(max_lat - min_lat) * 111
        area_km2 = width_km * height_km

        # Check if export is allowed based on license
        allowed, message = self.license_manager.check_export_allowed(area_km2)

        if not allowed:
            from qgis.core import Qgis
            from qgis.utils import iface

            iface.messageBar().pushMessage(
                "License Restriction",
                message,
                level=Qgis.Warning,
                duration=5
            )
            return

        # Collect configuration
        config = {
            "profile": self.current_profile.id if self.current_profile else "custom",
            "area": {
                "min_lon": self.min_lon_input.value(),
                "min_lat": self.min_lat_input.value(),
                "max_lon": self.max_lon_input.value(),
                "max_lat": self.max_lat_input.value(),
            },
            "elevation": {
                "enabled": self.elevation_enabled_check.isChecked(),
                "resolution": self.elevation_resolution_spin.value(),
                "source": self.elevation_source_combo.currentText(),
            },
            "satellite": {
                "enabled": self.satellite_enabled_check.isChecked(),
                "resolution": self.satellite_resolution_spin.value(),
                "prefer_recent": self.satellite_recent_check.isChecked(),
            },
            "osm": {
                "enabled": self.osm_enabled_check.isChecked(),
                "roads": self.osm_roads_check.isChecked(),
                "buildings": self.osm_buildings_check.isChecked(),
                "water": self.osm_water_check.isChecked(),
                "forests": self.osm_forests_check.isChecked(),
            },
            "features": {
                "materials": self.materials_enabled_check.isChecked(),
                "tactical": self.tactical_check.isChecked(),
                "fortifications": self.fortifications_check.isChecked(),
                "cover": self.cover_check.isChecked(),
                "vegetation": self.vegetation_check.isChecked(),
                "procedural_buildings": self.procedural_buildings_check.isChecked(),
            },
            "output": {
                "folder": self.output_folder_input.text(),
                "project_name": self.project_name_input.text(),
                "engine": self.engine_combo.currentText(),
            },
        }

        self.export_requested.emit(config)

        # Show progress (for now just a message)
        from qgis.core import Qgis
        from qgis.utils import iface

        iface.messageBar().pushMessage(
            "Export",
            f"Export started for profile: {config['profile']}. Data export functionality coming in next tasks!",
            level=Qgis.Info,
            duration=5
        )
