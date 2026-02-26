# AI-Ready Knowledge Backend – Phase 1

Phase 1 delivers a clean, production-ready backend with authentication, user management, file upload/storage, and a simple Streamlit UI for testing and demonstration.

This phase is intentionally LLM/RAG-free and focuses on building a strong backend foundation.

---

## Features (Phase 1)

### Authentication & Users
- JWT-based authentication
- Login endpoint
- Create account
- Role-based access (user / admin)
- Active / inactive users
- Admin-only operations

### File Management
- Upload files (any type)
- Store file metadata in database
- Secure download (owner or admin)
- Delete files (owner or admin)
- SHA256 hashing
- Disk storage abstraction

### Streamlit UI (Demo Only)
- Login / Logout
- Create account
- Upload files
- List my files
- Download & delete files

NOTE: Streamlit is only for testing/demo purposes and not intended as a production UI.

### Database & Migrations
- SQLAlchemy ORM
- Alembic migrations
- SQLite for local development

---


## Environment Setup

### Create virtual environment
python -m venv .venv

Activate (Windows):
.\\.venv\\Scripts\\activate

Activate (Linux / macOS):
source .venv/bin/activate

---

### Install dependencies
pip install -r requirements.txt

---

### Environment variables

Create .env from example:
cp .env.example .env

Edit .env:
SECRET_KEY=CHANGE_ME_TO_RANDOM_SECRET
ACCESS_TOKEN_EXPIRE_MINUTES=60
DATABASE_URL=sqlite:///./app.db

Do NOT commit .env to GitHub.

---

## Database (Alembic)

Run migrations:
alembic upgrade head

---

## Run Backend (FastAPI)

uvicorn app.main:app --reload

API: http://127.0.0.1:8000  
Swagger UI: http://127.0.0.1:8000/docs

---

## Run Streamlit UI

streamlit run streamlit_app/Home.py

UI: http://localhost:8501

---

## Phase 1 Completion Checklist

- JWT authentication
- Create account
- Role-based authorization
- File upload / download / delete
- Secure access rules
- Alembic migrations
- Streamlit demo UI
- Clean project structure

---

## Design Philosophy

- Backend-first approach
- Clear separation of concerns
- Production-ready patterns
- Minimal complexity
- Easy to extend later

---

## Next Phases (Planned)

- Phase 2: Document parsing & chunking
- Phase 3: Vector database + embeddings
- Phase 4: RAG + LLM integration
- Phase 5: Automation & orchestration

---

## Versioning

Phase 1 stable tag: v1.0-phase1

---

## Author Notes

This project represents a solid backend foundation for AI systems.
Phase 1 is intentionally frozen and considered stable.