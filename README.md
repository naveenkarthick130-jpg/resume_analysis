# AI Resume Analyzer

A Flask web app that reads a PDF resume, extracts the candidate's details, scores
the resume, checks Applicant Tracking System (ATS) friendliness, matches the
candidate against job roles, and stores every report in MySQL.

## Features

- **PDF upload and text extraction** (`PyPDF2`) with clear errors for invalid files.
- **Resume parsing** — name, email, phone, skills, education, experience, projects,
  certifications and languages (`analysis/resume.py`).
- **Resume score (0-100)** built from weighted section checks (`analysis/advanced_scorer.py`).
- **ATS check (0-100)** with pass/fail details for keywords, contact info, sections,
  length, measurable results, and formatting (`analysis/ats_checker.py`).
- **Job matching** — every role is scored from skill overlap (70%) plus TF-IDF
  description similarity (30%), returning matched and missing skills
  (`analysis/job_match.py`).
- **Skill-gap and suggestion reports** (`analysis/skill_gap.py`, `analysis/suggestion.py`).
- **MySQL history** — save, list, open and delete saved reports (`database/`).
- **Pages** — home/upload, live result, saved report, per-role job match, history,
  plus friendly error pages.

## Project layout

```
.
├── app.py                     # Flask app: routes and the analysis pipeline
├── analysis/
│   ├── __init__.py
│   ├── advanced_scorer.py     # resume score (0-100)
│   ├── ats_checker.py         # ATS compatibility score
│   ├── job_match.py           # job role matching with skills + TF-IDF
│   ├── resume.py              # PDF text field extraction
│   ├── skill_gap.py           # required-skill gaps per job role
│   └── suggestion.py          # improvement suggestions
├── database/
│   ├── __init__.py
│   ├── save_resume.py         # MySQL read/write helpers
│   └── schema.sql             # table definition
├── templates/                 # index, result, view_resume, job_result, history, error
├── tests/                     # unittest suite (no database required)
├── uploads/                   # uploaded PDFs (created automatically)
├── .env.example               # copy to .env and fill in your MySQL password
└── requirements.txt
```

## Requirements

- Python 3.10+
- MySQL 8 (or MariaDB) running locally, or a reachable MySQL server

## Setup

1. Create and activate a virtual environment.

   ```powershell
   python -m venv venv
   venv\Scripts\activate
   ```

2. Install the dependencies.

   ```powershell
   pip install -r requirements.txt
   ```

3. Create the database and table.

   ```powershell
   mysql -u root -p < database/schema.sql
   ```

   If your shell cannot redirect, open MySQL Workbench / the MySQL CLI and run the
   contents of `database/schema.sql`:

   ```sql
   CREATE DATABASE IF NOT EXISTS resume_analyzer;
   USE resume_analyzer;

   CREATE TABLE IF NOT EXISTS resumes (
       id INT UNSIGNED NOT NULL AUTO_INCREMENT,
       name VARCHAR(255) NOT NULL,
       email VARCHAR(320) NULL,
       phone VARCHAR(50) NULL,
       skills JSON NOT NULL,
       education JSON NOT NULL,
       experience JSON NOT NULL,
       projects JSON NOT NULL,
       certifications JSON NOT NULL,
       score DECIMAL(5, 2) NOT NULL DEFAULT 0,
       ats_score DECIMAL(5, 2) NOT NULL DEFAULT 0,
       created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
       PRIMARY KEY (id),
       INDEX idx_resumes_email (email),
       INDEX idx_resumes_created_at (created_at)
   );
   ```

4. Create your `.env` file (same folder as `app.py`).

   ```powershell
   copy .env.example .env
   ```

   Then set the values:

   ```
   MYSQL_HOST=localhost
   MYSQL_PORT=3306
   MYSQL_USER=root
   MYSQL_PASSWORD=your_mysql_password
   MYSQL_DATABASE=resume_analyzer
   SECRET_KEY=any-long-random-string
   ```

## Run

```powershell
python app.py
```

Open <http://127.0.0.1:5000> and upload a PDF resume.

Routes:

| Route | Method | Purpose |
| --- | --- | --- |
| `/` | GET | Upload page |
| `/upload` | POST | Analyze the uploaded PDF and save the report |
| `/history` | GET | All saved reports |
| `/resume/<id>` | GET | Saved report detail |
| `/resume/<id>/job/<slug>` | GET | Detailed match for one job role |
| `/resume/<id>/delete` | POST | Delete a saved report |
| `/health` | GET | JSON health check |

## Tests

The test suite runs the analyzers only, so MySQL is not needed:

```powershell
python -m unittest discover -s tests -t . -v
```

## Notes and limitations

- The database stores skills, education, experience, projects and certifications as
  JSON columns; they are decoded back into Python lists when reports are read.
- Scanned/image-only PDFs cannot be parsed — upload a text-based PDF.
- If MySQL is unreachable the analysis still renders, with a warning that the report
  could not be saved; the history page shows the connection error instead of crashing.
- Uploaded PDFs are stored in `uploads/` with a sanitised, unique file name.
