from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.document import Document
from app.models.ocr_result import OCRResult
from app.models.ocr_detection import OCRDetection

from app.core.dependencies import (
    get_db,
    get_current_user
)

from app.services.image_service import preprocess_image
from app.services.ocr_service import OCRService
from app.services.ocr_visualization_service import (
    create_ocr_visualization
)
from app.services.test_restoration import RestorationService

from app.schemas.ocr import OCRResultResponse


router = APIRouter(
    prefix="/documents",
    tags=["OCR"]
)


# ============================================================
# 1. RUN OCR
# ============================================================

@router.post(
    "/{document_id}/ocr",
    response_model=OCRResultResponse
)
def run_ocr(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    # --------------------------------------------------------
    # STEP 1 - FIND DOCUMENT
    # --------------------------------------------------------

    doc = (
        db.query(Document)
        .filter(
            Document.id == document_id,
            Document.owner_id == current_user.id
        )
        .first()
    )

    if not doc:
        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )

    # --------------------------------------------------------
    # STEP 2 - PREPROCESS IMAGE
    # --------------------------------------------------------

    try:

        enhanced_image_path = preprocess_image(
            doc.file_path
        )

        print(
            "Enhanced image:",
            enhanced_image_path
        )

    except Exception as e:

        print("PREPROCESSING ERROR:", str(e))

        raise HTTPException(
            status_code=500,
            detail=f"Image preprocessing failed: {str(e)}"
        )

    # --------------------------------------------------------
    # STEP 3 - RUN OCR
    # --------------------------------------------------------

    try:

        ocr_service = OCRService()

        ocr_data = ocr_service.process_image(
            enhanced_image_path
        )

        print("OCR completed")

        print(
            "Total OCR detections:",
            len(ocr_data["detections"])
        )

    except Exception as e:

        print("OCR ERROR:", str(e))

        raise HTTPException(
            status_code=500,
            detail=f"OCR processing failed: {str(e)}"
        )

    # --------------------------------------------------------
    # STEP 4 - OCR VISUALIZATION
    # --------------------------------------------------------

    visualization_path = None

    try:

        visualization_path = (
            enhanced_image_path.replace(
                "_enhanced",
                "_ocr"
            )
        )

        create_ocr_visualization(
            image_path=enhanced_image_path,
            detections=ocr_data["detections"],
            output_path=visualization_path
        )

        print(
            "OCR visualization created:",
            visualization_path
        )

    except Exception as e:

        print(
            "VISUALIZATION ERROR:",
            str(e)
        )

    # --------------------------------------------------------
    # STEP 5 - CREATE OCR RESULT
    # --------------------------------------------------------

    try:

        ocr_result = OCRResult(
            document_id=doc.id,

            raw_text=ocr_data["raw_text"],

            corrected_text=None,

            enhanced_image=enhanced_image_path,

            average_confidence=(
                ocr_data["average_confidence"]
            ),

            language=ocr_data["language"],

            processing_time=(
                ocr_data["processing_time"]
            )
        )

        db.add(ocr_result)

        db.flush()

    except Exception as e:

        db.rollback()

        print(
            "OCR RESULT ERROR:",
            str(e)
        )

        raise HTTPException(
            status_code=500,
            detail=f"Failed to create OCR result: {str(e)}"
        )

    # --------------------------------------------------------
    # STEP 6 - SAVE OCR DETECTIONS
    # --------------------------------------------------------

    try:

        for detection in ocr_data["detections"]:

            ocr_detection = OCRDetection(

                ocr_result_id=ocr_result.id,

                text=detection["text"],

                confidence=detection["confidence"],

                bounding_box=detection["bounding_box"]
            )

            db.add(ocr_detection)

    except Exception as e:

        db.rollback()

        print(
            "OCR DETECTION ERROR:",
            str(e)
        )

        raise HTTPException(
            status_code=500,
            detail=(
                f"Failed to save OCR detections: {str(e)}"
            )
        )

    # --------------------------------------------------------
    # STEP 7 - UPDATE DOCUMENT
    # --------------------------------------------------------

    doc.status = "ocr_completed"

    # --------------------------------------------------------
    # STEP 8 - COMMIT
    # --------------------------------------------------------

    try:

        db.commit()

        db.refresh(ocr_result)

        print(
            "OCR result saved successfully"
        )

    except Exception as e:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=(
                f"Failed to save OCR result: {str(e)}"
            )
        )

    # --------------------------------------------------------
    # RETURN RAW OCR RESULT
    # --------------------------------------------------------

    return ocr_result


# ============================================================
# 2. RESTORE OCR TEXT
# ============================================================

@router.post(
    "/{document_id}/restore",
    response_model=OCRResultResponse
)
def restore_text(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    # --------------------------------------------------------
    # STEP 1 - FIND DOCUMENT
    # --------------------------------------------------------

    doc = (
        db.query(Document)
        .filter(
            Document.id == document_id,
            Document.owner_id == current_user.id
        )
        .first()
    )

    if not doc:

        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )

    # --------------------------------------------------------
    # STEP 2 - GET LATEST OCR RESULT
    # --------------------------------------------------------

    ocr_result = (
        db.query(OCRResult)
        .filter(
            OCRResult.document_id == document_id
        )
        .order_by(
            OCRResult.created_at.desc()
        )
        .first()
    )

    if not ocr_result:

        raise HTTPException(
            status_code=404,
            detail=(
                "OCR result not found. "
                "Run OCR first."
            )
        )

    # --------------------------------------------------------
    # STEP 3 - CHECK RAW TEXT
    # --------------------------------------------------------

    if not ocr_result.raw_text:

        raise HTTPException(
            status_code=400,
            detail="No OCR text available for restoration."
        )

    # --------------------------------------------------------
    # STEP 4 - RUN MISTRAL RESTORATION
    # --------------------------------------------------------

    try:

        restoration_service = RestorationService()

        corrected_text = (
            restoration_service.correct_text(
                ocr_result.raw_text
            )
        )

        print(
            "Text restoration completed"
        )

    except Exception as e:

        error_message = str(e)

        print(
            "RESTORATION ERROR:",
            error_message
        )

        if (
            "429" in error_message
            or "rate_limit" in error_message.lower()
            or "rate limit" in error_message.lower()
        ):

            raise HTTPException(
                status_code=429,
                detail=(
                    "Mistral API rate limit exceeded. "
                    "Please try again later."
                )
            )

        raise HTTPException(
            status_code=500,
            detail=(
                f"Text restoration failed: "
                f"{error_message}"
            )
        )

    # --------------------------------------------------------
    # STEP 5 - SAVE CORRECTED TEXT
    # --------------------------------------------------------

    try:

        ocr_result.corrected_text = corrected_text

        doc.status = "restoration_completed"

        db.commit()

        db.refresh(ocr_result)

        print(
            "Corrected text saved successfully"
        )

    except Exception as e:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=(
                f"Failed to save corrected text: "
                f"{str(e)}"
            )
        )

    # --------------------------------------------------------
    # RETURN RESTORED RESULT
    # --------------------------------------------------------

    return ocr_result


# ============================================================
# 3. GET OCR RESULT
# ============================================================

@router.get(
    "/{document_id}/ocr",
    response_model=OCRResultResponse
)
def get_ocr_result(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    # --------------------------------------------------------
    # CHECK DOCUMENT
    # --------------------------------------------------------

    doc = (
        db.query(Document)
        .filter(
            Document.id == document_id,
            Document.owner_id == current_user.id
        )
        .first()
    )

    if not doc:

        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )

    # --------------------------------------------------------
    # GET LATEST OCR RESULT
    # --------------------------------------------------------

    ocr_result = (
        db.query(OCRResult)
        .filter(
            OCRResult.document_id == document_id
        )
        .order_by(
            OCRResult.created_at.desc()
        )
        .first()
    )

    if not ocr_result:

        raise HTTPException(
            status_code=404,
            detail="OCR result not found"
        )

    return ocr_result