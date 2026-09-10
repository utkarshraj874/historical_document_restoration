"""Streamlit client for the Historical Document Restoration FastAPI service.

Run with: streamlit run app/streamlit_ui.py
Set API_URL to point at a deployed API, if it is not running locally.
"""

import io
import os
from typing import Any

import requests
import streamlit as st
from PIL import Image

API_URL = os.getenv("API_URL", "http://127.0.0.1:8001").rstrip("/")
REQUEST_TIMEOUT = 120

st.set_page_config(page_title="Archive Restore", page_icon="📜", layout="wide")
st.markdown(
    """<style>
    .block-container { max-width: 1250px; padding-top: 2rem; }
    [data-testid="stMetric"] { background: #f7f3eb; border-radius: 10px; padding: .5rem; }
    </style>""",
    unsafe_allow_html=True,
)


def init_state() -> None:
    for key, value in {
        "token": None, "user": None, "selected_document_id": None,
        "result": None, "delete_confirm_id": None,
    }.items():
        st.session_state.setdefault(key, value)


def error_message(response: requests.Response) -> str:
    try:
        detail = response.json().get("detail")
        if isinstance(detail, list):
            return "; ".join(item.get("msg", str(item)) for item in detail)
        return str(detail or response.text or f"Request failed ({response.status_code})")
    except ValueError:
        return response.text or f"Request failed ({response.status_code})"


def api_request(method: str, path: str, **kwargs: Any) -> requests.Response | None:
    headers = kwargs.pop("headers", {})
    if st.session_state.token:
        headers["Authorization"] = f"Bearer {st.session_state.token}"
    try:
        response = requests.request(
            method, f"{API_URL}{path}", headers=headers,
            timeout=REQUEST_TIMEOUT, **kwargs,
        )
    except requests.RequestException as exc:
        st.error(f"Cannot reach the API at {API_URL}. {exc}")
        return None
    if response.status_code == 401:
        st.session_state.token, st.session_state.user = None, None
        st.warning("Your session has expired. Please sign in again.")
    return response


def image_from_api(path: str | None) -> Image.Image | None:
    if not path:
        return None
    if path.startswith(("https://", "http://")):
        # Vercel Blob returns a complete public URL, not a /uploads path.
        url = path
    else:
        normalized = path.replace("\\", "/")
        marker = "uploads/"
        position = normalized.lower().find(marker)
        url_path = normalized[position:] if position >= 0 else normalized.lstrip("/")
        url = f"{API_URL}/{url_path}"
    try:
        response = requests.get(url, timeout=REQUEST_TIMEOUT)
    except requests.RequestException as exc:
        st.warning(f"Could not load enhanced image. {exc}")
        return None
    if response and response.ok:
        try:
            return Image.open(io.BytesIO(response.content))
        except OSError:
            st.warning("The enhanced-image response was not a valid image.")
    return None


def load_result(document_id: int, quiet: bool = False) -> dict[str, Any] | None:
    response = api_request("GET", f"/documents/{document_id}/ocr")
    if response and response.ok:
        st.session_state.result = response.json()
        return st.session_state.result
    if response and response.status_code != 404 and not quiet:
        st.error(error_message(response))
    return None


def show_result(result: dict[str, Any]) -> None:
    st.subheader("Restoration workspace")
    col1, col2, col3 = st.columns(3)
    col1.metric("OCR confidence", f"{(result.get('average_confidence') or 0):.1f}%")
    col2.metric("Language", result.get("language") or "Unknown")
    col3.metric("Processing time", f"{(result.get('processing_time') or 0):.2f} sec")
    left, right = st.columns(2)
    with left:
        st.markdown("#### Enhanced document")
        image = image_from_api(result.get("enhanced_image"))
        if image:
            st.image(image, use_container_width=True)
        else:
            st.info("The enhanced image is unavailable.")
    with right:
        st.markdown("#### OCR text")
        st.text_area("Raw OCR output", result.get("raw_text") or "", height=350,
                     disabled=True, key=f"raw_{result['id']}")

    st.markdown("#### Restored text")
    corrected = result.get("corrected_text") or ""
    if corrected:
        st.text_area("AI-corrected transcription", corrected, height=350,
                     key=f"corrected_{result['id']}")
        st.download_button("Download restored text", corrected,
                           file_name=f"document_{result['document_id']}_restored.txt",
                           mime="text/plain")
    else:
        st.info("OCR is complete. Select “Restore text” to correct the transcription with the configured LLM.")


def login_or_register() -> None:
    st.title("📜 Archive Restore")
    st.caption("Enhance historical documents, extract their text, and create a clean transcription.")
    login_tab, register_tab = st.tabs(["Sign in", "Create account"])
    with login_tab:
        with st.form("login_form"):
            email = st.text_input("Email", key="login_email")
            password = st.text_input("Password", type="password", key="login_password")
            submitted = st.form_submit_button("Sign in", type="primary", use_container_width=True)
        if submitted:
            response = api_request("POST", "/login", data={"username": email, "password": password})
            if response and response.ok:
                st.session_state.token = response.json()["access_token"]
                me = api_request("GET", "/me")
                st.session_state.user = me.json() if me and me.ok else {"email": email}
                st.rerun()
            elif response:
                st.error(error_message(response))
    with register_tab:
        with st.form("register_form", clear_on_submit=True):
            email = st.text_input("Email", key="register_email")
            password = st.text_input("Password", type="password", key="register_password")
            confirm = st.text_input("Confirm password", type="password")
            submitted = st.form_submit_button("Create account", use_container_width=True)
        if submitted:
            if not email or not password:
                st.error("Email and password are required.")
            elif password != confirm:
                st.error("Passwords do not match.")
            else:
                response = api_request("POST", "/register", json={"email": email, "password": password})
                if response and response.ok:
                    st.success("Account created. You can now sign in.")
                elif response:
                    st.error(error_message(response))


def dashboard() -> None:
    user_email = (st.session_state.user or {}).get("email", "signed-in user")
    with st.sidebar:
        st.title("📜 Archive Restore")
        st.caption(f"Signed in as {user_email}")
        st.caption(f"API: {API_URL}")
        if st.button("Sign out", use_container_width=True):
            for key in ("token", "user", "selected_document_id", "result", "delete_confirm_id"):
                st.session_state[key] = None
            st.rerun()

    st.title("Document archive")
    st.caption("Upload an image, run OCR, then restore its transcription when ready.")
    with st.expander("Upload a document", expanded=True):
        with st.form("upload_form", clear_on_submit=True):
            title = st.text_input("Document title", placeholder="e.g. 1892 parish register")
            file = st.file_uploader("Image file", type=["png", "jpg", "jpeg"])
            upload = st.form_submit_button("Upload document", type="primary")
        if upload:
            if not file:
                st.error("Choose an image to upload.")
            else:
                response = api_request(
                    "POST", "/upload",
                    data={"title": title.strip() or file.name, "status": "uploaded"},
                    files={"file": (file.name, file.getvalue(), file.type or "application/octet-stream")},
                )
                if response and response.ok:
                    st.session_state.selected_document_id = response.json()["document_id"]
                    st.session_state.result = None
                    st.success("Document uploaded.")
                    st.rerun()
                elif response:
                    st.error(error_message(response))

    response = api_request("GET", "/documents")
    documents = response.json() if response and response.ok else []
    if response and not response.ok:
        st.error(error_message(response))
        return
    if not documents:
        st.info("Your archive is empty. Upload an image to begin.")
        return

    document_map = {doc["id"]: doc for doc in documents}
    ids = list(document_map)
    default_index = ids.index(st.session_state.selected_document_id) if st.session_state.selected_document_id in document_map else 0
    selected_id = st.selectbox(
        "Select a document", options=ids, index=default_index,
        format_func=lambda doc_id: f"#{doc_id} · {document_map[doc_id]['title']} ({document_map[doc_id]['status']})",
    )
    if selected_id != st.session_state.selected_document_id:
        st.session_state.selected_document_id, st.session_state.result = selected_id, None
    doc = document_map[selected_id]

    ocr_col, restore_col, delete_col = st.columns([2, 2, 1])
    with ocr_col:
        if st.button("Run OCR", type="primary", use_container_width=True):
            with st.spinner("Enhancing image and extracting text…"):
                response = api_request("POST", f"/documents/{selected_id}/ocr")
            if response and response.ok:
                st.session_state.result = response.json()
                st.success("OCR completed.")
            elif response:
                st.error(error_message(response))
    with restore_col:
        # Do not disable this from the list status: it can be stale immediately
        # after OCR. The API validates that an OCR result exists before restoring.
        if st.button("Restore text", use_container_width=True):
            with st.spinner("Correcting transcription…"):
                response = api_request("POST", f"/documents/{selected_id}/restore")
            if response and response.ok:
                st.session_state.result = response.json()
                st.success("Text restoration completed.")
            elif response:
                st.error(error_message(response))
    with delete_col:
        if st.button("Delete", use_container_width=True):
            st.session_state.delete_confirm_id = selected_id

    if st.session_state.delete_confirm_id == selected_id:
        st.warning(f"Delete “{doc['title']}”? This removes its database record.")
        confirm_col, cancel_col = st.columns(2)
        if confirm_col.button("Yes, delete permanently", type="primary"):
            response = api_request("DELETE", f"/documents/{selected_id}")
            if response and response.ok:
                st.session_state.selected_document_id = None
                st.session_state.result = None
                st.session_state.delete_confirm_id = None
                st.rerun()
            elif response:
                st.error(error_message(response))
        if cancel_col.button("Cancel"):
            st.session_state.delete_confirm_id = None
            st.rerun()

    result = st.session_state.result
    if not result or result.get("document_id") != selected_id:
        result = load_result(selected_id, quiet=True)
    if result:
        show_result(result)
    else:
        st.info("No OCR result for this document yet. Use “Run OCR” to start.")


init_state()
if st.session_state.token:
    dashboard()
else:
    login_or_register()
