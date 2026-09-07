import json
import logging


class JSONExporter:
    def __init__(self, logger: logging.Logger | None = None):
        # Keeps its own notebook (logger)
        self.logger = logger or logging.getLogger("JSONExporter")

    def json_export(self, data: list, output_filepath: str = "output.json") -> None:
        self.logger.info(f"Preparing to export {len(data)} records to '{output_filepath}'...")

        # 1. SPECIFIC CHECK: Serializing data to JSON string
        try:
            json_str = json.dumps(data, indent=2)
        except (TypeError, ValueError) as e:
            self.logger.error(f"DATA CORRUPTED: Could not convert data to JSON. Details: {e}")
            raise

        # 2. ATTEMPT PRIMARY WRITE
        try:
            with open(output_filepath, "w", encoding="utf-8") as f:
                f.write(json_str)
            self.logger.info(f"SUCCESS: Exported output to '{output_filepath}'.")
            return

        # SPECIFIC ERROR 1: Access denied (e.g. read-only folder, admin rights needed)
        except PermissionError:
            self.logger.error(f"PERMISSION DENIED: No write access to path '{output_filepath}'.")

        # SPECIFIC ERROR 2: Invalid path / folder doesn't exist
        except FileNotFoundError:
            self.logger.error(f"FILE NOT FOUND: The directory for path '{output_filepath}' does not exist.")

        # SPECIFIC ERROR 3: Other OS issues (e.g. disk full, read-only filesystem)
        except OSError as e:
            self.logger.error(f"OS ERROR: System issue while writing to '{output_filepath}'. Details: {e}")

        # 3. FALLBACK HANDLING
        fallback = "fallback_output.json"
        self.logger.warning(f"FALLBACK TRIGGERED: Attempting to save output to default path '{fallback}'...")

        try:
            with open(fallback, "w", encoding="utf-8") as f:
                f.write(json_str)
            self.logger.info(f"SUCCESS: Fallback export saved to '{fallback}'.")

        except Exception as fallback_error:
            # If even the fallback fails, log critical system failure
            self.logger.critical(f"CRITICAL: Fallback file write also failed! Details: {fallback_error}")
            raise