import re


def extract_name(text):
    lines = text.split("\n")

    for line in lines:
        line = line.strip()

        if line and len(line.split()) <= 4:
            if not any(char.isdigit() for char in line):
                return line

    return "Not found"


def extract_email(text):
    pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"

    result = re.search(pattern, text)

    if result:
        return result.group()

    return "Not found"


def extract_phone(text):
    pattern = r"(?:\+91[\s-]?)?[6-9]\d{9}"

    result = re.search(pattern, text)

    if result:
        return result.group()

    return "Not found"


def extract_skills(text):

    skills_list = [
        "Python",
        "Java",
        "JavaScript",
        "HTML",
        "CSS",
        "SQL",
        "MySQL",
        "Django",
        "Flask",
        "React",
        "Machine Learning",
        "Deep Learning",
        "Artificial Intelligence",
        "Generative AI",
        "Git",
        "GitHub",
        "Docker",
        "AWS",
        "Azure",
        "Power BI",
        "Tableau",
        "UiPath"
    ]

    found_skills = []

    text_lower = text.lower()

    for skill in skills_list:
        if skill.lower() in text_lower:
            found_skills.append(skill)

    return found_skills


def extract_education(text):

    education_keywords = [
        "B.Tech",
        "B.E",
        "B.Sc",
        "M.Tech",
        "M.E",
        "M.Sc",
        "MBA",
        "Bachelor",
        "Master"
    ]

    found = []

    for education in education_keywords:
        if education.lower() in text.lower():
            found.append(education)

    return found


def extract_experience(text):

    experience_keywords = [
        "experience",
        "internship",
        "intern",
        "developer",
        "engineer"
    ]

    found = []

    text_lower = text.lower()

    for keyword in experience_keywords:
        if keyword in text_lower:
            found.append(keyword)

    return found
def extract_projects(text):

    projects = []

    lines = text.split("\n")

    project_section = False

    for line in lines:

        line = line.strip()

        if not line:
            continue

        if "project" in line.lower():
            project_section = True
            continue

        if project_section:

            if any(section in line.lower() for section in [
                "education",
                "experience",
                "certification",
                "skills",
                "language"
            ]):
                break

            if len(line) > 5:
                projects.append(line)

    return projects[:10]


def extract_certifications(text):

    certifications = []

    lines = text.split("\n")

    certification_section = False

    for line in lines:

        line = line.strip()

        if not line:
            continue

        if any(word in line.lower() for word in [
            "certification",
            "certificate"
        ]):
            certification_section = True
            continue

        if certification_section:

            if any(section in line.lower() for section in [
                "education",
                "experience",
                "project",
                "skills",
                "language"
            ]):
                break

            if len(line) > 5:
                certifications.append(line)

    return certifications[:10]


def extract_languages(text):

    languages = [
        "English",
        "Tamil",
        "Hindi",
        "Telugu",
        "Malayalam",
        "Kannada",
        "French",
        "German",
        "Spanish"
    ]

    found_languages = []

    text_lower = text.lower()

    for language in languages:

        if language.lower() in text_lower:
            found_languages.append(language)

    return found_languages