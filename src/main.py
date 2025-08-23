"""
Clipboard Sanitizer - Main Application Entry Point
"""

import sys
import os
import logging
import argparse
from pathlib import Path
from typing import Any

from PySide6.QtWidgets import QApplication, QMessageBox, QSystemTrayIcon

from src.config import load_config, reset_config
from src.sanitizer import Sanitizer
from src.tray_app import TrayApp


def setup_logging(debug: bool = False) -> None:
    """Configure application logging."""
    log_level = logging.DEBUG if debug else logging.INFO
    log_format = '%(asctime)s - %(levelname)s - %(message)s'

    if sys.platform == "win32":
        log_file = Path(os.environ.get('TEMP', '')) / 'clipboard-sanitizer.log'
    else:
        log_file = Path('/tmp/clipboard-sanitizer.log')

    handlers: list = [logging.FileHandler(log_file)]
    if debug:
        handlers.append(logging.StreamHandler(sys.stdout))
    else:
        handlers.append(logging.NullHandler())

    logging.basicConfig(
        level=log_level,
        format=log_format,
        handlers=handlers
    )


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Clipboard Sanitizer - Simple clipboard content sanitization"
    )

    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug output and logging'
    )

    parser.add_argument(
        '--reset-config',
        action='store_true',
        help='Reset configuration to defaults'
    )

    parser.add_argument(
        '--version',
        action='version',
        version='Clipboard Sanitizer 1.0.0'
    )

    return parser.parse_args()


def _validate_rules(rules: Any) -> list[dict[str, Any]]:
    """Validate and filter rules configuration."""
    if not isinstance(rules, list):
        logging.warning("Invalid rules format in config, resetting to empty list")
        return []

    valid_rules = []
    for rule in rules:
        if isinstance(rule, dict) and "pattern" in rule and "placeholder" in rule:
            valid_rules.append(rule)
        else:
            logging.warning(f"Ignored invalid rule: {rule}")

    return valid_rules


def main() -> int:
    """Main application entry point."""
    logger = logging.getLogger(__name__)

    try:
        args = parse_arguments()
        setup_logging(args.debug)
        logger.info("Starting Clipboard Sanitizer")

        if args.reset_config:
            if reset_config():
                logger.info("Configuration reset successfully")
                return 0
            else:
                logger.error("Failed to reset configuration")
                return 1

        app = QApplication(sys.argv)
        app.setQuitOnLastWindowClosed(False)
        app.setApplicationName("Clipboard Sanitizer")
        app.setApplicationVersion("1.0.0")

        app.setStyle(app.style())

        if sys.platform == "darwin":
            try:
                palette = app.palette()
                app.setPalette(palette)
            except Exception:
                pass

        if not QSystemTrayIcon.isSystemTrayAvailable():
            QMessageBox.warning(None, "Clipboard Sanitizer",
                               "System tray is not available on this system.\n"
                               "The application will continue to run in the background.")

        try:
            cfg = load_config()
            if not isinstance(cfg, dict):
                cfg = {"enabled": True, "rules": []}
            else:
                cfg.setdefault("enabled", True)
                cfg["rules"] = _validate_rules(cfg.get("rules", []))
        except Exception as e:
            logger.warning(f"Failed to load configuration: {e}")
            cfg = {"enabled": True, "rules": []}

        try:
            sanitizer = Sanitizer(cfg["rules"])
        except Exception as e:
            logger.error(f"Failed to initialize sanitizer: {e}")
            QMessageBox.critical(None, "Error", "Failed to initialize sanitizer")
            return 1

        try:
            tray_app = TrayApp(cfg, sanitizer)
            if not tray_app.tray.isVisible():
                tray_app.tray.show()
        except Exception as e:
            logger.error(f"Failed to create tray application: {e}")
            QMessageBox.critical(None, "Error", f"Failed to create tray application: {e}")
            return 1

        if QSystemTrayIcon.supportsMessages():
            tray_app.tray.showMessage(
                "Clipboard Sanitizer",
                "Application is now running in the system tray",
                QSystemTrayIcon.MessageIcon.Information,
                3000
            )

        return app.exec()

    except Exception as e:
        logger.error(f"Fatal error during startup: {e}", exc_info=True)
        QMessageBox.critical(None, "Fatal Error", f"Application failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
