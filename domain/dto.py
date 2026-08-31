import logging
from typing import Annotated, Any, Literal
from pydantic import BaseModel, Field, ValidationInfo, ValidatorFunctionWrapHandler
from pydantic.functional_validators import WrapValidator

# 1. Setup your logging system
logger = logging.getLogger("DataClean")
logging.basicConfig(level=logging.WARNING)

# 2. Create ONE generic safety net function for ALL optional fields
def heal_and_log_field(value: Any, handler: ValidatorFunctionWrapHandler, info: ValidationInfo) -> Any:
    try:
        # Try validating the field normally using Pydantic's strict rules
        return handler(value)
    except Exception:
        # If it fails, log the field name and bad value, then fallback to None
        """
        logger.warning(
            f"⚠️ Fields validation anomaly! Field '{info.field_name}' "
            f"received invalid data: '{value}'. Gracefully defaulting to None."
        )
        """
        return None

# 3. Create a clean modifier using WrapValidator
# This can be applied to any field type (str, int, Literal, etc.)
SafeField = WrapValidator(heal_and_log_field)

# 4. Define your bulletproof model
class DTO(BaseModel):
    # MANDATORY: No SafeField wrapper. If ID is broken, the whole line breaks!
    id: int 
    
    # OPTIONAL FIELDS: Wrapped in SafeField so they heal to None on failure
    name: Annotated[str | None, SafeField] = Field(default=None, min_length=1)
    age: Annotated[int | None, SafeField] = Field(default=None, gt=0, lt=120)
    status: Annotated[Literal["Active", "Pending"] | None, SafeField] = Field(default=None)
