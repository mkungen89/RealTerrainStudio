"""
Profile Selection Wizard

Guides users through selecting a game profile for their project.
"""

from qgis.PyQt.QtCore import Qt, pyqtSignal
from qgis.PyQt.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QWidget, QGridLayout, QFrame, QTextEdit
)
from qgis.PyQt.QtGui import QFont

from ..game_profiles import get_all_profiles, get_profiles_by_category, GameProfile


class ProfileCard(QFrame):
    """A clickable card widget for a game profile."""

    clicked = pyqtSignal(str)  # Emits profile ID when clicked

    def __init__(self, profile: GameProfile, parent=None):
        super().__init__(parent)
        self.profile = profile
        self.selected = False

        self.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        self.setLineWidth(2)
        self.setCursor(Qt.PointingHandCursor)
        self.setMinimumHeight(100)
        self.setMaximumHeight(150)

        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)

        # Icon and title
        title_layout = QHBoxLayout()
        icon_label = QLabel(profile.icon)
        icon_font = QFont()
        icon_font.setPointSize(24)
        icon_label.setFont(icon_font)

        title_label = QLabel(profile.name)
        title_font = QFont()
        title_font.setPointSize(11)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setWordWrap(True)

        title_layout.addWidget(icon_label)
        title_layout.addWidget(title_label, 1)
        title_layout.addStretch()

        # Description
        desc_label = QLabel(profile.description)
        desc_label.setWordWrap(True)
        desc_font = QFont()
        desc_font.setPointSize(9)
        desc_label.setFont(desc_font)
        desc_label.setStyleSheet("color: #666;")

        # Examples
        examples_text = "Examples: " + ", ".join(profile.examples[:2])
        examples_label = QLabel(examples_text)
        examples_label.setWordWrap(True)
        examples_font = QFont()
        examples_font.setPointSize(8)
        examples_font.setItalic(True)
        examples_label.setFont(examples_font)
        examples_label.setStyleSheet("color: #888;")

        layout.addLayout(title_layout)
        layout.addWidget(desc_label)
        layout.addWidget(examples_label)
        layout.addStretch()

        self.setLayout(layout)
        self._update_style()

    def mousePressEvent(self, event):
        """Handle click on the card."""
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.profile.id)

    def set_selected(self, selected: bool):
        """Update the visual state of the card."""
        self.selected = selected
        self._update_style()

    def _update_style(self):
        """Update the card styling based on selection state."""
        if self.selected:
            self.setStyleSheet("""
                ProfileCard {
                    background-color: #e3f2fd;
                    border: 2px solid #2196f3;
                    border-radius: 5px;
                }
            """)
        else:
            self.setStyleSheet("""
                ProfileCard {
                    background-color: #ffffff;
                    border: 1px solid #cccccc;
                    border-radius: 5px;
                }
                ProfileCard:hover {
                    background-color: #f5f5f5;
                    border: 1px solid #999999;
                }
            """)


class ProfileWizard(QDialog):
    """Wizard dialog for selecting a game profile."""

    profile_selected = pyqtSignal(str)  # Emits profile ID when user confirms

    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_profile_id = None
        self.profile_cards = {}

        self.setWindowTitle("RealTerrain Studio - Select Your Project Type")
        self.setMinimumSize(900, 700)
        self.setModal(True)

        self._init_ui()

    def _init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Header
        header_label = QLabel("What type of project are you creating?")
        header_font = QFont()
        header_font.setPointSize(16)
        header_font.setBold(True)
        header_label.setFont(header_font)
        header_label.setAlignment(Qt.AlignCenter)

        subtitle_label = QLabel(
            "Choose a profile to automatically configure optimal settings for your project"
        )
        subtitle_font = QFont()
        subtitle_font.setPointSize(10)
        subtitle_label.setFont(subtitle_font)
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_label.setStyleSheet("color: #666;")

        layout.addWidget(header_label)
        layout.addWidget(subtitle_label)
        layout.addSpacing(10)

        # Scrollable profile area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout()
        scroll_layout.setContentsMargins(5, 5, 5, 5)
        scroll_layout.setSpacing(15)

        # Game profiles section
        game_label = QLabel("🎮 GAME PROFILES")
        game_font = QFont()
        game_font.setPointSize(12)
        game_font.setBold(True)
        game_label.setFont(game_font)
        scroll_layout.addWidget(game_label)

        game_grid = self._create_profile_grid("game")
        scroll_layout.addLayout(game_grid)

        scroll_layout.addSpacing(10)

        # Non-game profiles section
        nongame_label = QLabel("🎨 NON-GAME PROFILES")
        nongame_font = QFont()
        nongame_font.setPointSize(12)
        nongame_font.setBold(True)
        nongame_label.setFont(nongame_font)
        scroll_layout.addWidget(nongame_label)

        nongame_grid = self._create_profile_grid("non_game")
        scroll_layout.addLayout(nongame_grid)

        scroll_layout.addStretch()

        scroll_widget.setLayout(scroll_layout)
        scroll_area.setWidget(scroll_widget)

        layout.addWidget(scroll_area, 1)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setMinimumWidth(100)
        self.cancel_button.clicked.connect(self.reject)

        self.next_button = QPushButton("Next")
        self.next_button.setMinimumWidth(100)
        self.next_button.setEnabled(False)
        self.next_button.clicked.connect(self._on_next_clicked)

        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.next_button)

        layout.addLayout(button_layout)

        self.setLayout(layout)

    def _create_profile_grid(self, category: str) -> QGridLayout:
        """Create a grid of profile cards for a category."""
        profiles = get_profiles_by_category(category)

        grid = QGridLayout()
        grid.setSpacing(10)

        cols = 3
        for i, profile in enumerate(profiles):
            row = i // cols
            col = i % cols

            card = ProfileCard(profile)
            card.clicked.connect(self._on_profile_clicked)
            self.profile_cards[profile.id] = card

            grid.addWidget(card, row, col)

        return grid

    def _on_profile_clicked(self, profile_id: str):
        """Handle profile selection."""
        # Deselect all cards
        for card in self.profile_cards.values():
            card.set_selected(False)

        # Select clicked card
        self.profile_cards[profile_id].set_selected(True)
        self.selected_profile_id = profile_id
        self.next_button.setEnabled(True)

    def _on_next_clicked(self):
        """Handle Next button click."""
        if self.selected_profile_id:
            self.profile_selected.emit(self.selected_profile_id)
            self.accept()

    def get_selected_profile(self) -> str:
        """Get the selected profile ID."""
        return self.selected_profile_id
