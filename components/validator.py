import logging
from typing import Dict, Any, Tuple, Optional
from pydantic import ValidationError
from domain.dto import DTO

class Validator:
    def __init__(self, logger: logging.Logger = None):
        self.logger = logger or logging.getLogger("Validator")
        

    def validate_line(self, record_dict: Dict[str, Any]) -> Tuple[Dict[str, Any], Optional[DTO]]:
        try:
            self.logger.debug(f"DEBUG: Processing this dictionary right now -> {record_dict}")
            
            # Pydantic validates the dictionary here:
            dto_obj = DTO.model_validate(record_dict)
            self.logger.debug(f"SUCCESS: Record for '{dto_obj.name}' passed validation.")
            
            return dto_obj.model_dump()

        except ValidationError as e:
            self.logger.warning(f"Validation failed for record {record_dict}: {e}")
            raise e
        


    
