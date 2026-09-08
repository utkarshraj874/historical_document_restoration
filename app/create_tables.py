from app.core.database import engine

from app.core.base import Base
from app.models.user import User 
from app.models.document import Document
from app.models.ocr_detection import OCRDetection
from app.models.ocr_result import OCRResult

Base.metadata.create_all(bind=engine)
print("tables created sucessfully")