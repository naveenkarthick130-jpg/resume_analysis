def calculate_advanced_score(
    name,
    email,
    phone,
    skills,
    education,
    experience,
    projects,
    certifications
):

    score = 0
    breakdown = {}

    # Contact Information - 10 points
    contact_score = 0

    if name != "Not found":
        contact_score += 3

    if email != "Not found":
        contact_score += 4

    if phone != "Not found":
        contact_score += 3

    score += contact_score
    breakdown["Contact Information"] = contact_score


    # Skills - 25 points
    skill_score = min(len(skills) * 4, 25)

    score += skill_score
    breakdown["Skills"] = skill_score


    # Education - 15 points
    education_score = 15 if education else 0

    score += education_score
    breakdown["Education"] = education_score


    # Experience - 20 points
    experience_score = min(len(experience) * 5, 20)

    score += experience_score
    breakdown["Experience"] = experience_score


    # Projects - 15 points
    project_score = min(len(projects) * 5, 15)

    score += project_score
    breakdown["Projects"] = project_score


    # Certifications - 10 points
    certification_score = min(
        len(certifications) * 5,
        10
    )

    score += certification_score
    breakdown["Certifications"] = certification_score


    # Resume Content - 5 points
    content_score = 0

    if len(skills) >= 3:
        content_score += 2

    if projects:
        content_score += 1

    if experience:
        content_score += 1

    if certifications:
        content_score += 1

    score += content_score
    breakdown["Resume Content"] = content_score


    # Suggestions
    suggestions = []

    if name == "Not found":
        suggestions.append(
            "Add your full name clearly at the top of the resume."
        )

    if email == "Not found":
        suggestions.append(
            "Add a professional email address."
        )

    if phone == "Not found":
        suggestions.append(
            "Add your phone number."
        )

    if len(skills) < 5:
        suggestions.append(
            "Add more relevant technical skills."
        )

    if not education:
        suggestions.append(
            "Add your education details."
        )

    if not experience:
        suggestions.append(
            "Add internship or work experience."
        )

    if not projects:
        suggestions.append(
            "Add 2-3 technical projects."
        )

    if not certifications:
        suggestions.append(
            "Add relevant certifications."
        )

    return score, breakdown, suggestions