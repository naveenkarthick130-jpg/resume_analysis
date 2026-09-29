import json
import os

import mysql.connector
from dotenv import load_dotenv


from mysql.connector import Error as MySQLError


load_dotenv()

JSON_FIELDS = (
    "skills",
    "education",
    "experience",
    "projects",
    "certifications",
)


def get_connection():
    password = os.getenv("MYSQL_PASSWORD", "").strip()
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


def _as_json(value):
    if value is None:
        return json.dumps([])

    if isinstance(value, str):
        return value

    return json.dumps(value, ensure_ascii=False)


def _decode_list(value):
    if value is None:
        return []

    if isinstance(value, list):
        return value

    if isinstance(value, (bytes, bytearray)):
        value = value.decode("utf-8")

    if isinstance(value, str):
        text = value.strip()
        if not text:
            return []

        try:
            parsed = json.loads(text)
        except json.JSONDecodeError:
            return [item.strip() for item in text.split(",") if item.strip()]

        if isinstance(parsed, list):
            return parsed

        return [str(parsed)]

    return [str(value)]


def decode_resume(resume):
    if not resume:
        return resume

    decoded = dict(resume)

    for field in JSON_FIELDS:
        decoded[field] = _decode_list(decoded.get(field))

    for field in ("score", "ats_score"):
        if decoded.get(field) is not None:
            decoded[field] = float(decoded[field])

    return decoded


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
        _as_json(skills),
        _as_json(education),
        _as_json(experience),
        _as_json(projects),
        _as_json(certifications),
        score,
        ats_score
    )

    try:
        cursor.execute(query, values)
        connection.commit()
        return cursor.lastrowid
    except Exception:
        connection.rollback()
        raise
    finally:
        cursor.close()
        connection.close()
    
    
def get_resumes():

    connection = get_connection()

    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT *
            FROM resumes
            ORDER BY created_at DESC
        """)
        return [decode_resume(row) for row in cursor.fetchall()]
    finally:
        cursor.close()
        connection.close()


def get_resume(resume_id):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute(
            "SELECT * FROM resumes WHERE id = %s",
            (resume_id,)
        )
        return decode_resume(cursor.fetchone())
    finally:
        cursor.close()
        connection.close()


def delete_resume(resume_id):
    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            "DELETE FROM resumes WHERE id = %s",
            (resume_id,)
        )
        connection.commit()
        return cursor.rowcount > 0
    except Exception:
        connection.rollback()
        raise
    finally:
        cursor.close()
        connection.close()


def database_error_message(error):
    if isinstance(error, RuntimeError):
        return str(error)

    if isinstance(error, MySQLError):
        return (
            "Could not reach MySQL. Check that the server is running and that "
            "MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, and MYSQL_DATABASE in .env "
            f"are correct. Database error: {error}"
        )

    return f"Unexpected database error: {error}"
