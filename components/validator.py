import logging
from typing import Any

from domain.dto import DTO


class Validator:
    def __init__(self, logger: logging.Logger | None = None):
        self.logger = logger or logging.getLogger("Validator")
        

    def validate_line(self, record_dict: dict[str, Any]) -> dict[str, Any] | None:
        self.logger.debug(f"DEBUG: Processing this dictionary right now -> {record_dict}")
        
        # VALDIATING DICTIONARY
        dto_obj = DTO.model_validate(record_dict)
        self.logger.debug(f"SUCCESS: Record for '{dto_obj.name}' passed validation.")
        
        return dto_obj.model_dump()
    


    
