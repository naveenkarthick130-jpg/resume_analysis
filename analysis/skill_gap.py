JOB_SKILLS = {

    "Python Developer": [
        "Python",
        "SQL",
        "Flask",
        "Django",
        "Git",
        "GitHub",
        "Docker"
    ],

    "Data Analyst": [
        "Python",
        "SQL",
        "Excel",
        "Power BI",
        "Tableau",
        "Pandas",
        "NumPy"
    ],

    "Java Developer": [
        "Java",
        "SQL",
        "Spring",
        "MySQL",
        "Git",
        "GitHub"
    ],

    "Machine Learning Engineer": [
        "Python",
        "Machine Learning",
        "Deep Learning",
        "Pandas",
        "NumPy",
        "Scikit-learn",
        "TensorFlow"
    ],

    "Frontend Developer": [
        "HTML",
        "CSS",
        "JavaScript",
        "React",
        "Bootstrap",
        "Git"
    ]
}


def analyze_skill_gap(resume_skills):

    resume_skills_lower = [
        skill.lower().strip()
        for skill in resume_skills
    ]

    results = []

    for job, required_skills in JOB_SKILLS.items():

        matched = []
        missing = []

        for skill in required_skills:

            if skill.lower() in resume_skills_lower:
                matched.append(skill)
            else:
                missing.append(skill)

        results.append({
            "job": job,
            "matched": matched,
            "missing": missing
        })

    return results