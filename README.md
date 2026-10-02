# AI Resume Analyzer with Skill Extraction, Rule-Based Scoring, and Visualization Dashboard

A full-stack resume-analysis application that parses PDF resumes, extracts skills, calculates deterministic category scores, persists results using SQLAlchemy, ranks candidates in database order, and visualizes live data.

## 1. Create the PostgreSQL database

Install PostgreSQL, then create a database:

```sql
CREATE DATABASE resume_analyzer;
```

Copy `backend/.env.example` to `backend/.env` and set `DATABASE_URL`, for example:

```env
DATABASE_URL=postgresql+psycopg://postgres:YOUR_PASSWORD@localhost:5432/resume_analyzer
```

SQLite is used as a local fallback if no environment file is configured, but PostgreSQL is the intended persistent deployment database.

## 2. Start the backend

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn main:app --reload
```

Open `http://localhost:8000/docs` for interactive API documentation.

## 3. Start the frontend

In a second terminal:

```powershell
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`.

## 4. Test the workflow

1. Open **Upload resumes**.
2. Drag/drop or browse for up to 150 text-based PDF resumes (10 MB each).
3. Select **Analyze all resumes**. Each PDF is processed independently; failed files are reported without stopping the batch.
4. Open **Dashboard** to see live database metrics and charts.
5. Open **Candidates** to search, filter, page through the database-ranked table, view details, or delete a record.
6. Use **Job match** to paste a job description and see matching/missing skills for every stored candidate.

The backend always queries `overall_score DESC, candidate_name ASC`, so rankings and dashboard records are not generated in React and survive application restarts.
