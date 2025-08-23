# Clipboard Sanitizer

A Menubar app that automatically sanitizes clipboard content by replacing sensitive information with configurable placeholders.
> (Built with PySide6 — cross-platform capable, but currently tested only on macOS.)

## Features

* **Real-time monitoring** – Automatically detects and sanitizes clipboard content
* **Customizable rules** – Define your own patterns and replacement text
* **Menubar integration** – Runs quietly in the background
* **Native macOS design** – Light & dark theme support
* **Privacy focused** – All processing happens locally

## Installation

### From Source

```bash
make install
make run
```

### Build Application

```bash
make build  # Creates macOS .app bundle
```

## Usage

1. Launch the app – it appears in the menubar
2. Right-click the icon to access settings
3. Add custom sanitization rules via **Add Rule**
4. Clipboard content matching rules is automatically sanitized

## Configuration

Config file:
`~/Library/Application Support/ClipboardSanitizer/config.toml`

### Default Rules

* Emails → `[EMAIL]`
* Phone numbers → `[PHONE]`
* Social Security Numbers → `[SSN]`

### Custom Rules

Define:

* **Pattern** – Text or regex to match
* **Replacement** – Text to replace matches
* **Name** – Descriptive rule name

## License

MIT License – see [LICENSE](LICENSE) for details
