import streamlit as st
import requests
from PIL import Image
import io


# =====================================================
# CONFIG
# =====================================================

API_URL = "http://127.0.0.1:8001"


# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(
    page_title="Historical Document Restoration",
    page_icon="📜",
    layout="wide"
)


# =====================================================
# TITLE
# =====================================================

st.title("📜 Historical Document Restoration")

st.write(
    "Upload a historical document to enhance the image "
    "and restore its text using OCR and AI."
)


# =====================================================
# SESSION STATE
# =====================================================

if "token" not in st.session_state:
    st.session_state.token = None

if "document_id" not in st.session_state:
    st.session_state.document_id = None


# =====================================================
# SIDEBAR LOGIN
# =====================================================

st.sidebar.title("Login")

email = st.sidebar.text_input("Email")

password = st.sidebar.text_input(
    "Password",
    type="password"
)


if st.sidebar.button("Login"):

    try:

        response = requests.post(
            f"{API_URL}/login",
            data={
                "username": email,
                "password": password
            }
        )

        if response.status_code == 200:

            login_data = response.json()

            st.session_state.token = (
                login_data["access_token"]
            )

            st.sidebar.success(
                "Login successful!"
            )

        else:

            st.sidebar.error(
                response.json().get(
                    "detail",
                    "Login failed"
                )
            )

    except requests.exceptions.ConnectionError:

        st.sidebar.error(
            "FastAPI server is not running."
        )

    except Exception as e:

        st.sidebar.error(str(e))


# =====================================================
# LOGIN CHECK
# =====================================================

if not st.session_state.token:

    st.info(
        "Please login first using the sidebar."
    )

    st.stop()


# =====================================================
# UPLOAD
# =====================================================

st.header("Upload Historical Document")

uploaded_file = st.file_uploader(
    "Choose an image",
    type=[
        "png",
        "jpg",
        "jpeg"
    ]
)


# =====================================================
# SHOW ORIGINAL IMAGE
# =====================================================

if uploaded_file:

    original_image = Image.open(
        uploaded_file
    )

    st.subheader("Original Image")

    st.image(
        original_image,
        caption="Original Document",
        use_container_width=True
    )


# =====================================================
# RESTORE BUTTON
# =====================================================

if uploaded_file:

    if st.button(
        "✨ Restore Document",
        type="primary"
    ):

        headers = {
            "Authorization":
                f"Bearer {st.session_state.token}"
        }


        # =================================================
        # STEP 1 — UPLOAD DOCUMENT
        # =================================================

        try:

            files = {
                "file": (
                    uploaded_file.name,
                    uploaded_file.getvalue(),
                    uploaded_file.type
                )
            }

            data = {
                "title": uploaded_file.name,
                "status": "uploaded"
            }

            with st.spinner(
                "Uploading document..."
            ):

                upload_response = requests.post(

                    f"{API_URL}/upload",

                    headers=headers,

                    files=files,

                    data=data
                )


            if upload_response.status_code not in [
                200,
                201
            ]:

                st.error(
                    "Document upload failed."
                )

                st.code(
                    upload_response.text
                )

                st.stop()


            upload_data = (
                upload_response.json()
            )

            document_id = (
                upload_data["document_id"]
            )

            st.session_state.document_id = (
                document_id
            )


        except Exception as e:

            st.error(
                f"Upload error: {str(e)}"
            )

            st.stop()


        # =================================================
        # STEP 2 — RUN OCR + RESTORATION
        # =================================================

        try:

            with st.spinner(
                "Processing document..."
            ):

                ocr_response = requests.post(

                    f"{API_URL}/documents/"
                    f"{document_id}/ocr",

                    headers=headers
                )


            if ocr_response.status_code != 200:

                st.error(
                    "OCR / restoration failed."
                )

                st.code(
                    ocr_response.text
                )

                st.stop()


            result = ocr_response.json()


        except requests.exceptions.ConnectionError:

            st.error(
                "Could not connect to FastAPI."
            )

            st.stop()


        except Exception as e:

            st.error(
                f"Processing error: {str(e)}"
            )

            st.stop()


        # =================================================
        # SUCCESS
        # =================================================

        st.success(
            "Document restored successfully! 🎉"
        )


        # =================================================
        # RESULT — IMAGES
        # =================================================

        st.header("Restoration Result")

        col1, col2 = st.columns(2)


        # -------------------------------------------------
        # ORIGINAL
        # -------------------------------------------------

        with col1:

            st.subheader(
                "Original Image"
            )

            st.image(
                original_image,
                use_container_width=True
            )


        # -------------------------------------------------
        # ENHANCED IMAGE
        # -------------------------------------------------

        with col2:

            st.subheader(
                "Enhanced Image"
            )

            enhanced_image_path = (
                result.get("enhanced_image")
            )

            if enhanced_image_path:

                # -----------------------------------------
                # Convert Windows path to URL path
                # -----------------------------------------

                image_url = (
                    enhanced_image_path
                    .replace("\\", "/")
                )

                # -----------------------------------------
                # FastAPI static files
                # -----------------------------------------

                image_url = (
                    f"{API_URL}/{image_url}"
                )

                try:

                    image_response = requests.get(
                        image_url
                    )

                    if image_response.status_code == 200:

                        enhanced_image = Image.open(
                            io.BytesIO(
                                image_response.content
                            )
                        )

                        st.image(
                            enhanced_image,
                            caption="Enhanced Document",
                            use_container_width=True
                        )

                    else:

                        st.warning(
                            "Enhanced image could not "
                            "be loaded."
                        )

                except Exception as e:

                    st.warning(
                        f"Image loading error: {e}"
                    )

            else:

                st.warning(
                    "Enhanced image was not returned."
                )


        # =================================================
        # CORRECTED TEXT
        # =================================================

        st.header(
            "📝 Corrected / Restored Text"
        )

        corrected_text = result.get(
            "corrected_text",
            ""
        )


        st.text_area(
            "Restored Text",
            value=corrected_text,
            height=450
        )


        # =================================================
        # DOWNLOAD TEXT
        # =================================================

        st.download_button(

            label="⬇️ Download Corrected Text",

            data=corrected_text,

            file_name=(
                f"document_{document_id}"
                "_restored.txt"
            ),

            mime="text/plain"
        )


        # =================================================
        # PROCESSING INFO
        # =================================================

        with st.expander(
            "Processing Information"
        ):

            st.write(
                "Document ID:",
                result.get(
                    "document_id"
                )
            )

            st.write(
                "OCR Confidence:",
                result.get(
                    "average_confidence"
                )
            )

            st.write(
                "Language:",
                result.get(
                    "language"
                )
            )

            st.write(
                "Processing Time:",
                result.get(
                    "processing_time"
                )
            )