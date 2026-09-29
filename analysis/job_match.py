import re

from analysis.skill_gap import JOB_SKILLS
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


JOB_DESCRIPTIONS = {

    "Python Developer": """
    Python developer responsible for developing applications
    using Python, Flask, Django, REST API, SQL, MySQL,
    Git, GitHub, Docker and backend development.
    """,

    "Data Analyst": """
    Data analyst responsible for analyzing data using Python,
    SQL, Excel, Power BI, Tableau, pandas, numpy,
    data visualization and statistics.
    """,

    "Java Developer": """
    Java developer responsible for developing applications
    using Java, Spring Boot, SQL, MySQL, REST API,
    Git, GitHub and backend development.
    """,

    "Machine Learning Engineer": """
    Machine learning engineer working with Python,
    machine learning, deep learning, pandas, numpy,
    scikit-learn, TensorFlow, SQL and data analysis.
    """,

    "Frontend Developer": """
    Frontend developer working with HTML, CSS, JavaScript,
    React, Bootstrap, responsive web development,
    Git and frontend application development.
    """
}


def slugify_role(role):
    """Turn a job title into a URL-safe slug."""
    return re.sub(r"[^a-z0-9]+", "-", role.lower()).strip("-")


def _match_skills(resume_skills, required_skills):
    resume_skills_lower = [
        skill.lower().strip()
        for skill in resume_skills
    ]

    matched = []
    missing = []

    for skill in required_skills:
        if skill.lower() in resume_skills_lower:
            matched.append(skill)
        else:
            missing.append(skill)

    if required_skills:
        skill_percentage = round(
            (len(matched) / len(required_skills)) * 100
        )
    else:
        skill_percentage = 0

    return matched, missing, skill_percentage


def _text_similarity(resume_text, job_description):
    documents = [resume_text or "", job_description]

    if not documents[0].strip():
        return 0

    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf_matrix = vectorizer.fit_transform(documents)
    similarity = cosine_similarity(
        tfidf_matrix[0:1],
        tfidf_matrix[1:2]
    )[0][0]

    return round(float(similarity) * 100)


def analyze_jobs(resume_text, resume_skills=None):
    """Score each role with skill overlap and resume-text similarity."""
    if resume_skills is None:
        resume_skills = []

    results = []

    for job_role, job_description in JOB_DESCRIPTIONS.items():
        required_skills = JOB_SKILLS.get(job_role, [])
        matched, missing, skill_percentage = _match_skills(
            resume_skills,
            required_skills
        )
        text_percentage = _text_similarity(resume_text, job_description)
        match_percentage = round(
            (skill_percentage * 0.7) + (text_percentage * 0.3)
        )

        results.append({
            "job_role": job_role,
            "slug": slugify_role(job_role),
            "match_percentage": match_percentage,
            "skill_percentage": skill_percentage,
            "text_percentage": text_percentage,
            "matched_skills": matched,
            "missing_skills": missing,
            "job_description": job_description.strip()
        })

    results.sort(
        key=lambda item: item["match_percentage"],
        reverse=True
    )

    return results
