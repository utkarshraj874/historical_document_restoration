from fastapi import FastAPI
from app.api.user import router as user_router
from app.api.documents import router as user_documents
from app.api.ocr import router as ocr_router
from fastapi.staticfiles import StaticFiles

app = FastAPI(title = "HISTORICAL_DOCUMENT_RESTORATION" )

@app.post("/")
def root():
    return {
        "message":"project started "
    }
app.mount("/uploads",
          StaticFiles(directory="uploads"),
          name = "uploads"
          )
app.include_router(user_router)
app.include_router(user_documents)
app.include_router(ocr_router)
