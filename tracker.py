from dataclasses import dataclass


@dataclass
class PipelineTracker:
    total_processed: int = 0
    quarantined_records: int = 0
    successfully_cleaned: int = 0

    def increment_processed(self) -> None:
        self.total_processed += 1
    
    def increment_quarantined(self) -> None:
        self.quarantined_records += 1
    
    def increment_cleaned(self) -> None:
        self.successfully_cleaned += 1
    
    def print_tracks(self):
        print("[✖️] Data Cleaning Complete with Errors")
        print("────────────────────────────────────────────")
        print(f"Total Processed: {self.total_processed}")
        print(f"Successfully Cleaned: {self.successfully_cleaned}")
        print(f"Quarantined Records: {self.quarantined_records}")