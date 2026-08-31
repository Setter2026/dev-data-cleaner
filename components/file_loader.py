from domain.exceptions import FileReadError
import logging
import os
class FileLoader:
    def __init__(self, logger=None):
        self.logger = logger or logging.getLogger("FileLoader")

    def load(self, file_path: str) -> str:
        self.logger.info(f"Attempting to load: '{file_path}'")

        # 1. SPECIFIC CHECK: Does it exist?
        if not os.path.exists(file_path):
            self.logger.error(f"FILE MISSING: Could not find '{file_path}'. Check the folder path!")
            raise FileReadError(f"File not found: {file_path}")

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                self.logger.info(f"SUCCESS: Read {len(content.splitlines())} lines.")
                return content

        # 2. SPECIFIC CATCH: Access denied!
        except PermissionError:
            self.logger.error(f"ACCESS DENIED: You don't have permission to open '{file_path}'.")
            raise FileReadError(f"Permission denied: {file_path}")

        # 3. SPECIFIC CATCH: Bad characters / unreadable!
        except UnicodeDecodeError:
            self.logger.error(f"CORRUPTED FILE: '{file_path}' contains unreadable binary/encoding data.")
            raise FileReadError(f"Corrupted file: {file_path}")

        # 4. SAFETY NET: Anything wild we didn't think of (e.g., hard drive unplugged)
        except Exception as e:
            self.logger.exception(f"UNKNOWN SYSTEM ERROR: {e}")
            raise FileReadError(f"Unreadable file: {e}")
