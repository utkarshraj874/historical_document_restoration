from sqlalchemy import String, Integer, Float, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.base import Base
from datetime import datetime
from app.models.document import Document
from app.models.ocr_detection import OCRDetection

class OCRResult(Base):
    __tablename__ = "ocr_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    document_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False
    )

    raw_text: Mapped[str] = mapped_column(String, nullable=False)
    corrected_text: Mapped[str | None] = mapped_column(
        String,
        nullable=True
    )

    enhanced_image: Mapped[str | None] = mapped_column(
        String,
        nullable=True
    )
    average_confidence: Mapped[float] = mapped_column(Float, nullable=False)
    language: Mapped[str] = mapped_column(String, nullable=True)
    processing_time: Mapped[float] = mapped_column(Float, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    
    )


    document: Mapped["Document"] = relationship(
    
        "Document",
        back_populates="ocr_results"
    )

    detections: Mapped[list["OCRDetection"]] = relationship(
        "OCRDetection",
        back_populates="ocr_result",
        cascade="all, delete-orphan"
    )
