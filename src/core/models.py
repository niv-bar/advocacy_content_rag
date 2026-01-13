"""Data models for the feature pipeline."""
from typing import Optional
from pydantic import BaseModel, Field, field_validator


class RawDataRow(BaseModel):
    """Normalized row from Excel source data."""

    id: str = Field(..., description="Unique hash identifier")
    main_subject: str
    sub_topic: str = "General"
    question: str
    link: Optional[str] = None
    social_network: str = "Other"

    @field_validator('link')
    @classmethod
    def clean_link(cls, v: Optional[str]) -> Optional[str]:
        if v and str(v).lower() in ('nan', 'none', ''):
            return None
        return str(v).strip() if v else None


class EnrichedChunk(BaseModel):
    """Enriched data ready for vector database (Qdrant)."""

    id: str
    full_text: str = Field(..., description="Combined question + transcription")
    payload: dict = Field(..., description="Metadata for frontend")
    sparse_vector: Optional[dict] = None
