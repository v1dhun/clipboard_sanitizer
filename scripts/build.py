#!/usr/bin/env python3
"""
Build script for Clipboard Sanitizer macOS application.
"""

import os
import sys
import shutil
import subprocess
import platform
from pathlib import Path


class MacOSBuilder:
    """Builds macOS standalone app for Clipboard Sanitizer."""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.dist_dir = self.project_root / "dist"
        self.build_dir = self.project_root / "build"
        self.spec_file = self.project_root / "clipboard_sanitizer.spec"

        # App metadata
        self.app_name = "Clipboard Sanitizer"
        self.app_version = "1.0.0"
        self.app_identifier = "com.clipboardsanitizer.app"

    def check_requirements(self) -> bool:
        """Check if all build requirements are met."""
        print("Checking build requirements...")

        if platform.system() != "Darwin":
            print("Error: This build script is designed for macOS only.")
            return False

        if sys.version_info < (3, 8):
            print("Error: Python 3.8 or higher is required.")
            return False

        try:
            import PyInstaller
            print(f"PyInstaller version: {PyInstaller.__version__}")
        except ImportError:
            print("Error: PyInstaller is not installed.")
            print("Install it with: pip install pyinstaller")
            return False

        if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
            print("Warning: Virtual environment not detected. Consider using one for clean builds.")

        return True

    def clean_build_dirs(self) -> None:
        """Clean previous build artifacts."""
        print("Cleaning previous build artifacts...")

        dirs_to_clean = [self.dist_dir, self.build_dir]
        files_to_clean = [self.spec_file]

        for dir_path in dirs_to_clean:
            if dir_path.exists():
                shutil.rmtree(dir_path)
                print(f"Removed: {dir_path}")

        for file_path in files_to_clean:
            if file_path.exists():
                file_path.unlink()
                print(f"Removed: {file_path}")

    def create_spec_file(self) -> None:
        """Create PyInstaller spec file for the app."""
        print("Creating PyInstaller spec file...")

        icon_path = self.project_root / "assets" / "icon.icns"
        if not icon_path.exists():
            icon_path = self.project_root / "assets" / "icon.png"

        icon_reference = f"'{icon_path}'" if icon_path.exists() else "None"

        spec_content = f'''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['src/main.py'],
    pathex=['{self.project_root}'],
    binaries=[],
    datas=[],
    hiddenimports=[
        'PySide6.QtCore',
        'PySide6.QtGui',
        'PySide6.QtWidgets',
        'toml',
        'src.config',
        'src.sanitizer',
        'src.tray_app'
    ],
    hookspath=[],
    hooksconfig=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='clipboard_sanitizer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='clipboard_sanitizer',
)

app = BUNDLE(
    coll,
    name='{self.app_name}.app',
    icon={icon_reference},
    bundle_identifier='{self.app_identifier}',
    version='{self.app_version}',
    info_plist={{
        'CFBundleName': '{self.app_name}',
        'CFBundleDisplayName': '{self.app_name}',
        'CFBundleVersion': '{self.app_version}',
        'CFBundleShortVersionString': '{self.app_version}',
        'CFBundleIdentifier': '{self.app_identifier}',
        'CFBundleExecutable': 'clipboard_sanitizer',
        'CFBundlePackageType': 'APPL',
        'CFBundleSignature': '????',
        'LSMinimumSystemVersion': '10.15.0',
        'NSHighResolutionCapable': True,
        'LSUIElement': True,
        'NSRequiresAquaSystemAppearance': False,
        'CFBundleDocumentTypes': [],
        'CFBundleURLTypes': [],
        'NSAppleEventsUsageDescription': 'Clipboard Sanitizer needs to monitor clipboard content for sanitization.',
        'NSSystemAdministrationUsageDescription': 'Clipboard Sanitizer may need system permissions to access clipboard content.',
    }},
)
'''

        with open(self.spec_file, 'w') as f:
            f.write(spec_content)

        print(f"Created spec file: {self.spec_file}")
        if icon_path.exists():
            print(f"Using icon: {icon_path}")
        else:
            print("No icon found - app will use default icon")

    def install_dependencies(self) -> bool:
        """Install required dependencies."""
        print("Installing dependencies...")

        try:
            subprocess.run([
                sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'
            ], check=True, capture_output=True, text=True)

            subprocess.run([
                sys.executable, '-m', 'pip', 'install', 'pyinstaller'
            ], check=True, capture_output=True, text=True)

            print("Dependencies installed successfully.")
            return True

        except subprocess.CalledProcessError as e:
            print(f"Error installing dependencies: {e}")
            print(f"stdout: {e.stdout}")
            print(f"stderr: {e.stderr}")
            return False

    def build_app(self) -> bool:
        """Build the macOS app using PyInstaller."""
        print("Building macOS app...")

        try:
            cmd = [
                sys.executable, '-m', 'PyInstaller',
                '--clean',
                '--noconfirm',
                str(self.spec_file)
            ]

            print(f"Running: {' '.join(cmd)}")
            subprocess.run(cmd, check=True, capture_output=True, text=True)

            print("Build completed successfully!")
            print(f"App location: {self.dist_dir / (self.app_name + '.app')}")
            return True

        except subprocess.CalledProcessError as e:
            print(f"Build failed: {e}")
            print(f"stdout: {e.stdout}")
            print(f"stderr: {e.stderr}")
            return False

    def build(self, clean: bool = True, create_dmg: bool = False) -> bool:
        """Main build process."""
        print("=" * 60)
        print(f"Building {self.app_name} for macOS")
        print("=" * 60)

        if not self.check_requirements():
            return False

        if clean:
            self.clean_build_dirs()

        if not self.install_dependencies():
            return False

        self.create_spec_file()

        if not self.build_app():
            return False

        print("=" * 60)
        print("Build completed successfully!")
        print(f"App location: {self.dist_dir / (self.app_name + '.app')}")
        print("=" * 60)

        return True


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Build Clipboard Sanitizer for macOS")
    parser.add_argument("--no-clean", action="store_true", help="Don't clean previous builds")
    parser.add_argument("--version", action="version", version="1.0.0")

    args = parser.parse_args()

    builder = MacOSBuilder()
    success = builder.build(clean=not args.no_clean)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
