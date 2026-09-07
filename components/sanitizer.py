import logging
import re

from domain.exceptions import SanitizeError


class Sanitizer:
    def __init__(self, logger: logging.Logger | None = None):
        self.logger = logger or logging.getLogger("Sanitizer")

    def sanitize_line(self, line: str) -> str:
        """Sanitizes a single line of text."""
        
        # 1. SPECIFIC CHECK: Non-string input type
        if not isinstance(line, str):
            raise SanitizeError(f"Expected str, got {type(line).__name__}")

        # 2. PERFORM REGEX CLEANUP 
        line_clean = re.sub(
            r"[\x00-\x1F\x7F-\x9F\u200B-\u200D\uFEFF]", "", line
        ).strip()

        # 3. Log if modifications occurred
        if len(line) != len(line_clean):
            self.logger.debug("Cleaned hidden characters/whitespace from line.")

        return line_clean

    