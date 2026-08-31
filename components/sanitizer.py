import logging
import re
from domain.exceptions import SanitizeError

class Sanitizer:
    def __init__(self, logger: logging.Logger = None):
        self.logger = logger or logging.getLogger("Sanitizer")

    def sanitize_line(self, line: str) -> str:
        """Sanitizes a single line of text."""
        # 1. SPECIFIC CHECK: Input type
        if not isinstance(line, str):
            self.logger.error(f"TYPE ERROR: Expected string, got {type(line).__name__}.")
            raise SanitizeError("Line must be a string.")

        try:
            # Strip hidden control characters, zero-width spaces, and BOMs
            line_clean = re.sub(r"[\x00-\x1F\x7F-\x9F\u200B-\u200D\uFEFF]", "", line).strip()
            
            if len(line) != len(line_clean):
                self.logger.debug(f"Cleaned hidden characters/whitespace from line.")

            return line_clean

        # 2. SPECIFIC CATCH: Bad Unicode decoding
        except UnicodeDecodeError as e:
            self.logger.error(f"ENCODING ERROR: Failed to decode characters in line. Details: {e}")
            raise SanitizeError(f"UnicodeDecodeError: {e}")

        # 3. SAFETY NET: Unexpected regex/string errors
        except Exception as e:
            self.logger.exception(f"UNEXPECTED SANITIZATION ERROR: {e}")
            raise SanitizeError(f"Sanitization failed: {e}")

    