"""AI Resume Analyzer - Flask entry point.

Upload a PDF resume, run every analyzer on it, store the report in MySQL,
and browse past reports.
"""

import os
import re
import uuid

from flask import Flask, abort, redirect, render_template, request, url_for
from mysql.connector import Error as MySQLError
from PyPDF2 import PdfReader

from analysis.advanced_scorer import calculate_advanced_score
from analysis.ats_checker import check_ats
from analysis.job_match import analyze_jobs
from analysis.resume import (
    extract_certifications,
    extract_education,
    extract_email,
    extract_experience,
    extract_languages,
    extract_name,
    extract_phone,
    extract_projects,
    extract_skills,
)
from analysis.skill_gap import analyze_skill_gap
from analysis.suggestion import generate_suggestions
from database import (
    database_error_message,
    delete_resume,
    get_resume,
    get_resumes,
    save_resume,
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-key-change-me")
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 8 * 1024 * 1024  # 8 MB upload cap


def analyze_resume(resume_text):
    """Run every analyzer once and return the full report payload."""

    name = extract_name(resume_text)
    email = extract_email(resume_text)
    phone = extract_phone(resume_text)
    skills = extract_skills(resume_text)
    education = extract_education(resume_text)
    experience = extract_experience(resume_text)
    projects = extract_projects(resume_text)
    certifications = extract_certifications(resume_text)
    languages = extract_languages(resume_text)

    score, score_breakdown, score_suggestions = calculate_advanced_score(
        name,
        email,
        phone,
        skills,
        education,
        experience,
        projects,
        certifications,
    )

    ats_result = check_ats(resume_text, skills, education, experience, projects)
    job_results = analyze_jobs(resume_text, skills)
    skill_gap = analyze_skill_gap(skills)
    suggestions = generate_suggestions(
        skills,
        education,
        experience,
        projects,
        certifications,
    )

    return {
        "name": name,
        "email": email,
        "phone": phone,
        "skills": skills,
        "education": education,
        "experience": experience,
        "projects": projects,
        "certifications": certifications,
        "languages": languages,
        "score": score,
        "score_breakdown": score_breakdown,
        "score_suggestions": score_suggestions,
        "ats_result": ats_result,
        "job_results": job_results,
        "skill_gap": skill_gap,
        "suggestions": suggestions,
    }


def stored_resume_text(resume):
    """Rebuild searchable text from a saved row (the PDF is not re-read)."""

    parts = []

    for field in (
        "skills",
        "education",
        "experience",
        "projects",
        "certifications",
    ):
        value = resume.get(field) or []

        if isinstance(value, str):
            parts.append(value)
        else:
            parts.extend(str(item) for item in value)

    return " ".join(parts)


def safe_pdf_name(filename):
    """Return a filesystem-safe, collision-free name for an uploaded PDF."""

    name = os.path.basename(filename or "").strip()
    name = re.sub(r"[^A-Za-z0-9._-]+", "_", name)

    if not name.lower().endswith(".pdf"):
        name = f"{name}.pdf"

    return f"{uuid.uuid4().hex[:8]}_{name}"


def read_pdf_text(filepath):
    reader = PdfReader(filepath)
    pages = []

    for page in reader.pages:
        text = page.extract_text()

        if text:
            pages.append(text)

    return "\n".join(pages)


def remove_upload(filepath):
    """Best-effort cleanup for uploads that could not be analyzed."""

    try:
        os.remove(filepath)
    except OSError:
        pass


def database_error_response(error):
    return (
        render_template(
            "error.html",
            title="Database unavailable",
            message=database_error_message(error),
        ),
        503,
    )


def validation_error_response(message):
    return (
        render_template(
            "error.html",
            title="Upload problem",
            message=message,
        ),
        400,
    )


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/health")
def health():
    return {"status": "ok"}


@app.route("/upload", methods=["POST"])
def upload_resume():

    if "resume" not in request.files:
        return validation_error_response(
            "No file was selected. Choose a PDF resume and try again."
        )

    file = request.files["resume"]

    if not file.filename:
        return validation_error_response(
            "No file was selected. Choose a PDF resume and try again."
        )

    if not file.filename.lower().endswith(".pdf"):
        return validation_error_response(
            "Only PDF resumes are supported. Please upload a .pdf file."
        )

    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    filepath = os.path.join(
        app.config["UPLOAD_FOLDER"],
        safe_pdf_name(file.filename),
    )

    file.save(filepath)

    try:
        resume_text = read_pdf_text(filepath)
    except Exception as error:
        remove_upload(filepath)
        return validation_error_response(
            "That PDF could not be read. It may be corrupted or password "
            f"protected. Details: {error}"
        )

    if not resume_text.strip():
        remove_upload(filepath)
        return validation_error_response(
            "No text could be extracted from that PDF. Upload a text-based "
            "PDF instead of a scanned image."
        )

    report = analyze_resume(resume_text)

    resume_id = None
    save_error = None

    try:
        resume_id = save_resume(
            report["name"],
            report["email"],
            report["phone"],
            report["skills"],
            report["education"],
            report["experience"],
            report["projects"],
            report["certifications"],
            report["score"],
            report["ats_result"]["score"],
        )
    except (MySQLError, RuntimeError) as error:
        # The analysis already succeeded, so still show the report.
        save_error = database_error_message(error)

    return render_template(
        "result.html",
        resume_text=resume_text,
        resume_id=resume_id,
        save_error=save_error,
        **report,
    )


@app.route("/history")
def history():

    try:
        resumes = get_resumes()
    except (MySQLError, RuntimeError) as error:
        return render_template(
            "history.html",
            resumes=[],
            error=database_error_message(error),
        )

    return render_template("history.html", resumes=resumes, error=None)


@app.route("/resume/<int:resume_id>")
def view_resume(resume_id):

    try:
        resume = get_resume(resume_id)
    except (MySQLError, RuntimeError) as error:
        return database_error_response(error)

    if resume is None:
        abort(404)

    job_results = analyze_jobs(
        stored_resume_text(resume),
        resume.get("skills") or [],
    )

    return render_template(
        "view_resume.html",
        resume=resume,
        job_results=job_results,
    )


@app.route("/resume/<int:resume_id>/job/<job_slug>")
def job_detail(resume_id, job_slug):

    try:
        resume = get_resume(resume_id)
    except (MySQLError, RuntimeError) as error:
        return database_error_response(error)

    if resume is None:
        abort(404)

    job_results = analyze_jobs(
        stored_resume_text(resume),
        resume.get("skills") or [],
    )

    job = next(
        (item for item in job_results if item["slug"] == job_slug),
        None,
    )

    if job is None:
        abort(404)

    return render_template(
        "job_result.html",
        resume_id=resume_id,
        job_role=job["job_role"],
        match_percentage=job["match_percentage"],
        matched_skills=job["matched_skills"],
        missing_skills=job["missing_skills"],
    )


@app.route("/resume/<int:resume_id>/delete", methods=["POST"])
def remove_resume(resume_id):

    try:
        delete_resume(resume_id)
    except (MySQLError, RuntimeError) as error:
        return database_error_response(error)

    return redirect(url_for("history"))


@app.errorhandler(404)
def not_found(error):
    return (
        render_template(
            "error.html",
            title="Page not found",
            message=(
                "That page or saved resume report does not exist. "
                "It may have been deleted."
            ),
        ),
        404,
    )


if __name__ == "__main__":
    app.run(debug=True)
