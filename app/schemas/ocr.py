from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class OCRDetectionResponse(BaseModel):

    id: int

    text: str

    confidence: float

    bounding_box: list[float]

    model_config = ConfigDict(from_attributes=True)


class OCRResultResponse(BaseModel):

    id: int

    document_id: int

    raw_text: str

    corrected_text: str | None

    enhanced_image: str | None

    average_confidence: float | None

    language: str | None

    processing_time: float | None

    created_at: datetime

    detections: list[OCRDetectionResponse] = Field(
        default_factory=list
    )

    model_config = ConfigDict(from_attributes=True)

