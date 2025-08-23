from PySide6.QtWidgets import (QApplication, QSystemTrayIcon, QMenu, QMessageBox, QFileDialog,
                               QDialog, QVBoxLayout, QFormLayout, QLineEdit, QPushButton,
                               QHBoxLayout, QTextEdit, QCheckBox, QWidget,
                               QSizePolicy, QSpacerItem)
from PySide6.QtGui import QAction, QIcon, QPixmap, QColor, QPalette, QPainter, QPen, QShowEvent
from PySide6.QtCore import QTimer, Qt
import toml, subprocess
import os, sys

from src.config import save_config, CONFIG_PATH


class AddRuleDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Sanitization Rule")
        self.setFixedSize(400, 380)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.WindowCloseButtonHint)

        # Ensure we inherit the current application palette
        app = QApplication.instance()
        if app and isinstance(app, QApplication):
            palette = app.palette()
            self.setPalette(palette)

        self.setup_ui()
        # Apply theme (which includes stylesheet)
        self.update_theme()

    def apply_stylesheet(self):
        """Apply the themed stylesheet to the dialog using actual palette colors."""
        app = QApplication.instance()
        if not app or not isinstance(app, QApplication):
            return

        # Get current palette and extract actual color values
        palette = app.palette()
        window_color = palette.color(QPalette.ColorRole.Window).name()
        windowtext_color = palette.color(QPalette.ColorRole.WindowText).name()
        base_color = palette.color(QPalette.ColorRole.Base).name()
        text_color = palette.color(QPalette.ColorRole.Text).name()
        mid_color = palette.color(QPalette.ColorRole.Mid).name()
        button_color = palette.color(QPalette.ColorRole.Button).name()
        buttontext_color = palette.color(QPalette.ColorRole.ButtonText).name()
        highlight_color = palette.color(QPalette.ColorRole.Highlight).name()
        highlightedtext_color = palette.color(QPalette.ColorRole.HighlightedText).name()

        # Generate CSS with actual color values instead of palette() references
        css = f"""
            QDialog {{
                background-color: {window_color};
            }}
            QLabel {{
                font: -apple-system;
                color: {windowtext_color};
            }}
            QLineEdit {{
                font: -apple-system;
                padding: 6px 8px;
                border: 1px solid {mid_color};
                border-radius: 4px;
                background-color: {base_color};
                color: {text_color};
                min-height: 18px;
            }}
            QLineEdit:focus {{
                border: 2px solid {highlight_color};
                outline: none;
            }}
            QComboBox {{
                font: -apple-system;
                padding: 6px 8px;
                padding-right: 25px;
                border: 1px solid {mid_color};
                border-radius: 4px;
                background-color: {base_color};
                color: {text_color};
                min-height: 18px;
            }}
            QComboBox:focus {{
                border: 2px solid {highlight_color};
                outline: none;
            }}
            QComboBox::drop-down {{
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
                border-left: 1px solid {mid_color};
                border-top-right-radius: 4px;
                border-bottom-right-radius: 4px;
                background-color: {button_color};
            }}
            QComboBox::down-arrow {{
                image: none;
                border: 3px solid transparent;
                border-top: 4px solid {text_color};
                margin-right: 3px;
            }}
            QComboBox QAbstractItemView {{
                border: 1px solid {mid_color};
                border-radius: 6px;
                background-color: {base_color};
                selection-background-color: {highlight_color};
                selection-color: {highlightedtext_color};
                outline: none;
                padding: 4px;
                font-size: 13px;
                min-width: 150px;
            }}
            QComboBox QAbstractItemView::item {{
                padding: 8px 12px;
                margin: 1px;
                border-radius: 4px;
                min-height: 18px;
            }}
            QComboBox QAbstractItemView::item:selected {{
                background-color: {highlight_color};
                color: {highlightedtext_color};
            }}
            QComboBox QAbstractItemView::item:hover {{
                background-color: {highlight_color};
                color: {highlightedtext_color};
            }}
            QTextEdit {{
                font: -apple-system;
                padding: 6px;
                border: 1px solid {mid_color};
                border-radius: 4px;
                background-color: {base_color};
                color: {text_color};
            }}
            QTextEdit:focus {{
                border: 2px solid {highlight_color};
                outline: none;
            }}
            QPushButton {{
                font: -apple-system;
                padding: 8px 16px;
                border-radius: 6px;
                min-width: 70px;
            }}
            QPushButton#primary {{
                background-color: {highlight_color};
                color: {highlightedtext_color};
                border: none;
            }}
            QPushButton#secondary {{
                background-color: {button_color};
                color: {buttontext_color};
                border: 1px solid {mid_color};
            }}
            QCheckBox {{
                font: -apple-system;
                color: {windowtext_color};
            }}
        """

        self.setStyleSheet(css)

    def update_theme(self):
        """Update the dialog's appearance based on current system theme."""
        # Force the dialog to use the current application palette
        app = QApplication.instance()
        if app and isinstance(app, QApplication):
            palette = app.palette()
            self.setPalette(palette)
            # Process events to ensure palette is applied
            app.processEvents()

        # Clear existing stylesheet completely and force style recalculation
        self.setStyleSheet("")
        self.style().unpolish(self)
        self.apply_stylesheet()
        self.style().polish(self)

        # Force complete visual update
        self.repaint()
        self.update()

        # Also update all child widgets to ensure they get new colors
        for child in self.findChildren(QWidget):
            child.repaint()
            child.update()

        # Process all pending events to ensure changes are visible
        if app and isinstance(app, QApplication):
            app.processEvents()


    def showEvent(self, event: QShowEvent):
        """Override showEvent to ensure dialog always reflects current theme when shown."""
        self.update_theme()
        super().showEvent(event)

    def setup_ui(self):
        """Set up the dialog's user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)


        form_layout = QFormLayout()
        form_layout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)
        form_layout.setRowWrapPolicy(QFormLayout.RowWrapPolicy.DontWrapRows)
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        form_layout.setVerticalSpacing(12)
        form_layout.setHorizontalSpacing(10)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter a descriptive name")
        form_layout.addRow("Rule Name:", self.name_input)


        self.pattern_input = QTextEdit()
        self.pattern_input.setPlaceholderText("Enter text or regex pattern to match (e.g., email@domain.com or \\d{3}-\\d{2}-\\d{4})")
        self.pattern_input.setMaximumHeight(80)
        self.pattern_input.setMinimumHeight(80)
        form_layout.addRow("Pattern:", self.pattern_input)


        self.placeholder_input = QLineEdit()
        self.placeholder_input.setText("[REDACTED]")
        self.placeholder_input.setPlaceholderText("Text to replace matches with (e.g., [EMAIL], [PHONE])")
        form_layout.addRow("Replace with:", self.placeholder_input)

        layout.addLayout(form_layout)

        self.enabled_checkbox = QCheckBox("Enable this rule immediately")
        self.enabled_checkbox.setChecked(True)
        layout.addWidget(self.enabled_checkbox)


        layout.addItem(QSpacerItem(0, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))


        button_layout = QHBoxLayout()
        button_layout.setSpacing(12)

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setObjectName("secondary")
        self.cancel_btn.clicked.connect(self.reject)

        self.save_btn = QPushButton("Add Rule")
        self.save_btn.setObjectName("primary")
        self.save_btn.clicked.connect(self.accept)
        self.save_btn.setDefault(True)

        button_layout.addWidget(self.cancel_btn)
        button_layout.addItem(QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        button_layout.addWidget(self.save_btn)
        layout.addLayout(button_layout)



    def get_rule(self):
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Input Error", "Rule name cannot be empty.")
            return None

        pattern = self.pattern_input.toPlainText().strip()
        if not pattern:
            QMessageBox.warning(self, "Input Error", "Please enter a pattern to match.")
            return None

        placeholder = self.placeholder_input.text().strip() or "[REDACTED]"
        enabled = self.enabled_checkbox.isChecked()

        return {"name": name, "pattern": pattern, "placeholder": placeholder, "enabled": enabled}



class TrayApp:
    def __init__(self, config: dict, sanitizer):
        self.config = config
        self.sanitizer = sanitizer
        self.clipboard = QApplication.clipboard()
        self.last_text = ""
        self.enabled = self.config.get("enabled", True)


        self.current_dark_mode = self.is_dark_mode()

        self.tray = QSystemTrayIcon()
        self.update_tray_icon()


        self.theme_check_timer = QTimer()
        self.theme_check_timer.timeout.connect(self.check_theme_change)
        self.theme_check_timer.start(1000)
        self.menu = QMenu()
        self.tray.setContextMenu(self.menu)

        self.action_enable = QAction("Enabled", checkable=True, checked=self.enabled)
        self.action_enable.triggered.connect(self.toggle_enabled)
        self.menu.addAction(self.action_enable)


        self.menu.addSeparator()
        self.action_add = QAction("Add Rule")
        self.action_add.triggered.connect(self.add_rule)
        self.menu.addAction(self.action_add)

        self.action_import = QAction("Import Rules")
        self.action_import.triggered.connect(self.import_rules)
        self.menu.addAction(self.action_import)

        self.action_export = QAction("Export Rules")
        self.action_export.triggered.connect(self.export_rules)
        self.menu.addAction(self.action_export)

        self.action_open_config = QAction("Edit Config")
        self.action_open_config.triggered.connect(self.open_config)
        self.menu.addAction(self.action_open_config)

        self.menu.addSeparator()
        self.action_quit = QAction("Quit")
        self.action_quit.triggered.connect(self.safe_quit)
        self.menu.addAction(self.action_quit)

        self.tray.setToolTip("Clipboard Sanitizer")


        if not self.tray.isVisible():
            self.tray.show()

        if not QSystemTrayIcon.isSystemTrayAvailable():
            QMessageBox.warning(None, "Clipboard Sanitizer",
                                "System tray is not available on this system.\n"
                                "The application will run in the background.")

        self.start_timer()

    def is_dark_mode(self):
        """Check if system is in dark mode."""
        try:
            app = QApplication.instance()
            if not app or not isinstance(app, QApplication):
                return False

            palette = app.palette()
            window_color = palette.color(QPalette.ColorRole.Window)
            text_color = palette.color(QPalette.ColorRole.WindowText)

            # More robust detection: check if text is lighter than background
            window_lightness = window_color.lightness()
            text_lightness = text_color.lightness()

            # If text is lighter than background, we're in dark mode
            return text_lightness > window_lightness
        except Exception:
            return False

    def update_tray_icon(self):
        """Update tray icon using system theme icon that adapts to light/dark mode."""
        icon_names = ["edit-paste", "edit-copy", "clipboard", "paste"]

        icon = None
        for icon_name in icon_names:
            icon = QIcon.fromTheme(icon_name)
            if not icon.isNull():
                break

        # Create custom icon if system icons aren't available
        if icon is None or icon.isNull():
            pixmap = QPixmap(22, 22)
            pixmap.fill(Qt.GlobalColor.transparent)
            painter = QPainter(pixmap)

            # Use current theme colors
            is_dark = self.is_dark_mode()
            color = QColor(255, 255, 255) if is_dark else QColor(0, 0, 0)

            # Draw with anti-aliasing for better appearance
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            pen = QPen(color, 1.5)
            painter.setPen(pen)

            # Draw clipboard icon
            painter.drawRect(6, 4, 10, 12)  # Main clipboard
            painter.drawRect(8, 2, 6, 3)   # Clip at top
            painter.end()

            icon = QIcon(pixmap)

        self.tray.setIcon(icon)

    def check_theme_change(self):
        """Check if theme has changed and update icon if needed."""
        current_dark_mode = self.is_dark_mode()
        if current_dark_mode != self.current_dark_mode:
            self.current_dark_mode = current_dark_mode
            self.update_tray_icon()

            app = QApplication.instance()
            if app and isinstance(app, QApplication):
                style = app.style()
                if style:
                    app.setStyle(style)
                app.processEvents()


    def on_theme_changed(self):
        """Handle system theme changes."""
        self.update_tray_icon()

    def start_timer(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_clipboard)
        self.timer.start(100)

    def check_clipboard(self):
        if not self.enabled:
            return
        try:
            text = self.clipboard.text()
            if text and text != self.last_text:
                self.last_text = text
                sanitized = self.sanitizer.sanitize(text)
                if sanitized != text:
                    self.clipboard.setText(sanitized)
                    self.tray.showMessage("Clipboard Sanitizer", "Clipboard sanitized")
        except Exception as e:
            print(f"Error monitoring clipboard: {e}")


    def toggle_enabled(self):
        self.enabled = self.action_enable.isChecked()
        self.config["enabled"] = self.enabled
        save_config(self.config, tray_icon=self.tray)
        self.tray.showMessage("Clipboard Sanitizer", "Enabled" if self.enabled else "Disabled")

    def add_rule(self):
        dialog = AddRuleDialog()
        if dialog.exec() == QDialog.DialogCode.Accepted:
            rule = dialog.get_rule()
            if rule:
                self.config["rules"].append(rule)
                save_config(self.config, tray_icon=self.tray)
                self.sanitizer.update_rules(self.config["rules"])
                self.tray.showMessage("Clipboard Sanitizer", f"Added rule '{rule['name']}' successfully")

    def import_rules(self):
        path, _ = QFileDialog.getOpenFileName(None, "Import Rules", "", "TOML Files (*.toml)")
        if not path:
            return
        try:
            data = toml.load(path)
            if "rules" in data and isinstance(data["rules"], list):
                self.config["rules"] = data["rules"]
                save_config(self.config, tray_icon=self.tray)
                self.sanitizer.update_rules(self.config["rules"])
                self.tray.showMessage("Clipboard Sanitizer", "Imported rules successfully")
        except Exception as e:
            QMessageBox.warning(None, "Error", f"Failed to import: {e}")

    def export_rules(self):
        path, _ = QFileDialog.getSaveFileName(None, "Export Rules", "", "TOML Files (*.toml)")
        if not path:
            return
        try:
            with open(path, "w", encoding="utf-8") as f:
                toml.dump(self.config, f)
            self.tray.showMessage("Clipboard Sanitizer", f"Exported rules to {path}")
        except Exception as e:
            QMessageBox.warning(None, "Error", f"Failed to export: {e}")

    def open_config(self):
        if CONFIG_PATH.exists():
            try:
                if sys.platform == "darwin":
                    subprocess.run(["open", str(CONFIG_PATH)])
                elif sys.platform == "win32":
                    os.startfile(str(CONFIG_PATH))
                else:
                    subprocess.run(["xdg-open", str(CONFIG_PATH)])
            except Exception as e:
                QMessageBox.warning(None, "Error", f"Failed to open config: {e}")
                print(f"Error opening config file: {e}")
        else:
            QMessageBox.information(None, "Info", "Config file does not exist.")

    def safe_quit(self):
        app = QApplication.instance()
        if app:
            app.quit()
