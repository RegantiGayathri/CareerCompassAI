import re


# ---------------------------------------------------------
# COMMON SKILLS
# ---------------------------------------------------------

SKILLS = [
    "Python",
    "Java",
    "C",
    "C++",
    "JavaScript",
    "HTML",
    "CSS",
    "SQL",
    "MySQL",
    "Git",
    "GitHub",
    "Excel",
    "MS Excel",
    "Power BI",
    "Pandas",
    "NumPy",
    "TensorFlow",
    "Scikit-learn",
    "Machine Learning",
    "Deep Learning",
    "Data Structures",
    "Algorithms",
    "Data Structures and Algorithms",
    "DBMS",
    "Operating Systems",
    "Communication",
    "Problem-solving",
    "Teamwork",
]


# ---------------------------------------------------------
# SECTION EXTRACTION
# ---------------------------------------------------------

def extract_section(text, section_name, next_sections):
    """
    Extract text belonging to a particular resume section.
    """

    pattern = rf"{re.escape(section_name)}\s*(.*?)(?=\n(?:{'|'.join(map(re.escape, next_sections))})\b|$)"

    match = re.search(
        pattern,
        text,
        re.IGNORECASE | re.DOTALL
    )

    if match:
        return match.group(1).strip()

    return ""


# ---------------------------------------------------------
# SKILL EXTRACTION
# ---------------------------------------------------------

def extract_skills(text):
    """
    Find known technical and soft skills from resume text.
    """

    found_skills = []

    text_lower = text.lower()

    for skill in SKILLS:

        if skill.lower() in text_lower:

            found_skills.append(skill)

    return sorted(
        list(set(found_skills)),
        key=str.lower
    )


# ---------------------------------------------------------
# EDUCATION EXTRACTION
# ---------------------------------------------------------

def extract_education(text):
    """
    Extract education-related information.
    """

    education_section = extract_section(
        text,
        "EDUCATION",
        [
            "SKILLS",
            "PROJECTS",
            "EXPERIENCE",
            "CERTIFICATES",
            "CERTIFICATIONS",
            "CODING PROFILES",
            "HACKATHONS",
        ]
    )

    return education_section


# ---------------------------------------------------------
# PROJECT EXTRACTION
# ---------------------------------------------------------

def extract_projects(text):
    """
    Extract project information.
    """

    projects_section = extract_section(
        text,
        "PROJECTS",
        [
            "CODING PROFILES",
            "CERTIFICATES",
            "CERTIFICATIONS",
            "HACKATHONS",
            "ACHIEVEMENTS",
            "EXPERIENCE",
        ]
    )

    if not projects_section:
        return []

    lines = [
        line.strip()
        for line in projects_section.splitlines()
        if line.strip()
    ]

    projects = []

    current_project = None

    for line in lines:

        # Ignore bullet points
        clean_line = re.sub(
            r"^[•\-*]\s*",
            "",
            line
        ).strip()

        # A line containing "Link" is usually
        # part of a project heading.
        if (
            "link" in clean_line.lower()
            and not clean_line.startswith("•")
        ):

            if current_project:
                projects.append(current_project)

            project_name = re.sub(
                r"\s*:?link\s*$",
                "",
                clean_line,
                flags=re.IGNORECASE
            ).strip()

            current_project = {
                "name": project_name,
                "description": []
            }

        elif current_project:

            current_project["description"].append(
                clean_line
            )

    if current_project:
        projects.append(current_project)

    return projects


# ---------------------------------------------------------
# CERTIFICATION EXTRACTION
# ---------------------------------------------------------

def extract_certifications(text):
    """
    Extract certificate/certification information.
    """

    section = extract_section(
        text,
        "CERTIFICATES",
        [
            "HACKATHONS",
            "ACHIEVEMENTS",
            "CODING PROFILES",
        ]
    )

    if not section:

        section = extract_section(
            text,
            "CERTIFICATIONS",
            [
                "HACKATHONS",
                "ACHIEVEMENTS",
                "CODING PROFILES",
            ]
        )

    if not section:
        return []

    certifications = []

    for line in section.splitlines():

        line = re.sub(
            r"^[•\-*]\s*",
            "",
            line
        ).strip()

        if line:
            certifications.append(line)

    return certifications


# ---------------------------------------------------------
# EXPERIENCE EXTRACTION
# ---------------------------------------------------------

def extract_experience(text):
    """
    Extract experience information.

    If the resume does not contain an Experience section,
    return an empty list.
    """

    section = extract_section(
        text,
        "EXPERIENCE",
        [
            "PROJECTS",
            "EDUCATION",
            "SKILLS",
            "CERTIFICATES",
            "CERTIFICATIONS",
            "HACKATHONS",
        ]
    )

    if not section:
        return []

    experience = []

    for line in section.splitlines():

        line = re.sub(
            r"^[•\-*]\s*",
            "",
            line
        ).strip()

        if line:
            experience.append(line)

    return experience


# ---------------------------------------------------------
# ACHIEVEMENTS / HACKATHONS
# ---------------------------------------------------------

def extract_achievements(text):
    """
    Extract achievements and hackathon information.
    """

    section = extract_section(
        text,
        "HACKATHONS EVENTS",
        [
            "CERTIFICATES",
            "CERTIFICATIONS",
            "EDUCATION",
            "SKILLS",
        ]
    )

    if not section:

        section = extract_section(
            text,
            "HACKATHONS",
            [
                "CERTIFICATES",
                "CERTIFICATIONS",
                "EDUCATION",
                "SKILLS",
            ]
        )

    if not section:
        return []

    achievements = []

    for line in section.splitlines():

        line = re.sub(
            r"^[•\-*]\s*",
            "",
            line
        ).strip()

        if line:
            achievements.append(line)

    return achievements


# ---------------------------------------------------------
# KEYWORD EXTRACTION
# ---------------------------------------------------------

def extract_keywords(text):
    """
    Extract important resume keywords.
    """

    keywords = []

    important_terms = [
        "Python",
        "Java",
        "C",
        "JavaScript",
        "HTML",
        "CSS",
        "SQL",
        "MySQL",
        "Git",
        "GitHub",
        "Data Structures",
        "Algorithms",
        "DBMS",
        "Operating Systems",
        "Machine Learning",
        "Deep Learning",
        "Artificial Intelligence",
        "AI",
        "Data Analysis",
        "Power BI",
        "Excel",
        "Communication",
        "Problem-solving",
        "Teamwork",
        "Hackathon",
        "Internship",
        "Project",
        "Leadership",
        "Authentication",
        "Real-time",
    ]

    text_lower = text.lower()

    for keyword in important_terms:

        if keyword.lower() in text_lower:

            keywords.append(keyword)

    return sorted(
        list(set(keywords)),
        key=str.lower
    )


# ---------------------------------------------------------
# RESUME ANALYSIS
# ---------------------------------------------------------

def analyze_resume(text):
    """
    Perform complete resume analysis.

    Returns a dictionary containing:

    - skills
    - education
    - projects
    - certifications
    - experience
    - achievements
    - keywords
    """

    if not text:
        return {
            "skills": [],
            "education": "",
            "projects": [],
            "certifications": [],
            "experience": [],
            "achievements": [],
            "keywords": [],
        }

    return {
        "skills": extract_skills(text),

        "education": extract_education(text),

        "projects": extract_projects(text),

        "certifications": extract_certifications(text),

        "experience": extract_experience(text),

        "achievements": extract_achievements(text),

        "keywords": extract_keywords(text),
    }