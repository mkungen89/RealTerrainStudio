"""
License Activation Dialog

UI for license key activation and management.
"""

from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QTextEdit, QFrame, QGroupBox, QTabWidget, QWidget
)
from qgis.PyQt.QtGui import QFont

from ..licensing.license_manager import LicenseManager, LicenseStatus


class LicenseDialog(QDialog):
    """Dialog for license activation and information."""

    def __init__(self, parent=None, show_continue_free=True):
        """
        Initialize the license dialog.

        Args:
            parent: Parent widget
            show_continue_free: If True, shows "Continue with Free" button
        """
        super().__init__(parent)
        self.license_manager = LicenseManager()
        self.show_continue_free = show_continue_free

        self.setWindowTitle("RealTerrain Studio - License Activation")
        self.setMinimumSize(600, 500)
        self.setModal(True)

        self._init_ui()
        self._load_current_status()

    def _init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Header
        header_label = QLabel("License Activation")
        header_font = QFont()
        header_font.setPointSize(16)
        header_font.setBold(True)
        header_label.setFont(header_font)
        header_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(header_label)

        # Tab widget
        self.tab_widget = QTabWidget()

        # Activation tab
        self.activation_tab = self._create_activation_tab()
        self.tab_widget.addTab(self.activation_tab, "Activate")

        # Status tab
        self.status_tab = self._create_status_tab()
        self.tab_widget.addTab(self.status_tab, "License Info")

        layout.addWidget(self.tab_widget)

        # Buttons
        button_layout = QHBoxLayout()

        if self.show_continue_free:
            self.free_button = QPushButton("Continue with Free Version")
            self.free_button.setMinimumWidth(180)
            self.free_button.clicked.connect(self._on_continue_free)
            button_layout.addWidget(self.free_button)

        button_layout.addStretch()

        self.close_button = QPushButton("Close")
        self.close_button.setMinimumWidth(100)
        self.close_button.clicked.connect(self.accept)
        button_layout.addWidget(self.close_button)

        layout.addLayout(button_layout)

        self.setLayout(layout)

    def _create_activation_tab(self) -> QWidget:
        """Create the activation tab."""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Description
        desc_label = QLabel(
            "Enter your license key to unlock Pro features.\n"
            "Don't have a license? You can use the free version with limited features."
        )
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)

        # License key input
        key_group = QGroupBox("License Key")
        key_layout = QVBoxLayout()

        key_input_layout = QHBoxLayout()
        self.license_key_input = QLineEdit()
        self.license_key_input.setPlaceholderText("XXXX-XXXX-XXXX-XXXX")
        self.license_key_input.setMaxLength(19)  # 16 chars + 3 dashes
        key_input_layout.addWidget(self.license_key_input)

        self.activate_button = QPushButton("Activate")
        self.activate_button.setMinimumWidth(100)
        self.activate_button.clicked.connect(self._on_activate)
        key_input_layout.addWidget(self.activate_button)

        key_layout.addLayout(key_input_layout)

        # Status message
        self.activation_status_label = QLabel("")
        self.activation_status_label.setWordWrap(True)
        key_layout.addWidget(self.activation_status_label)

        key_group.setLayout(key_layout)
        layout.addWidget(key_group)

        # Hardware ID display
        hw_group = QGroupBox("Hardware ID")
        hw_layout = QVBoxLayout()

        hw_desc = QLabel(
            "Your Hardware ID is required for license activation. "
            "Copy this ID when purchasing a license."
        )
        hw_desc.setWordWrap(True)
        hw_layout.addWidget(hw_desc)

        hw_id_layout = QHBoxLayout()
        self.hardware_id_label = QLabel(self.license_manager.hardware_id)
        self.hardware_id_label.setStyleSheet(
            "background-color: #f0f0f0; padding: 5px; "
            "font-family: monospace; border: 1px solid #ccc;"
        )
        self.hardware_id_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        hw_id_layout.addWidget(self.hardware_id_label)

        copy_button = QPushButton("Copy")
        copy_button.setMaximumWidth(70)
        copy_button.clicked.connect(self._on_copy_hardware_id)
        hw_id_layout.addWidget(copy_button)

        hw_layout.addLayout(hw_id_layout)

        hw_group.setLayout(hw_layout)
        layout.addWidget(hw_group)

        # Pro features
        features_group = QGroupBox("Pro Features")
        features_layout = QVBoxLayout()

        features_text = QTextEdit()
        features_text.setReadOnly(True)
        features_text.setMaximumHeight(150)
        features_text.setHtml("""
            <ul>
                <li><b>Unlimited area exports</b> - No size restrictions</li>
                <li><b>Unlimited monthly exports</b> - Export as much as you need</li>
                <li><b>Highest resolution</b> - Up to 1m elevation and imagery</li>
                <li><b>All special features</b> - Tactical analysis, fortifications, etc.</li>
                <li><b>Priority support</b> - Fast response times</li>
                <li><b>Commercial use</b> - Use in commercial projects</li>
            </ul>
        """)
        features_layout.addWidget(features_text)

        features_group.setLayout(features_layout)
        layout.addWidget(features_group)

        layout.addStretch()

        widget.setLayout(layout)
        return widget

    def _create_status_tab(self) -> QWidget:
        """Create the license status tab."""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Status display
        status_group = QGroupBox("Current License Status")
        status_layout = QVBoxLayout()

        self.status_text = QTextEdit()
        self.status_text.setReadOnly(True)
        self.status_text.setMaximumHeight(200)

        status_layout.addWidget(self.status_text)

        # Deactivate button
        deactivate_layout = QHBoxLayout()
        deactivate_layout.addStretch()

        self.deactivate_button = QPushButton("Deactivate License")
        self.deactivate_button.setMaximumWidth(150)
        self.deactivate_button.clicked.connect(self._on_deactivate)
        deactivate_layout.addWidget(self.deactivate_button)

        status_layout.addLayout(deactivate_layout)

        status_group.setLayout(status_layout)
        layout.addWidget(status_group)

        # Free tier limits (if applicable)
        limits_group = QGroupBox("Current Limits")
        limits_layout = QVBoxLayout()

        self.limits_text = QTextEdit()
        self.limits_text.setReadOnly(True)
        self.limits_text.setMaximumHeight(150)

        limits_layout.addWidget(self.limits_text)

        limits_group.setLayout(limits_layout)
        layout.addWidget(limits_group)

        # Purchase link
        purchase_group = QGroupBox("Get a License")
        purchase_layout = QVBoxLayout()

        purchase_label = QLabel(
            'Visit <a href="https://realterrainstudio.com/pricing">realterrainstudio.com/pricing</a> '
            'to purchase a Pro license.'
        )
        purchase_label.setOpenExternalLinks(True)
        purchase_label.setWordWrap(True)
        purchase_layout.addWidget(purchase_label)

        purchase_group.setLayout(purchase_layout)
        layout.addWidget(purchase_group)

        layout.addStretch()

        widget.setLayout(layout)
        return widget

    def _load_current_status(self):
        """Load and display current license status."""
        info = self.license_manager.get_license_info()

        # Update status text
        status_html = f"""
            <h3>License Status: {info['tier']}</h3>
            <p>{info['message']}</p>
        """

        if info['status'] == LicenseStatus.PRO:
            status_html += f"""
                <p><b>License Key:</b> {info.get('license_key', 'N/A')}</p>
                <p><b>Activated:</b> {info.get('activated_date', 'N/A')}</p>
                <p><b>Email:</b> {info.get('user_email', 'N/A')}</p>
            """
            self.deactivate_button.setEnabled(True)
        else:
            self.deactivate_button.setEnabled(False)

        status_html += f"""
            <p><b>Hardware ID:</b> {info['hardware_id']}</p>
        """

        self.status_text.setHtml(status_html)

        # Update limits text
        limits = info.get('limits', {})
        limits_html = "<ul>"

        if isinstance(limits.get('max_area_km2'), str):
            limits_html += f"<li><b>Area limit:</b> {limits['max_area_km2']}</li>"
        else:
            limits_html += f"<li><b>Area limit:</b> {limits.get('max_area_km2', 'N/A')} km²</li>"

        if isinstance(limits.get('monthly_exports'), str):
            limits_html += f"<li><b>Monthly exports:</b> {limits['monthly_exports']}</li>"
        else:
            limits_html += f"<li><b>Monthly exports:</b> {limits.get('monthly_exports', 'N/A')}</li>"

        limits_html += f"<li><b>Max resolution:</b> {limits.get('max_resolution_m', 'N/A')}</li>"
        limits_html += "</ul>"

        self.limits_text.setHtml(limits_html)

    def _on_activate(self):
        """Handle activate button click."""
        license_key = self.license_key_input.text().strip()

        if not license_key:
            self.activation_status_label.setText("❌ Please enter a license key")
            self.activation_status_label.setStyleSheet("color: red;")
            return

        # Attempt activation
        success, message = self.license_manager.activate_license(license_key)

        if success:
            self.activation_status_label.setText(f"✅ {message}")
            self.activation_status_label.setStyleSheet("color: green;")
            self.license_key_input.clear()

            # Reload status
            self._load_current_status()

            # Switch to status tab
            self.tab_widget.setCurrentIndex(1)
        else:
            self.activation_status_label.setText(f"❌ {message}")
            self.activation_status_label.setStyleSheet("color: red;")

    def _on_deactivate(self):
        """Handle deactivate button click."""
        from qgis.PyQt.QtWidgets import QMessageBox

        reply = QMessageBox.question(
            self,
            "Deactivate License",
            "Are you sure you want to deactivate your license?\n"
            "You will need to re-enter your license key to reactivate.",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.license_manager.deactivate_license()
            self._load_current_status()
            self.activation_status_label.setText("✅ License deactivated")
            self.activation_status_label.setStyleSheet("color: green;")

    def _on_copy_hardware_id(self):
        """Copy hardware ID to clipboard."""
        from qgis.PyQt.QtWidgets import QApplication

        clipboard = QApplication.clipboard()
        clipboard.setText(self.license_manager.hardware_id)

        self.activation_status_label.setText("✅ Hardware ID copied to clipboard")
        self.activation_status_label.setStyleSheet("color: green;")

    def _on_continue_free(self):
        """Handle continue with free version."""
        self.license_manager.mark_first_run_complete()
        self.accept()
