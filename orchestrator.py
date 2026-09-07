import json
import logging
from typing import Any

from pydantic import ValidationError

from domain.dto import DTO
from domain.exceptions import ParseError, SanitizeError


class PipelineOrchestrator:
    """Coordinates streaming file ingestion, line-by-line sanitization,

    parsing, validation, tracking, and export.
    """

    def __init__(
        self,
        file_loader: Any,
        sanitizer: Any,
        parser: Any,
        validator: Any,
        exporter: Any,
        tracker: Any | None = None,
        logger: logging.Logger | None = None,
    ):
        self.loader = file_loader
        self.sanitizer = sanitizer
        self.parser = parser
        self.validator = validator
        self.exporter = exporter
        self.tracker = tracker
        self.logger = logger or logging.getLogger("PipelineOrchestrator")

    def run(
        self,
        input_filepath: str,
        output_filepath: str = "output.json",
        errors_filepath: str = "data/errors.json",
    ) -> int:
        """Executes the full streaming pipeline workflow end-to-end line by line.

        Returns the exit code (0 for success, 1 for quarantined records).
        """
        valid_dtos: list[DTO] = []
        error_list: list[dict[str, Any]] = []

        # 1. STREAMING LINE-BY-LINE INGESTION & PROCESSING
        try:
            # Assumes file_loader.load_lines() or .load() yields lines lazily via yield
            line_generator = self.loader.load(input_filepath)
            
            self.logger.info(f"=== PIPELINE STARTED: Ingesting '{input_filepath}' ===")

            for idx, line in enumerate(line_generator, start=1):
                raw_line = line.strip()
                
                if not raw_line:
                    continue

                if self.tracker:
                    self.tracker.increment_processed()
                    
                self.logger.debug(f"Processing line {idx}: {raw_line!r}")

                # STEP A: SANITIZE
                try:
                    clean_line = self.sanitizer.sanitize_line(raw_line)
                except SanitizeError as sanitize_err:
                    self.logger.error(f"Line {idx}: Sanitization error -> {sanitize_err}")
                    error_entry = {
                        "line_number": idx,
                        "raw_record": line,
                        "reasons": [str(sanitize_err)],
                    }
                    error_list.append(error_entry)
                    if self.tracker:
                        self.tracker.increment_quarantined()
                    continue

                # STEP B: PARSE
                try:
                    raw_dict = self.parser.parse_line(clean_line)
                except ParseError as parse_err:
                    self.logger.error(f"Line {idx}: Parsing syntax error -> {parse_err}")
                    error_entry = {
                        "line_number": idx,
                        "raw_record": line,
                        "reasons": [str(parse_err)],
                    }
                    error_list.append(error_entry)
                    if self.tracker:
                        self.tracker.increment_quarantined()
                    continue

                # STEP C: VALIDATE
                try:
                    dto_obj = self.validator.validate_line(raw_dict)
                    if dto_obj:
                        valid_dtos.append(dto_obj)
                        if self.tracker:
                            self.tracker.increment_cleaned()
                except ValidationError as validate_err:
                    reasons = []
                    for err in validate_err.errors():
                        self.logger.warning(f"Line {idx}: Corrupted line: {raw_dict}")
                        loc = err.get("loc", ())
                        field_name = str(loc[0]) if loc else "__all__"
                        reasons.append(f"Field '{field_name}': {err.get('msg')}")

                    error_entry = {
                        "line_number": idx,
                        "raw_record": line,
                        "reasons": reasons,
                    }
                    error_list.append(error_entry)
                    if self.tracker:
                        self.tracker.increment_quarantined()
                    continue

        except (FileNotFoundError, PermissionError, OSError) as e:
            self.logger.critical(
                f"PIPELINE ABORTED: FileLoader failed. Details: {e}"
            )
            raise

        # 2. EXPORT CLEANED DATA & ERRORS
        self.logger.info(
            f"Exporting {len(valid_dtos)} valid DTO record(s) to '{output_filepath}'..."
        )
        self.exporter.json_export(valid_dtos, output_filepath)

        if error_list:
            with open(errors_filepath, "w") as f:
                json.dump(error_list, f, indent=2)
            if self.tracker and hasattr(self.tracker, "errors_filepath"):
                self.tracker.errors_filepath = errors_filepath

        # 3. TRACKING & SUMMARY OUTPUT
        if self.tracker:
            if hasattr(self.tracker, "print_tracks"):
                self.tracker.print_tracks()
            elif hasattr(self.tracker, "print_summary"):
                self.tracker.print_summary()

            return getattr(self.tracker, "exit_code", 1 if error_list else 0)

        return 1 if error_list else 0