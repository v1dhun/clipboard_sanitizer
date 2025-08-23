"""
Clipboard content sanitizer.
"""

import re
from typing import List, Dict, Any

class Sanitizer:
    """Clipboard content sanitizer."""

    def __init__(self, rules: List[Dict[str, Any]]):
        self.compiled = []
        self.update_rules(rules)

    def update_rules(self, rules: List[Dict[str, Any]]) -> None:
        """Compile regex patterns and store placeholders."""
        self.compiled.clear()

        if not isinstance(rules, list):
            return

        for rule in rules:
            if not isinstance(rule, dict):
                continue

            if not rule.get("enabled", True):
                continue

            pattern = rule.get("pattern", "")
            placeholder = rule.get("placeholder", "[REDACTED]")

            if not pattern:
                continue

            try:
                regex = re.compile(pattern, re.IGNORECASE | re.MULTILINE)
                self.compiled.append((regex, placeholder))

            except re.error:
                pass
            except Exception:
                pass

    def sanitize(self, text: str) -> str:
        """Sanitize text by applying all enabled rules."""
        if not text:
            return text

        if not isinstance(text, str):
            try:
                text = str(text)
            except Exception:
                return "[ERROR: Invalid input]"

        try:
            result = text

            for regex, placeholder in self.compiled:
                try:
                    result = regex.sub(placeholder, result)
                except Exception:
                    continue

            return result

        except Exception:
            return "[ERROR: Sanitization failed]"
