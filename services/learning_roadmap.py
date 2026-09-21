# =========================================================
# LEARNING ROADMAP SERVICE
# =========================================================

CAREER_ROADMAPS = {

    "Software Developer": [
        {
            "title": "Programming Fundamentals",
            "skills": ["Python", "Java", "C"],
            "description": "Strengthen programming fundamentals, OOP and problem solving."
        },
        {
            "title": "Data Structures & Algorithms",
            "skills": ["Data Structures", "Algorithms"],
            "description": "Practice arrays, strings, linked lists, stacks, queues, trees and graphs."
        },
        {
            "title": "Database Development",
            "skills": ["SQL", "MySQL", "DBMS"],
            "description": "Learn SQL queries, joins, normalization and database design."
        },
        {
            "title": "Web Development",
            "skills": ["HTML", "CSS", "JavaScript"],
            "description": "Build responsive frontend applications and connect them with backend services."
        },
        {
            "title": "Version Control",
            "skills": ["Git", "GitHub"],
            "description": "Learn Git workflows, branching, commits and collaborative development."
        },
        {
            "title": "Real-World Projects",
            "skills": ["Projects", "Problem-solving"],
            "description": "Build 2-3 complete projects and publish them on GitHub."
        },
        {
            "title": "Interview Preparation",
            "skills": ["DSA", "Communication"],
            "description": "Practice coding problems, technical interviews and HR questions."
        }
    ],

    "Data Analyst": [
        {
            "title": "Python for Data Analysis",
            "skills": ["Python", "Pandas", "NumPy"],
            "description": "Learn Python libraries used for data cleaning and analysis."
        },
        {
            "title": "SQL",
            "skills": ["SQL", "MySQL"],
            "description": "Master queries, joins, grouping, subqueries and database analysis."
        },
        {
            "title": "Statistics",
            "skills": ["Statistics"],
            "description": "Learn descriptive statistics, probability and analytical concepts."
        },
        {
            "title": "Data Visualization",
            "skills": ["Excel", "Power BI", "Data Visualization"],
            "description": "Create dashboards, charts and meaningful visual reports."
        },
        {
            "title": "Real-World Data Projects",
            "skills": ["Data Analysis"],
            "description": "Work with real datasets and create portfolio projects."
        },
        {
            "title": "Interview Preparation",
            "skills": ["Communication", "Problem-solving"],
            "description": "Practice SQL, analytics and business case interview questions."
        }
    ],

    "AI / ML Engineer": [
        {
            "title": "Python",
            "skills": ["Python"],
            "description": "Strengthen Python programming and object-oriented programming."
        },
        {
            "title": "Mathematics & Statistics",
            "skills": ["Statistics"],
            "description": "Learn probability, statistics and mathematical foundations for ML."
        },
        {
            "title": "Data Processing",
            "skills": ["NumPy", "Pandas"],
            "description": "Learn data cleaning, preprocessing and exploratory data analysis."
        },
        {
            "title": "Machine Learning",
            "skills": ["Machine Learning", "Scikit-learn"],
            "description": "Learn supervised and unsupervised machine learning algorithms."
        },
        {
            "title": "Deep Learning",
            "skills": ["Deep Learning", "TensorFlow"],
            "description": "Learn neural networks and deep learning fundamentals."
        },
        {
            "title": "AI Projects",
            "skills": ["Artificial Intelligence"],
            "description": "Build practical AI/ML projects using real-world datasets."
        },
        {
            "title": "Interview Preparation",
            "skills": ["Problem-solving", "Communication"],
            "description": "Practice ML concepts, coding and technical interview questions."
        }
    ]
}


def get_learning_roadmap(career_name):
    """
    Return roadmap for the selected career.
    """

    return CAREER_ROADMAPS.get(
        career_name,
        CAREER_ROADMAPS["Software Developer"]
    )