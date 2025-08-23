"""
Configuration management for Clipboard Sanitizer.
"""

import sys
from pathlib import Path
import toml
from typing import Optional, Dict, Any
from PySide6.QtWidgets import QSystemTrayIcon

def get_config_dir() -> Path:
    """Get the appropriate config directory based on platform."""
    if sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support" / "ClipboardSanitizer"
    elif sys.platform == "win32":
        return Path.home() / "AppData" / "Local" / "ClipboardSanitizer"
    else:
        return Path.home() / ".config" / "clipboard-sanitizer"

CONFIG_DIR = get_config_dir()
CONFIG_PATH = CONFIG_DIR / "config.toml"

def default_config() -> Dict[str, Any]:
    """Return default configuration."""
    return {
        "enabled": True,
        "rules": [
            {
                "name": "Email Addresses",
                "pattern": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
                "placeholder": "[EMAIL]",
                "enabled": True
            },
            {
                "name": "Phone Numbers",
                "pattern": r"\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b",
                "placeholder": "[PHONE]",
                "enabled": True
            },
            {
                "name": "Social Security Numbers",
                "pattern": r"\b\d{3}-\d{2}-\d{4}\b",
                "placeholder": "[SSN]",
                "enabled": True
            }
        ]
    }

def load_config(tray_icon: Optional[QSystemTrayIcon] = None) -> Dict[str, Any]:
    """Load configuration with error handling."""
    try:
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)

        if CONFIG_PATH.exists():
            try:
                with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                    cfg = toml.load(f)

                if "enabled" not in cfg:
                    cfg["enabled"] = True
                if "rules" not in cfg:
                    cfg["rules"] = []

                for rule in cfg["rules"]:
                    if "enabled" not in rule:
                        rule["enabled"] = True

                if tray_icon:
                    tray_icon.showMessage("Clipboard Sanitizer", "Configuration loaded successfully")
                return cfg

            except Exception:
                if tray_icon:
                    tray_icon.showMessage("Clipboard Sanitizer", "Failed to load config, using defaults")

        cfg = default_config()
        save_config(cfg, tray_icon)
        return cfg

    except Exception:
        return {"enabled": True, "rules": []}

def save_config(cfg: Dict[str, Any], tray_icon: Optional[QSystemTrayIcon] = None) -> bool:
    """Save configuration with error handling."""
    try:
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            toml.dump(cfg, f)

        if tray_icon:
            tray_icon.showMessage("Clipboard Sanitizer", "Configuration saved successfully")

        return True

    except Exception as e:
        error_msg = f"Failed to save config: {e}"
        if tray_icon:
            tray_icon.showMessage("Clipboard Sanitizer", error_msg)
        return False

def reset_config(tray_icon: Optional[QSystemTrayIcon] = None) -> bool:
    """Reset configuration to defaults."""
    try:
        cfg = default_config()
        return save_config(cfg, tray_icon)
    except Exception:
        return False
