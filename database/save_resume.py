import json
import os

import mysql.connector
from dotenv import load_dotenv


load_dotenv()


def get_connection():
    password = os.getenv("MYSQL_PASSWORD", "Naveen@123").strip()
    if not password or password == "replace_with_your_mysql_password":
        raise RuntimeError(
            "MYSQL_PASSWORD is not configured. Set your MySQL password in .env."
        )

    return mysql.connector.connect(
        host=os.getenv("MYSQL_HOST", "localhost"),
        port=int(os.getenv("MYSQL_PORT", "3306")),
        user=os.getenv("MYSQL_USER", "root"),
        password=password,
        database=os.getenv("MYSQL_DATABASE", "resume_analyzer"),
    )


def save_resume(
    name,
    email,
    phone,
    skills,
    education,
    experience,
    projects,
    certifications,
    score,
    ats_score
):

    connection = get_connection()

    cursor = connection.cursor()

    query = """
        INSERT INTO resumes
        (name, email, phone, skills, education, experience, projects,
         certifications, score, ats_score)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    values = (
        name,
        email,
        phone,
        json.dumps(skills, ensure_ascii=False),
        json.dumps(education, ensure_ascii=False),
        json.dumps(experience, ensure_ascii=False),
        json.dumps(projects, ensure_ascii=False),
        json.dumps(certifications, ensure_ascii=False),
        score,
        ats_score
    )

    try:
        cursor.execute(query, values)
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        cursor.close()
        connection.close()
    
    
def get_resumes():

    connection = get_connection()

    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT *
        FROM resumes
        ORDER BY created_at DESC
    """)

    resumes = cursor.fetchall()

    cursor.close()
    connection.close()

    return resumes