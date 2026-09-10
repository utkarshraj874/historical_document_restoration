Historical Document Restoration
An AI-powered system to enhance old document images, extract text using OCR, and restore/correct OCR-generated text with LLMs.

🚀 Features
Upload historical documents

Image preprocessing (OpenCV)

Text extraction (PaddleOCR)

OCR confidence scoring & visualization

Text correction using Mistral AI

Store results in PostgreSQL

JWT-based authentication

REST APIs with FastAPI

Streamlit frontend

Docker & Docker Compose support

🏗️ Architecture
Code
Streamlit (Frontend)
        │
        ▼
FastAPI (Backend REST API)
        │
 ┌──────┴────────┐
 │               │
 ▼               ▼
Image Processing  PostgreSQL
 │
 ▼
PaddleOCR → Raw Text → Mistral AI → Corrected Text
🛠️ Tech Stack
Backend: Python, FastAPI, SQLAlchemy, PostgreSQL, Alembic, JWT

OCR/Image: PaddleOCR, PaddlePaddle, OpenCV, Pillow

LLM: Mistral AI, LangChain

Frontend: Streamlit

Deployment: Docker, Docker Compose

📂 Project Structure
Code
historical-document-restoration/
├── app/ (FastAPI backend)
├── frontend/ (Streamlit UI)
├── alembic/ (migrations)
├── uploads/
├── .env
├── .gitignore
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
⚙️ Installation
bash
git clone <your-repo-url>
cd historical-document-restoration
python -m venv venv
venv\Scripts\activate   # Windows
source venv/bin/activate # Linux/Mac
pip install -r requirements.txt
🗄️ Database Setup
Create PostgreSQL DB: historical_document

Configure .env:

Code
DATABASE_URL=postgresql+psycopg2://postgres:<password>@localhost:5432/historical_document
MISTRAL_API_KEY=<your-mistral-api-key>
SECRET_KEY=<your-secret-key>

### Vercel deployment

Set these in the Vercel project's Environment Variables:

- `DATABASE_URL` — an externally reachable PostgreSQL connection string.
  `localhost` only works on your computer.
- `SECRET_KEY` — a long random value used to sign JWTs.
- `GROQCLOUD_API_KEY` — the API key used for text restoration.
- `BLOB_READ_WRITE_TOKEN` — added automatically when you create and connect a
  **public Vercel Blob** store in the project Storage tab. It makes uploaded
  and enhanced images durable across serverless invocations.

Then import the repository in Vercel (Framework Preset: **Other**) and deploy.
Vercel detects `app/main.py` as the FastAPI application. The deployment uses
Python 3.12 and allows OCR requests to run for up to 300 seconds.

`vercel.json` is intentionally comment-free because JSON does not support
comments. Its `excludeFiles` rule keeps development files out of the function,
and `maxDuration: 300` gives OCR enough processing time.

PaddleOCR is deliberately **not** included in `requirements.txt`: its
PaddlePaddle/PaddleX runtime makes the deployment about 1.2 GB, above Vercel's
standard 500 MB Python Function limit. The Vercel API deploys without it and
returns HTTP 503 from the OCR endpoint with an explanation. The complete OCR
runtime is in `requirements.ocr.txt`; the supplied Dockerfile installs that
file, so use the Docker deployment (or a separate worker service) for OCR.

After pushing this change, redeploy the same branch using **Redeploy without
cache** so Vercel discards the previous oversized dependency bundle.

Without `BLOB_READ_WRITE_TOKEN`, uploads fall back to a temporary function
directory and are suitable only for local development. Vercel Function request
bodies are limited to 4.5 MB, so use client-side Blob uploads if documents can
exceed that limit.

Run migrations:

bash
alembic upgrade head
▶️ Run
Backend (FastAPI)

bash
uvicorn app.main:app --reload --port 8001
API docs → http://127.0.0.1:8001/docs

Frontend (Streamlit)

bash
streamlit run frontend/streamlit_app.py
🔌 API Endpoints
POST /auth/register → Register

POST /auth/login → Login

POST /upload → Upload document

POST /documents/{id}/ocr → Run OCR + restoration

GET /documents/{id}/ocr → Get OCR result

🐳 Docker
bash
docker compose up --build
docker compose up -d   # run in background
docker compose down    # stop
📊 Output
Enhanced document image

Corrected/restored text

🚧 Future Improvements
Handwritten text recognition

Multi-language OCR

Super-resolution & deblurring

Cloud storage integration
