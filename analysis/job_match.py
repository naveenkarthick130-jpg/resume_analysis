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


def analyze_jobs(resume_text):

    results = []

    for job_role, job_description in JOB_DESCRIPTIONS.items():

        documents = [
            resume_text,
            job_description
        ]

        vectorizer = TfidfVectorizer(
            stop_words="english"
        )

        tfidf_matrix = vectorizer.fit_transform(
            documents
        )

        similarity = cosine_similarity(
            tfidf_matrix[0:1],
            tfidf_matrix[1:2]
        )[0][0]

        percentage = round(similarity * 100)

        results.append({
            "job_role": job_role,
            "match_percentage": percentage,
            "job_description": job_description
        })

    results.sort(
        key=lambda x: x["match_percentage"],
        reverse=True
    )

    return results