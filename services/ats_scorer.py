import re


# =========================================================
# ATS SCORER
# =========================================================
#
# This module calculates an ATS-style resume score.
#
# Score categories:
# 1. Contact Information       - 10 points
# 2. Resume Sections           - 20 points
# 3. Skills & Keywords         - 25 points
# 4. Projects / Experience     - 20 points
# 5. Education                 - 10 points
# 6. Resume Content            - 15 points
#
# Total = 100 points
#
# This is a rule-based ATS scoring engine.
# Later we can improve it with job-description matching
# and NLP-based analysis.
# =========================================================


# ---------------------------------------------------------
# CONTACT INFORMATION
# ---------------------------------------------------------

def score_contact_information(text):
    """
    Check whether common contact information
    exists in the resume.
    """

    score = 0
    reasons = []

    text_lower = text.lower()

    # -----------------------------------------------------
    # Email
    # -----------------------------------------------------

    email_pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"

    if re.search(email_pattern, text):

        score += 4

        reasons.append(
            "Email address detected."
        )

    else:

        reasons.append(
            "Add a professional email address."
        )

    # -----------------------------------------------------
    # Phone
    # -----------------------------------------------------

    phone_pattern = r"(\+?\d[\d\s\-()]{8,}\d)"

    if re.search(phone_pattern, text):

        score += 4

        reasons.append(
            "Phone number detected."
        )

    else:

        reasons.append(
            "Add a professional phone number."
        )

    # -----------------------------------------------------
    # LinkedIn / GitHub
    # -----------------------------------------------------

    if (
        "linkedin" in text_lower
        or "github" in text_lower
    ):

        score += 2

        reasons.append(
            "Professional profile link detected."
        )

    else:

        reasons.append(
            "Consider adding LinkedIn or GitHub."
        )

    return score, reasons


# ---------------------------------------------------------
# RESUME SECTIONS
# ---------------------------------------------------------

def score_sections(text):
    """
    Check for important resume sections.
    """

    score = 0
    reasons = []

    text_lower = text.lower()

    sections = {

        "education": 4,

        "skills": 4,

        "projects": 4,

        "experience": 4,

        "certificates": 2,

        "hackathons": 2,

    }

    for section, points in sections.items():

        if section in text_lower:

            score += points

        else:

            # Certifications and hackathons are optional,
            # so don't strongly penalize their absence.

            if section in [
                "certificates",
                "hackathons"
            ]:

                reasons.append(
                    f"Consider adding a {section} section "
                    "if applicable."
                )

            else:

                reasons.append(
                    f"Important section missing: {section.title()}."
                )

    # -----------------------------------------------------
    # Alternative certification heading
    # -----------------------------------------------------

    if "certification" in text_lower:

        score += 2

        # Avoid double-penalty if Certificates was absent.

        if "certificates" not in text_lower:

            score = min(score, 20)

    return min(score, 20), reasons


# ---------------------------------------------------------
# SKILLS & KEYWORDS
# ---------------------------------------------------------

def score_skills_and_keywords(analysis):
    """
    Score the number and quality of detected skills
    and important keywords.
    """

    score = 0
    reasons = []

    skills = analysis.get("skills") or []

    keywords = analysis.get("keywords") or []

    # -----------------------------------------------------
    # Skills
    # -----------------------------------------------------

    skill_count = len(skills)

    if skill_count >= 10:

        score += 15

        reasons.append(
            "Strong number of relevant skills detected."
        )

    elif skill_count >= 7:

        score += 12

        reasons.append(
            "Good range of skills detected."
        )

    elif skill_count >= 4:

        score += 9

        reasons.append(
            "Some relevant skills were detected."
        )

    elif skill_count >= 1:

        score += 5

        reasons.append(
            "Add more relevant technical skills "
            "to improve keyword coverage."
        )

    else:

        reasons.append(
            "No recognized skills detected."
        )

    # -----------------------------------------------------
    # Keywords
    # -----------------------------------------------------

    keyword_count = len(keywords)

    if keyword_count >= 10:

        score += 10

        reasons.append(
            "Good keyword coverage detected."
        )

    elif keyword_count >= 6:

        score += 8

        reasons.append(
            "Reasonable keyword coverage detected."
        )

    elif keyword_count >= 3:

        score += 5

        reasons.append(
            "Consider adding more job-relevant keywords."
        )

    elif keyword_count >= 1:

        score += 2

        reasons.append(
            "Resume keyword coverage is limited."
        )

    else:

        reasons.append(
            "Important resume keywords were not detected."
        )

    return min(score, 25), reasons


# ---------------------------------------------------------
# PROJECTS / EXPERIENCE
# ---------------------------------------------------------

def score_projects_experience(analysis):
    """
    Score projects and work experience.
    """

    score = 0
    reasons = []

    projects = analysis.get("projects") or []

    experience = analysis.get("experience") or []

    # -----------------------------------------------------
    # Projects
    # -----------------------------------------------------

    project_count = len(projects)

    if project_count >= 3:

        score += 12

        reasons.append(
            "Strong project portfolio detected."
        )

    elif project_count == 2:

        score += 10

        reasons.append(
            "Two projects detected."
        )

    elif project_count == 1:

        score += 7

        reasons.append(
            "One project detected. Consider adding "
            "more relevant projects."
        )

    else:

        reasons.append(
            "No projects detected."
        )

    # -----------------------------------------------------
    # Experience
    # -----------------------------------------------------

    experience_count = len(experience)

    if experience_count >= 4:

        score += 8

        reasons.append(
            "Good experience information detected."
        )

    elif experience_count >= 2:

        score += 6

        reasons.append(
            "Some experience information detected."
        )

    elif experience_count == 1:

        score += 4

        reasons.append(
            "Limited experience information detected."
        )

    else:

        # Students may not have work experience.
        # Therefore we don't heavily penalize this.

        reasons.append(
            "No formal work experience detected."
        )

    return min(score, 20), reasons


# ---------------------------------------------------------
# EDUCATION
# ---------------------------------------------------------

def score_education(analysis):
    """
    Score education information.
    """

    score = 0
    reasons = []

    education = analysis.get("education") or ""

    if education:

        score += 10

        reasons.append(
            "Education information detected."
        )

    else:

        reasons.append(
            "Add your education details."
        )

    return score, reasons


# ---------------------------------------------------------
# CONTENT QUALITY
# ---------------------------------------------------------

def score_content(text, analysis):
    """
    Check basic content quality indicators.
    """

    score = 0
    reasons = []

    # -----------------------------------------------------
    # Resume length
    # -----------------------------------------------------

    word_count = len(
        text.split()
    )

    if word_count >= 250:

        score += 5

        reasons.append(
            "Resume contains sufficient content."
        )

    elif word_count >= 150:

        score += 4

        reasons.append(
            "Resume contains a reasonable amount of content."
        )

    elif word_count >= 80:

        score += 2

        reasons.append(
            "Resume content is somewhat limited."
        )

    else:

        reasons.append(
            "Resume contains very little text."
        )

    # -----------------------------------------------------
    # Action-oriented words
    # -----------------------------------------------------

    action_words = [

        "developed",
        "created",
        "designed",
        "implemented",
        "built",
        "analyzed",
        "managed",
        "improved",
        "optimized",
        "develop",
        "create",
        "design",
        "implement",
        "build",
        "analyze",

    ]

    text_lower = text.lower()

    found_action_words = []

    for word in action_words:

        if word in text_lower:

            found_action_words.append(word)

    if len(found_action_words) >= 3:

        score += 5

        reasons.append(
            "Resume uses strong action-oriented language."
        )

    elif len(found_action_words) >= 1:

        score += 3

        reasons.append(
            "Some action-oriented language detected."
        )

    else:

        reasons.append(
            "Use action verbs such as developed, "
            "implemented, designed and analyzed."
        )

    # -----------------------------------------------------
    # Quantifiable achievements
    # -----------------------------------------------------

    number_pattern = r"\b\d+(?:\.\d+)?%?\b"

    numbers = re.findall(
        number_pattern,
        text
    )

    if len(numbers) >= 5:

        score += 5

        reasons.append(
            "Resume contains several measurable details."
        )

    elif len(numbers) >= 2:

        score += 3

        reasons.append(
            "Some measurable information detected."
        )

    else:

        reasons.append(
            "Add measurable results where possible."
        )

    return min(score, 15), reasons


# ---------------------------------------------------------
# IMPROVEMENT SUGGESTIONS
# ---------------------------------------------------------

def generate_suggestions(
    contact_score,
    section_score,
    skill_score,
    project_score,
    education_score,
    content_score
):
    """
    Generate personalized ATS improvement suggestions.
    """

    suggestions = []

    # -----------------------------------------------------
    # Contact
    # -----------------------------------------------------

    if contact_score < 8:

        suggestions.append(
            "Add complete professional contact information "
            "including email, phone and LinkedIn/GitHub."
        )

    # -----------------------------------------------------
    # Sections
    # -----------------------------------------------------

    if section_score < 16:

        suggestions.append(
            "Make sure your resume contains clear sections "
            "such as Education, Skills, Projects and Experience."
        )

    # -----------------------------------------------------
    # Skills
    # -----------------------------------------------------

    if skill_score < 18:

        suggestions.append(
            "Add more job-relevant technical skills and "
            "keywords that match your target role."
        )

    # -----------------------------------------------------
    # Projects
    # -----------------------------------------------------

    if project_score < 14:

        suggestions.append(
            "Add strong projects and describe your "
            "contribution, technologies and results."
        )

    # -----------------------------------------------------
    # Education
    # -----------------------------------------------------

    if education_score < 10:

        suggestions.append(
            "Add your degree, college, branch and "
            "relevant academic information."
        )

    # -----------------------------------------------------
    # Content
    # -----------------------------------------------------

    if content_score < 10:

        suggestions.append(
            "Improve resume content using action verbs "
            "and measurable achievements."
        )

    # -----------------------------------------------------
    # Default
    # -----------------------------------------------------

    if not suggestions:

        suggestions.append(
            "Your resume has a strong basic ATS structure. "
            "Next, match it against a specific job description "
            "for a more accurate ATS score."
        )

    return suggestions


# ---------------------------------------------------------
# MAIN ATS ANALYSIS
# ---------------------------------------------------------

def calculate_ats_score(text, analysis):
    """
    Calculate the complete ATS score.

    Returns:
        Dictionary containing total score,
        category scores, reasons and suggestions.
    """

    if not text:

        return {

            "score": 0,

            "categories": {

                "contact": 0,

                "sections": 0,

                "skills": 0,

                "projects": 0,

                "education": 0,

                "content": 0,

            },

            "reasons": [],

            "suggestions": [

                "Upload a resume to calculate an ATS score."

            ]

        }

    # -----------------------------------------------------
    # Calculate individual categories
    # -----------------------------------------------------

    contact_score, contact_reasons = (
        score_contact_information(text)
    )

    section_score, section_reasons = (
        score_sections(text)
    )

    skill_score, skill_reasons = (
        score_skills_and_keywords(analysis)
    )

    project_score, project_reasons = (
        score_projects_experience(analysis)
    )

    education_score, education_reasons = (
        score_education(analysis)
    )

    content_score, content_reasons = (
        score_content(
            text,
            analysis
        )
    )

    # -----------------------------------------------------
    # Total score
    # -----------------------------------------------------

    total_score = (

        contact_score
        + section_score
        + skill_score
        + project_score
        + education_score
        + content_score

    )

    total_score = min(
        round(total_score),
        100
    )

    # -----------------------------------------------------
    # Combine reasons
    # -----------------------------------------------------

    reasons = (

        contact_reasons
        + section_reasons
        + skill_reasons
        + project_reasons
        + education_reasons
        + content_reasons

    )

    # -----------------------------------------------------
    # Suggestions
    # -----------------------------------------------------

    suggestions = generate_suggestions(

        contact_score,

        section_score,

        skill_score,

        project_score,

        education_score,

        content_score

    )

    # -----------------------------------------------------
    # Return result
    # -----------------------------------------------------

    return {

        "score": total_score,

        "categories": {

            "contact": contact_score,

            "sections": section_score,

            "skills": skill_score,

            "projects": project_score,

            "education": education_score,

            "content": content_score,

        },

        "reasons": reasons,

        "suggestions": suggestions,

    }