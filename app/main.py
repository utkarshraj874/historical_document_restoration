from fastapi import FastAPI
from app.api.user import router as user_router
from app.api.documents import router as user_documents
from app.api.ocr import router as ocr_router
from fastapi.staticfiles import StaticFiles
from app.services.storage_service import local_upload_directory

app = FastAPI(title = "HISTORICAL_DOCUMENT_RESTORATION" )

@app.post("/")
def root():
    return {
        "message":"project started "
    }
# Vercel's project directory is read-only; this resolves a writable runtime
# folder for local-only uploads when Blob storage has not been configured.
app.mount("/uploads",
          StaticFiles(directory=str(local_upload_directory())),
          name = "uploads"
          )
app.include_router(user_router)
app.include_router(user_documents)
app.include_router(ocr_router)
