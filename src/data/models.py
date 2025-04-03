from pydantic import BaseModel, field_validator
from typing import List, Optional, Dict


class Pair_data(BaseModel):
    raw_data: str | List
    old_data: Optional[List] = None


class Parcel(BaseModel):
    data_combined: Dict[str, List] | None


class DequeChange(BaseModel):
    """Represents a changein the deque"""

    operation: str
    old_value: List
    new_value: List
