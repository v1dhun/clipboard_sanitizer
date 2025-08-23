APP_NAME = Clipboard Sanitizer
APP_BUNDLE = dist/$(APP_NAME).app
ICON = assets/icon.png
SPEC_FILE = clipboard_sanitizer.spec
BUILD_SCRIPT = scripts/build.py
CREATE_ICON_SCRIPT = scripts/create_icon.py
SRC_DIR = src
VENV_PATH = .venv

activate:
	@if [ ! -d "$(VENV_PATH)" ]; then \
		echo "Creating virtual environment..."; \
		python3 -m venv $(VENV_PATH); \
	fi
	@echo "Virtual environment activated."

build: activate
	$(VENV_PATH)/bin/python3 $(BUILD_SCRIPT)

icon: activate
	$(VENV_PATH)/bin/python3 $(CREATE_ICON_SCRIPT)

clean:
	rm -rf dist build

dmg: activate build
	$(VENV_PATH)/bin/python3 $(BUILD_SCRIPT) --dmg

run: activate
	$(VENV_PATH)/bin/python -m src.main $(ARGS)

debug: activate
	$(VENV_PATH)/bin/python -m src.main --debug

install: activate
	$(VENV_PATH)/bin/python -m pip install -r requirements.txt

help:
	@echo "Makefile for Clipboard Sanitizer"
	@echo "Usage: make <target>"
	@echo "Targets:"
	@echo "  activate: Activate the virtual environment"
	@echo "  build:    Build the application"
	@echo "  icon:     Create the application icon"
	@echo "  clean:    Clean the project"
	@echo "  dmg:      Create a DMG package (requires build target)"
	@echo "  run:      Run the application from source (use ARGS=\"--flag\" to pass arguments)"
	@echo "  debug:    Run the application in debug mode"
	@echo "  install:  Install dependencies"
	@echo "  help:     Show this help message"
