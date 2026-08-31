import logging
from typing import List, Dict, Any, Tuple, Optional
from domain.dto import DTO
from domain.exceptions import SanitizeError, ParseError
from pydantic import ValidationError

class PipelineOrchestrator:
    """
    Coordinates file ingestion, streaming line-by-line sanitization, 
    parsing, validation, tracking, and export.
    """
    def __init__(
        self,
        file_loader: Any,
        sanitizer: Any,
        parser: Any,
        validator: Any,
        exporter: Any,
        tracker: Optional[Any] = None,
        logger: Optional[logging.Logger] = None
    ):
        self.loader = file_loader
        self.sanitizer = sanitizer
        self.parser = parser
        self.validator = validator
        self.exporter = exporter
        self.tracker = tracker
        self.logger = logger or logging.getLogger("PipelineOrchestrator")

    def run(self, input_filepath: str, output_filepath: str = "output.json") -> Tuple[List[Dict[str, Any]], List[DTO]]:
        """
        Executes the full pipeline workflow end-to-end line by line.
        """
        if self.tracker:
            self.tracker.start_pipeline()

        self.logger.info(f"=== PIPELINE STARTED: Ingesting '{input_filepath}' ===")
        
        # 1. FILE INGESTION (Load raw content)
        try:
            raw_content = self.loader.load(input_filepath)
        except (FileNotFoundError, PermissionError, OSError) as e:
            self.logger.critical(f"PIPELINE ABORTED: FileLoader failed. Details: {e}")
            raise

        raw_lines = raw_content.splitlines()
        total_lines = len(raw_lines)
        self.logger.info(f"Loaded {total_lines} raw line(s) for processing.")

        if self.tracker:
            self.tracker.total_lines = total_lines

        report_records: List[Dict[str, Any]] = []
        valid_dtos: List[DTO] = []
        records = 0

        # 2. LINE-BY-LINE STREAMING PROCESS: Sanitizer -> Parser -> Validator
        for idx, raw_line in enumerate(raw_lines, start=1):
            self.logger.debug(f"Processing line {idx}/{total_lines}: {raw_line!r}")
            try:
                # Expects sanitizer.sanitize_line(raw_line) or sanitize_content(raw_line)
                clean_line = self.sanitizer.sanitize_line(raw_line)
            except SanitizeError as sanitize_err:
                self.logger.error(f"Line {idx}: Sanitization error -> {sanitize_err}")
                if self.tracker:
                    self.tracker.record_corrupt(line_num=idx, reason=f"SanitizeError: {sanitize_err}")
                #report_records.append({"id": "N/A", "name": "N/A", "age": "N/A", "status": "N/A"})
                continue
            
            # Skip empty/whitespace lines if sanitizer returns empty string
            if not clean_line.strip():
                self.logger.debug(f"Line {idx}: Skipped empty/blank line.")
                continue

            try:
                raw_dict = self.parser.parse_line(clean_line)
            except ParseError as parse_err:
                self.logger.error(f"Line {idx}: Parsing syntax error -> {parse_err}")
                if self.tracker:
                    self.tracker.record_corrupt(line_num=idx, reason=f"ParseError: {parse_err}")
                #report_records.append({"id": "N/A", "name": "N/A", "age": "N/A", "status": "N/A"})
                continue
            
            try:
                dto_obj = self.validator.validate_line(raw_dict)
                valid_dtos.append(dto_obj)
                if self.tracker:
                    self.tracker.record_success()
                    
            except ValidationError:
                self.logger.warning(f"Line {idx}: Corrupted line: {raw_dict}")
                
        self.logger.info(f"Exporting {len(report_records)} report record(s) to '{output_filepath}'...")
        self.exporter.json_export(valid_dtos, output_filepath)

        # 4. TRACKING & SUMMARY
        if self.tracker:
            self.tracker.stop_pipeline()
            self.tracker.log_summary()

        return valid_dtos
        
            