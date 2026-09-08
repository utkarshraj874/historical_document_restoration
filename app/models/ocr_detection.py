from sqlalchemy import Integer, ForeignKey, String, Float, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.base import Base
#from app.models.ocr_result import OCRResult


# in ocr_detection.py
def get_result_class():
    from app.models.ocr_result import OCRResult
    return OCRResult

class OCRDetection(Base):
    __tablename__ = "ocr_detections"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    ocr_result_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("ocr_results.id", ondelete="CASCADE"),
        nullable=False
    )

    text: Mapped[str] = mapped_column(
        String,
        nullable=False
    )

    confidence: Mapped[list[float]] = mapped_column(
        Float,
        nullable=False
    )

    bounding_box: Mapped[list] = mapped_column(
        JSON,
        nullable=False
    )

    ocr_result: Mapped["get_result_class"] = relationship(
        "OCRResult",
        back_populates="detections"
    )

