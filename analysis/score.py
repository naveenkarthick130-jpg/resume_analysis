def calculate_score(skills, education, experience):

    score = 0

    # Skills - 40 points
    if len(skills) >= 8:
        score += 40
    elif len(skills) >= 5:
        score += 30
    elif len(skills) >= 3:
        score += 20
    elif len(skills) >= 1:
        score += 10

    # Education - 20 points
    if len(education) >= 1:
        score += 20

    # Experience - 20 points
    if len(experience) >= 3:
        score += 20
    elif len(experience) >= 1:
        score += 10

    # Resume content - 20 points
    # Based on the above information
    if skills and education:
        score += 10

    if skills and experience:
        score += 10

    return score