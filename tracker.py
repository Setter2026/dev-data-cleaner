import time
import logging
from typing import Dict, Any, List, Optional

class PipelineTracker:
    """
    Tracks pipeline operational metrics, performance timing, 
    and detailed diagnostic logs during execution.
    """
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger("PipelineTracker")
        self.reset()

    def reset(self) -> None:
        """Resets all metrics for a new pipeline run."""
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None
        
        # Batch Counters
        self.total_lines: int = 0
        self.valid_dtos: int = 0
        self.degraded_records: int = 0
        self.corrupt_lines: int = 0
        
        # Detailed Diagnostics
        self.warnings: List[Dict[str, Any]] = []
        self.errors: List[Dict[str, Any]] = []

    def start_pipeline(self) -> None:
        """Starts execution timer."""
        self.reset()
        self.start_time = time.perf_counter()
        self.logger.debug("Pipeline metrics tracking started.")

    def stop_pipeline(self) -> None:
        """Stops execution timer."""
        self.end_time = time.perf_counter()
        self.logger.debug("Pipeline metrics tracking stopped.")

    @property
    def duration_seconds(self) -> float:
        """Returns total execution time in seconds."""
        if self.start_time is None:
            return 0.0
        end = self.end_time or time.perf_counter()
        return round(end - self.start_time, 4)

    def record_success(self) -> None:
        """Increment count for 100% valid DTO records."""
        self.valid_dtos += 1

    def record_degraded(self, line_num: int, missing_fields: List[str], details: str) -> None:
        """Record a degraded record (fields defaulted to 'N/A')."""
        self.degraded_records += 1
        self.warnings.append({
            "line": line_num,
            "missing_fields": missing_fields,
            "details": details
        })

    def record_corrupt(self, line_num: int, reason: str) -> None:
        """Record an unparseable or completely broken line."""
        self.corrupt_lines += 1
        self.errors.append({
            "line": line_num,
            "reason": reason
        })

    def get_summary_report(self) -> Dict[str, Any]:
        """Generates a structured execution report dictionary."""
        total_processed = self.valid_dtos + self.degraded_records + self.corrupt_lines
        success_rate = (self.valid_dtos / total_processed * 100) if total_processed > 0 else 0.0

        return {
            "metrics": {
                "duration_seconds": self.duration_seconds,
                "total_lines_read": self.total_lines,
                "fully_valid_dtos": self.valid_dtos,
                "degraded_na_records": self.degraded_records,
                "corrupt_failed_lines": self.corrupt_lines,
                "success_rate_pct": round(success_rate, 2)
            },
            "diagnostics": {
                "warning_count": len(self.warnings),
                "error_count": len(self.errors),
                "warnings": self.warnings,
                "errors": self.errors
            }
        }

    def log_summary(self) -> None:
        """Outputs formatted metrics to the logger."""
        summary = self.get_summary_report()["metrics"]
        self.logger.info("==========================================")
        self.logger.info("       PIPELINE EXECUTION TRACKER         ")
        self.logger.info("==========================================")
        self.logger.info(f" Execution Duration  : {summary['duration_seconds']} sec")
        self.logger.info(f" Total Lines Read    : {summary['total_lines_read']}")
        self.logger.info(f" Valid DTO Objects   : {summary['fully_valid_dtos']}")
        self.logger.info(f" Degraded (N/A)      : {summary['degraded_na_records']}")
        self.logger.info(f" Corrupt / Unparsed  : {summary['corrupt_failed_lines']}")
        self.logger.info(f" Success Rate        : {summary['success_rate_pct']}%")
        self.logger.info("==========================================")