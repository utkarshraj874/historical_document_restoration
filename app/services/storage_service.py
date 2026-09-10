"""Durable file storage with a Vercel Blob production backend.

When no Blob store is configured, the application keeps its existing local
development behaviour.  Vercel's function filesystem is ephemeral, so a
production deployment must provide ``BLOB_READ_WRITE_TOKEN``.
"""

import os
import shutil
import tempfile
import uuid
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import urlopen

from fastapi import UploadFile


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _blob_enabled() -> bool:
    return bool(os.getenv("BLOB_READ_WRITE_TOKEN"))


def local_upload_directory() -> Path:
    """Return a writable directory for local development or a Vercel runtime."""
    directory = (
        Path(tempfile.gettempdir()) / "historical-document-restoration-uploads"
        if os.getenv("VERCEL")
        else PROJECT_ROOT / "uploads"
    )
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def _blob_client():
    try:
        from vercel.blob import BlobClient
    except ModuleNotFoundError as exc:
        raise RuntimeError("Vercel Blob support is not installed.") from exc
    return BlobClient()


def _safe_name(filename: str | None) -> str:
    suffix = Path(filename or "document").suffix.lower()
    return f"{uuid.uuid4().hex}{suffix}"


def store_upload(upload: UploadFile) -> str:
    """Persist an uploaded file and return its local path or durable Blob URL."""
    filename = _safe_name(upload.filename)
    if _blob_enabled():
        blob = _blob_client().put(
            f"documents/{filename}", upload.file.read(), access="public",
            content_type=upload.content_type or "application/octet-stream",
        )
        return blob.url

    destination = local_upload_directory() / filename
    with destination.open("wb") as buffer:
        shutil.copyfileobj(upload.file, buffer)
    return str(destination)


def materialize_for_processing(path_or_url: str) -> str:
    """Return a local file path, downloading a durable object when necessary."""
    if not path_or_url.startswith(("https://", "http://")):
        return path_or_url
    suffix = Path(urlparse(path_or_url).path).suffix or ".bin"
    destination = Path(tempfile.gettempdir()) / f"ocr-source-{uuid.uuid4().hex}{suffix}"
    with urlopen(path_or_url, timeout=30) as response, destination.open("wb") as output:
        shutil.copyfileobj(response, output)
    return str(destination)


def store_generated_file(local_path: str) -> str:
    """Persist a generated image when a Blob store is configured."""
    if not _blob_enabled():
        return local_path
    source = Path(local_path)
    blob = _blob_client().put(
        f"processed/{_safe_name(source.name)}", source.read_bytes(), access="public",
        content_type="image/jpeg" if source.suffix.lower() in {".jpg", ".jpeg"} else "image/png",
    )
    return blob.url
