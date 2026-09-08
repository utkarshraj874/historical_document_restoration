import os
import shutil
from datetime import datetime

from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.document import Document
from app.core.dependencies import get_db, get_current_user

router = APIRouter()


@router.post("/upload")
def upload_document(
    title: str = Form(...),
    status: str = Form(...),
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    upload_dir = "uploads"
    os.makedirs(upload_dir, exist_ok=True)

    file_path = os.path.join(upload_dir, file.filename)
    
    
    
    try:
        # Save file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Save metadata
        doc = Document(
            title=title,
            filename=file.filename,
            file_path=file_path,
            file_type=file.content_type,
            status=status,
            owner_id=current_user.id,
            created_at=datetime.utcnow(),
        )

        db.add(doc)
        db.commit()
        db.refresh(doc)

        return {
            "message": "Uploaded successfully",
            "document_id": doc.id,
        }

    except Exception as e:
        db.rollback()

        # Remove file if DB operation failed
        if os.path.exists(file_path):
            os.remove(file_path)

        raise HTTPException(
            status_code=500,
            detail=str(e),
        )


@router.get("/documents")
def get_documents(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    docs = db.query(Document).filter(
        Document.owner_id == current_user.id
    ).all()

    return [
        {
            "id": doc.id,
            "title": doc.title,
            "filename": doc.filename,
            "file_type": doc.file_type,
            "status": doc.status
        }
        for doc in docs
    ]


@router.get("/documents/{document_id}")
def get_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    doc = db.query(Document).filter(
        Document.id == document_id,
        Document.owner_id == current_user.id
    ).first()

    if not doc:
        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )

    return {
        "id": doc.id,
        "title": doc.title,
        "filename": doc.filename,
        "file_type": doc.file_type,
        "status": doc.status
    }


@router.delete("/documents/{document_id}")
def delete_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Find the document owned by the current user
    doc = db.query(Document).filter(
        Document.id == document_id,
        Document.owner_id == current_user.id
    ).first()

    if not doc:
        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )

    # Delete and commit
    db.delete(doc)
    db.commit()

    return {"message": "Document deleted successfully"}