def check_ats(resume_text, skills, education, experience, projects):

    score = 0
    checks = []

    text = resume_text.lower()

    # 1. Skills section
    if skills:
        score += 20
        checks.append({
            "name": "Skills Section",
            "status": "Good",
            "message": "Skills were detected."
        })
    else:
        checks.append({
            "name": "Skills Section",
            "status": "Missing",
            "message": "Add a clear skills section."
        })

    # 2. Education
    if education:
        score += 15
        checks.append({
            "name": "Education",
            "status": "Good",
            "message": "Education details were detected."
        })
    else:
        checks.append({
            "name": "Education",
            "status": "Missing",
            "message": "Add education details."
        })

    # 3. Experience
    if experience:
        score += 20
        checks.append({
            "name": "Experience",
            "status": "Good",
            "message": "Experience details were detected."
        })
    else:
        checks.append({
            "name": "Experience",
            "status": "Missing",
            "message": "Add internship or work experience."
        })

    # 4. Projects
    if projects:
        score += 15
        checks.append({
            "name": "Projects",
            "status": "Good",
            "message": "Projects were detected."
        })
    else:
        checks.append({
            "name": "Projects",
            "status": "Missing",
            "message": "Add technical projects."
        })

    # 5. Common ATS keywords
    keywords = [
        "python",
        "sql",
        "java",
        "javascript",
        "git",
        "github",
        "api",
        "machine learning",
        "data",
        "developer"
    ]

    found_keywords = []

    for keyword in keywords:

        if keyword in text:
            found_keywords.append(keyword)

    keyword_score = min(
        len(found_keywords) * 3,
        30
    )

    score += keyword_score

    return {
        "score": min(score, 100),
        "found_keywords": found_keywords,
        "checks": checks
    }