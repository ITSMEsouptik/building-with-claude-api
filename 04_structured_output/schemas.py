"""Pydantic models for extraction. extra='forbid' also emits additionalProperties: false."""
from typing import Literal

from pydantic import BaseModel, ConfigDict, field_validator


class Ticket(BaseModel):
    model_config = ConfigDict(extra="forbid")

    customer: str
    category: Literal["billing", "bug", "feature_request", "other"]
    urgency: int
    summary: str

    @field_validator("urgency")
    @classmethod
    def urgency_in_range(cls, v: int) -> int:
        """Urgency is 1 (low) to 5 (critical). Checked here, not in the schema."""
        if not 1 <= v <= 5:
            raise ValueError("urgency must be between 1 and 5")
        return v
