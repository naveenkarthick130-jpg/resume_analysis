from flask import Flask, render_template, request
from PyPDF2 import PdfReader
from mysql.connector import Error as MySQLError
import os
from analysis.score import calculate_score
from analysis.resume import *
from analysis.job_match import *
from analysis.suggestion import *
from analysis.advanced_scorer import *
from analysis.ats_checker import check_ats
from analysis.skill_gap import analyze_skill_gap
from database import *

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload_resume():

    if "resume" not in request.files:
        return "No file selected"

    file = request.files["resume"]

    if file.filename == "":
        return "No file selected"

    if not file.filename.lower().endswith(".pdf"):
        return "Please upload a PDF file"

    # Create uploads folder if it doesn't exist
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    # Save PDF
    filepath = os.path.join(
        app.config["UPLOAD_FOLDER"],
        file.filename
    )

    file.save(filepath)

    # Read PDF
    reader = PdfReader(filepath)

    resume_text = ""

    for page in reader.pages:
        text = page.extract_text()

        if text:
            resume_text += text + "\n"
     # Extract information

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
    certifications
)
    job_results = analyze_jobs(resume_text)
    projects = extract_projects(resume_text)
    certifications = extract_certifications(resume_text)
    languages = extract_languages(resume_text)
    ats_result = check_ats(
    resume_text,
    skills,
    education,
    experience,
    projects)
    skill_gap = analyze_skill_gap(skills)
    try:
        save_resume(
            name,
            email,
            phone,
            skills,
            education,
            experience,
            projects,
            certifications,
            score,
            ats_result["score"]
        )
    except (MySQLError, RuntimeError) as error:
        return (
            "Resume analyzed, but it could not be saved to MySQL. "
            "Check MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE "
            f"in .env. Database error: {error}",
            503,
        )
    suggestions = generate_suggestions(

    skills,
    education,
    experience,
    projects,
    certifications
)


    
    
    
    
    
    return render_template(
    "result.html",
    resume_text=resume_text,
    name=name,
    email=email,
    phone=phone,
    skills=skills,
    education=education,
    experience=experience,
    projects=projects,
    certifications=certifications,
    languages=languages,
    score=score,
    score_breakdown=score_breakdown,
    score_suggestions=score_suggestions,
    suggestions=suggestions,
    job_results=job_results,
    ats_result=ats_result,
    skill_gap=skill_gap,
    
)
@app.route("/history")
def history():

    resumes = get_resumes()

    return render_template(
        "history.html",
        resumes=resumes
    )

@app.route("/resume/<int:resume_id>")
def view_resume(resume_id):

    connection = get_connection()

    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM resumes WHERE id = %s",
        (resume_id,)
    )

    resume = cursor.fetchone()

    cursor.close()
    connection.close()

    if resume is None:
        return "Resume not found"

    return render_template(
        "view_resume.html",
        resume=resume
    )
    
    
    

    #score information

if __name__ == "__main__":
    app.run(debug=True)