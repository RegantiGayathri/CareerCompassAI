def calculate_career_match(user, career):
    """
    Calculate how well a career matches the student's profile.

    Matching factors:
    - Branch / education
    - Skills
    - Career requirements

    Returns a score from 0 to 100.
    """

    score = 0
    reasons = []

    # ---------------------------------------------------------
    # 1. BRANCH / EDUCATION MATCH - 30 POINTS
    # ---------------------------------------------------------

    branch = (user.get("branch") or "").lower()
    education = (career.get("education") or "").lower()

    if branch:

        if "computer" in branch or "cse" in branch:
            if any(word in education for word in
                   ["computer", "software", "engineering"]):

                score += 30
                reasons.append("Your academic branch matches this career.")

            else:
                score += 15

        elif "information technology" in branch or "it" in branch:
            if any(word in education for word in
                   ["computer", "software", "engineering"]):

                score += 30
                reasons.append("Your academic background is suitable.")

            else:
                score += 15

        else:
            score += 15

    # ---------------------------------------------------------
    # 2. SKILL MATCH - 50 POINTS
    # ---------------------------------------------------------

    user_skills = user.get("skills") or ""

    user_skill_list = [
        skill.strip().lower()
        for skill in user_skills.split(",")
        if skill.strip()
    ]

    required_skills = career.get("required_skills") or ""

    career_skill_list = [
        skill.strip().lower()
        for skill in required_skills.split(",")
        if skill.strip()
    ]

    if user_skill_list and career_skill_list:

        matched_skills = []

        for user_skill in user_skill_list:

            for career_skill in career_skill_list:

                if (
                    user_skill in career_skill
                    or career_skill in user_skill
                ):
                    matched_skills.append(career_skill)
                    break

        matched_skills = list(set(matched_skills))

        skill_score = (
            len(matched_skills)
            / len(career_skill_list)
        ) * 50

        score += skill_score

        if matched_skills:

            reasons.append(
                f"You already have {len(matched_skills)} "
                f"skill(s) required for this career."
            )

    else:

        score += 10

        reasons.append(
            "Add your skills to your profile for a more accurate match."
        )

    # ---------------------------------------------------------
    # 3. CAREER DEMAND - 20 POINTS
    # ---------------------------------------------------------

    job_growth = (career.get("job_growth") or "").lower()

    if "rapid" in job_growth:
        score += 20
        reasons.append("This career has rapidly growing demand.")

    elif "strong" in job_growth:
        score += 18
        reasons.append("This career has strong job demand.")

    elif "growing" in job_growth:
        score += 16
        reasons.append("This career has growing demand.")

    else:
        score += 10

    # ---------------------------------------------------------
    # LIMIT SCORE TO 100
    # ---------------------------------------------------------

    score = min(round(score), 100)

    return {
        "score": score,
        "reasons": reasons
    }


def get_career_recommendations(user, careers):
    """
    Calculate scores for all careers and return
    them from highest match to lowest match.
    """

    recommendations = []

    for career in careers:

        result = calculate_career_match(
            user,
            career
        )

        recommendations.append({
            "career": career,
            "score": result["score"],
            "reasons": result["reasons"]
        })

    recommendations.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    return recommendations