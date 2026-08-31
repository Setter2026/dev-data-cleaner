import logging
from domain.exceptions import ParseError
import re

class Parser:
    def __init__(self, logger: logging.Logger = None):
        self.logger = logger or logging.getLogger("Parser")

    def parse_line(self, line: str) -> dict:
        self.logger.debug(f"Parsing line: '{line}'")

        # 1. SPECIFIC CHECK: Non-string input type
        if not isinstance(line, str):
            self.logger.error(f"TYPE ERROR: Expected string input, got {type(line).__name__}.")
            raise ParseError("Input must be a string.")

        # 2. SPECIFIC CHECK: Unmatched quote marks
        if line.count('"') % 2 != 0 or line.count("'") % 2 != 0:
            self.logger.error(f"SYNTAX ERROR: Unmatched quotes in line -> '{line}'")
            raise ParseError("Unmatched Quotes")

        pairs = [p.strip() for p in re.split(r"[,|]", line) if p.strip()]
        record = {}

        # 3. SPECIFIC CHECK: Empty line after split
        if not pairs:
            self.logger.warning("EMPTY LINE: No key-value pairs found after splitting line.")
            return record

        for pair in pairs:
            # 4. SPECIFIC CHECK: Missing colon delimiter
            if ":" not in pair:
                self.logger.error(f"DELIMITER ERROR: Missing ':' in pair -> '{pair}'")
                raise ParseError(f"Missing Delimiters (expected ':' in '{pair}')")

            parts = pair.split(":", 1)
            
            # 5. SPECIFIC CHECK: Wrong column count (multiple colons in one pair, e.g., "key:val1:val2")
            if len(parts) != 2:
                self.logger.error(f"COLUMN COUNT ERROR: Expected 1 colon, found {len(parts)-1} in pair -> '{pair}'")
                raise ParseError(f"Wrong Column Count in pair '{pair}'")

            k, v = parts[0].strip().lower(), parts[1].strip()

            # 6. SPECIFIC CHECK: Empty key or value (e.g. "name:" or ":John")
            if not k or not v:
                self.logger.error(f"EMPTY VALUE ERROR: Missing key or value in pair -> '{pair}'")
                raise ParseError(f"Empty key or value in pair '{pair}'")

            record[k] = v

        self.logger.debug(f"Successfully parsed record with keys: {list(record.keys())}")
        return record

line = "ID: 101 | Name: Leo   | Age: 10 | Status: Active"
parser = Parser()
print(parser.parse_line(line))