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

Set `DATABASE_URL`, `SECRET_KEY`, and `GROQCLOUD_API_KEY` in the Vercel
project's Environment Variables. `DATABASE_URL` must point to an externally
reachable PostgreSQL instance; `localhost` only works on your computer.

PaddleOCR is included in `requirements.txt`. After pushing this change,
redeploy the same branch and use **Redeploy without cache** so Vercel installs
the current requirements file. If PaddleOCR cannot be packaged by your Vercel
plan, the rest of the API still starts and the OCR endpoint responds with 503;
run the OCR worker in the provided Docker deployment or another compute
service in that case.

Vercel function storage is temporary. Do not rely on `uploads/` for
production document storage; use object storage for uploaded files.

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
