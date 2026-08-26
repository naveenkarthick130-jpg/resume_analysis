def generate_suggestions(
    skills,
    education,
    experience,
    projects,
    certifications
):

    suggestions = []

    # Skills
    if len(skills) < 5:
        suggestions.append(
            "Add more relevant technical skills to your resume."
        )

    # Education
    if not education:
        suggestions.append(
            "Add your education details clearly."
        )

    # Experience
    if not experience:
        suggestions.append(
            "Add internship, training, or work experience."
        )

    # Projects
    if len(projects) < 2:
        suggestions.append(
            "Add at least 2 technical projects with descriptions."
        )

    # Certifications
    if not certifications:
        suggestions.append(
            "Add relevant professional certifications."
        )

    # Good resume
    if not suggestions:
        suggestions.append(
            "Your resume contains the major sections. "
            "Continue improving it with measurable achievements."
        )

    return suggestions