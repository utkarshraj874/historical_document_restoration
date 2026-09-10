from fastapi import FastAPI
from app.api.user import router as user_router
from app.api.documents import router as user_documents
from app.api.ocr import router as ocr_router
from fastapi.staticfiles import StaticFiles
from app.services.storage_service import local_upload_directory

app = FastAPI(title = "HISTORICAL_DOCUMENT_RESTORATION" )

# A browser requests the deployment URL with GET. Keeping POST also preserves
# the original API behaviour for any existing client that used that method.
@app.api_route("/", methods=["GET", "POST"], tags=["Health"])
def root():
    return {
        "message": "Historical Document Restoration API is running.",
        "docs": "/docs",
        "streamlit_ui": "Deploy app/streamlit_ui.py separately; it is not served by this API."
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
