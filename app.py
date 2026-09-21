import os
import re
import uuid

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session
)

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

from werkzeug.utils import secure_filename

from mysql.connector import IntegrityError

from database.database import get_connection

from services.recommendation_engine import (
    get_career_recommendations
)

from services.resume_parser import (
    extract_text_from_pdf
)

from services.resume_analyzer import (
    analyze_resume
)

from services.ats_scorer import (
    calculate_ats_score
)

from services.learning_roadmap import (
    get_learning_roadmap
)


# =========================================================
# FLASK APPLICATION
# =========================================================

app = Flask(__name__)

app.secret_key = "careercompass-secret-key"


# =========================================================
# RESUME UPLOAD CONFIGURATION
# =========================================================

UPLOAD_FOLDER = os.path.join(
    app.root_path,
    "uploads",
    "resumes"
)

ALLOWED_EXTENSIONS = {"pdf"}

app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024

os.makedirs(
    UPLOAD_FOLDER,
    exist_ok=True
)


# =========================================================
# FILE VALIDATION
# =========================================================

def allowed_file(filename):

    return (
        "." in filename
        and
        filename.rsplit(".", 1)[1].lower()
        in ALLOWED_EXTENSIONS
    )


# =========================================================
# NORMALIZE SKILL
# =========================================================

def normalize_skill(skill):

    if not skill:
        return ""

    skill = str(skill).strip().lower()

    skill = skill.replace("-", " ")
    skill = skill.replace("_", " ")
    skill = skill.replace("/", " ")

    skill = re.sub(
        r"\s+",
        " ",
        skill
    )

    return skill.strip()


# =========================================================
# BUILD CANONICAL SKILL SET
# =========================================================

def build_skill_set(raw_skills):

    if not raw_skills:
        return set()

    skills = set()

    parts = re.split(
        r"[,;|]",
        str(raw_skills)
    )

    for part in parts:

        skill = normalize_skill(part)

        if not skill:
            continue

        skills.add(skill)

        # -----------------------------
        # DSA
        # -----------------------------

        if skill in {
            "dsa",
            "data structures and algorithms",
            "data structure and algorithms",
            "data structure algorithms"
        }:

            skills.add("data structures")
            skills.add("algorithms")

        # -----------------------------
        # Data Structures
        # -----------------------------

        elif skill in {
            "data structure",
            "data structures"
        }:

            skills.add("data structures")

        # -----------------------------
        # Algorithms
        # -----------------------------

        elif skill in {
            "algorithm",
            "algorithms"
        }:

            skills.add("algorithms")

        # -----------------------------
        # SQL
        # -----------------------------

        elif skill in {
            "mysql",
            "postgresql",
            "postgres",
            "sql server",
            "database sql"
        }:

            skills.add("sql")

        # -----------------------------
        # JavaScript
        # -----------------------------

        elif skill in {
            "js",
            "javascript es6",
            "ecmascript"
        }:

            skills.add("javascript")

        # -----------------------------
        # HTML
        # -----------------------------

        elif skill in {
            "html5"
        }:

            skills.add("html")

        # -----------------------------
        # CSS
        # -----------------------------

        elif skill in {
            "css3"
        }:

            skills.add("css")

        # -----------------------------
        # Problem Solving
        # -----------------------------

        elif skill in {
            "problem solving",
            "problem solving skills",
            "problem-solving"
        }:

            skills.add("problem solving")

        # -----------------------------
        # Git / GitHub
        # -----------------------------

        elif skill == "github":

            skills.add("github")

            # GitHub normally implies Git usage
            skills.add("git")

        elif skill == "git":

            skills.add("git")

    # -----------------------------------------------------
    # If both DSA concepts exist, keep both
    # -----------------------------------------------------

    if (
        "dsa" in skills
        or
        (
            "data structures" in skills
            and
            "algorithms" in skills
        )
    ):

        skills.add("data structures")
        skills.add("algorithms")

    return skills


# =========================================================
# HOME
# =========================================================

@app.route("/")
def home():

    return "CareerCompassAI is running! 🚀"


# =========================================================
# REGISTER
# =========================================================

@app.route(
    "/register",
    methods=["GET", "POST"]
)
def register():

    if request.method == "POST":

        full_name = request.form["full_name"]
        email = request.form["email"]
        password = request.form["password"]
        phone = request.form["phone"]
        college = request.form["college"]
        branch = request.form["branch"]
        graduation_year = request.form["graduation_year"]

        hashed_password = generate_password_hash(
            password
        )

        connection = get_connection()

        if not connection:

            return "❌ Database connection failed!"

        cursor = connection.cursor()

        try:

            query = """
                INSERT INTO users
                (
                    full_name,
                    email,
                    password,
                    phone,
                    college,
                    branch,
                    graduation_year
                )
                VALUES
                (
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s
                )
            """

            values = (
                full_name,
                email,
                hashed_password,
                phone,
                college,
                branch,
                graduation_year
            )

            cursor.execute(
                query,
                values
            )

            connection.commit()

            return (
                "✅ Registration successful! "
                "Account created."
            )

        except IntegrityError:

            connection.rollback()

            return (
                "❌ Email already exists! "
                "Please use another email."
            )

        except Exception as e:

            connection.rollback()

            return f"❌ Registration failed: {e}"

        finally:

            cursor.close()
            connection.close()

    return render_template(
        "register.html"
    )


# =========================================================
# LOGIN
# =========================================================

@app.route(
    "/login",
    methods=["GET", "POST"]
)
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        connection = get_connection()

        if not connection:

            return "❌ Database connection failed!"

        cursor = connection.cursor(
            dictionary=True
        )

        try:

            cursor.execute(
                """
                SELECT *
                FROM users
                WHERE email = %s
                """,
                (email,)
            )

            user = cursor.fetchone()

            if user and check_password_hash(
                user["password"],
                password
            ):

                session["user_id"] = user["user_id"]

                session["user_name"] = (
                    user["full_name"]
                )

                return redirect(
                    url_for("dashboard")
                )

            return (
                "❌ Invalid email or password!"
            )

        finally:

            cursor.close()
            connection.close()

    return render_template(
        "login.html"
    )


# =========================================================
# DASHBOARD
# =========================================================

@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )

    return render_template(
        "dashboard.html",
        user_name=session["user_name"]
    )


# =========================================================
# PROFILE
# =========================================================

@app.route(
    "/profile",
    methods=["GET", "POST"]
)
def profile():

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )

    user_id = session["user_id"]

    connection = get_connection()

    if not connection:

        return "❌ Database connection failed!"

    cursor = connection.cursor(
        dictionary=True
    )

    try:

        if request.method == "POST":

            full_name = request.form["full_name"]
            email = request.form["email"]
            phone = request.form["phone"]
            college = request.form["college"]
            branch = request.form["branch"]
            graduation_year = request.form[
                "graduation_year"
            ]

            skills = request.form.get(
                "skills",
                ""
            ).strip()

            cursor.execute(
                """
                UPDATE users
                SET
                    full_name = %s,
                    email = %s,
                    phone = %s,
                    college = %s,
                    branch = %s,
                    graduation_year = %s,
                    skills = %s
                WHERE user_id = %s
                """,
                (
                    full_name,
                    email,
                    phone,
                    college,
                    branch,
                    graduation_year,
                    skills,
                    user_id
                )
            )

            connection.commit()

            session["user_name"] = full_name

            return redirect(
                url_for(
                    "profile",
                    updated="1"
                )
            )

        cursor.execute(
            """
            SELECT
                user_id,
                full_name,
                email,
                phone,
                college,
                branch,
                graduation_year,
                skills
            FROM users
            WHERE user_id = %s
            """,
            (user_id,)
        )

        user = cursor.fetchone()

        if not user:

            session.clear()

            return redirect(
                url_for("login")
            )

        updated = request.args.get(
            "updated"
        )

        return render_template(
            "profile.html",
            user=user,
            updated=updated
        )

    except IntegrityError:

        connection.rollback()

        cursor.execute(
            """
            SELECT
                user_id,
                full_name,
                email,
                phone,
                college,
                branch,
                graduation_year,
                skills
            FROM users
            WHERE user_id = %s
            """,
            (user_id,)
        )

        user = cursor.fetchone()

        return render_template(
            "profile.html",
            user=user,
            error=(
                "Email already exists. "
                "Please use another email."
            )
        )

    except Exception as e:

        connection.rollback()

        return (
            f"❌ Profile update failed: {e}"
        )

    finally:

        cursor.close()
        connection.close()


# =========================================================
# CAREER RECOMMENDATION
# =========================================================

@app.route("/career-recommendation")
def career_recommendation():

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )

    connection = get_connection()

    if not connection:

        return "❌ Database connection failed!"

    cursor = connection.cursor(
        dictionary=True
    )

    try:

        cursor.execute(
            """
            SELECT
                user_id,
                full_name,
                branch,
                graduation_year,
                skills
            FROM users
            WHERE user_id = %s
            """,
            (session["user_id"],)
        )

        user = cursor.fetchone()

        if not user:

            return redirect(
                url_for("login")
            )

        cursor.execute(
            """
            SELECT
                career_id,
                career_name,
                description,
                required_skills,
                education,
                average_salary,
                job_growth
            FROM careers
            ORDER BY career_id
            """
        )

        careers = cursor.fetchall()

        recommendations = (
            get_career_recommendations(
                user,
                careers
            )
        )

        return render_template(
            "career_recommendation.html",
            recommendations=recommendations,
            user=user
        )

    except Exception as e:

        return (
            f"❌ Error generating "
            f"recommendations: {e}"
        )

    finally:

        cursor.close()
        connection.close()


# =========================================================
# CAREER DETAILS
# =========================================================

@app.route("/career/<int:career_id>")
def career_details(career_id):

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )

    connection = get_connection()

    if not connection:

        return "❌ Database connection failed!"

    cursor = connection.cursor(
        dictionary=True
    )

    try:

        cursor.execute(
            """
            SELECT
                career_id,
                career_name,
                description,
                required_skills,
                education,
                average_salary,
                job_growth
            FROM careers
            WHERE career_id = %s
            """,
            (career_id,)
        )

        career = cursor.fetchone()

        if not career:

            return "❌ Career not found!"

        skills = [
            skill.strip()
            for skill in
            career["required_skills"].split(",")
            if skill.strip()
        ]

        roadmap = [
            "Learn the required programming fundamentals",
            "Build strong technical skills",
            "Practice problem solving",
            "Work on real-world projects",
            "Build a strong resume and portfolio",
            "Prepare for technical interviews",
            "Apply for relevant internships and jobs"
        ]

        return render_template(
            "career_detail.html",
            career=career,
            skills=skills,
            roadmap=roadmap
        )

    except Exception as e:

        return (
            f"❌ Error loading career: {e}"
        )

    finally:

        cursor.close()
        connection.close()


# =========================================================
# RESUME ANALYSIS
# =========================================================

@app.route(
    "/resume-analysis",
    methods=["GET", "POST"]
)
def resume_analysis():

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )

    if request.method == "GET":

        return render_template(
            "resume_analysis.html"
        )

    if "resume" not in request.files:

        return render_template(
            "resume_analysis.html",
            error="Please select a resume PDF."
        )

    file = request.files["resume"]

    if file.filename == "":

        return render_template(
            "resume_analysis.html",
            error="Please select a resume PDF."
        )

    if not allowed_file(
        file.filename
    ):

        return render_template(
            "resume_analysis.html",
            error="Only PDF files are allowed."
        )

    try:

        file.stream.seek(0)

        file_header = (
            file.stream.read(5)
        )

        file.stream.seek(0)

    except Exception:

        return render_template(
            "resume_analysis.html",
            error=(
                "Unable to read "
                "the uploaded file."
            )
        )

    if file_header != b"%PDF-":

        return render_template(
            "resume_analysis.html",
            error=(
                "The uploaded file "
                "is not a valid PDF."
            )
        )

    original_filename = secure_filename(
        file.filename
    )

    unique_filename = (
        str(session["user_id"])
        + "_"
        + uuid.uuid4().hex
        + "_"
        + original_filename
    )

    file_path = os.path.join(
        UPLOAD_FOLDER,
        unique_filename
    )

    try:

        file.save(file_path)

    except Exception as e:

        return render_template(
            "resume_analysis.html",
            error=(
                f"Unable to save resume: {e}"
            )
        )

    session[
        "resume_filename"
    ] = unique_filename

    try:

        resume_text = (
            extract_text_from_pdf(
                file_path
            )
        )

    except Exception as e:

        return render_template(
            "resume_analysis.html",
            error=(
                "Resume text extraction "
                f"failed: {e}"
            )
        )

    if not resume_text:

        return render_template(
            "resume_analysis.html",
            error=(
                "The PDF was uploaded successfully, "
                "but no readable text was found."
            )
        )

    session[
        "resume_text"
    ] = resume_text

    try:

        analysis = analyze_resume(
            resume_text
        )

    except Exception as e:

        return render_template(
            "resume_analysis.html",
            error=(
                f"Resume analysis failed: {e}"
            ),
            uploaded=True,
            filename=original_filename,
            resume_text=resume_text
        )

    try:

        ats_score = calculate_ats_score(
            resume_text,
            analysis
        )

    except Exception as e:

        return render_template(
            "resume_analysis.html",
            error=(
                "ATS score calculation "
                f"failed: {e}"
            ),
            uploaded=True,
            filename=original_filename,
            resume_text=resume_text,
            analysis=analysis
        )

    session[
        "resume_analysis"
    ] = analysis

    session[
        "ats_score"
    ] = ats_score

    return render_template(
        "resume_analysis.html",
        uploaded=True,
        filename=original_filename,
        resume_text=resume_text,
        analysis=analysis,
        ats_score=ats_score
    )


# =========================================================
# ATS SCORE
# =========================================================

@app.route("/ats-score")
def ats_score():

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )

    ats_result = session.get(
        "ats_score"
    )

    return render_template(
        "ats_score.html",
        ats_score=ats_result
    )


# =========================================================
# SCHOLARSHIPS
# =========================================================

@app.route("/scholarships")
def scholarships():

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )

    connection = get_connection()

    if not connection:

        return "❌ Database connection failed!"

    cursor = connection.cursor(
        dictionary=True
    )

    try:

        cursor.execute(
            """
            SELECT
                scholarship_id,
                name,
                provider,
                amount,
                income_limit,
                min_marks,
                category_required,
                course_required,
                state_required,
                deadline,
                description,
                application_link
            FROM scholarships
            ORDER BY
                deadline IS NULL,
                deadline ASC
            """
        )

        scholarship_list = (
            cursor.fetchall()
        )

        return render_template(
            "scholarships.html",
            scholarships=scholarship_list
        )

    except Exception as e:

        return (
            f"❌ Scholarship loading failed: {e}"
        )

    finally:

        cursor.close()
        connection.close()


# =========================================================
# APPLY FOR SCHOLARSHIP
# =========================================================

@app.route(
    "/apply-scholarship/<int:scholarship_id>"
)
def apply_scholarship(
    scholarship_id
):

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )

    connection = get_connection()

    if not connection:

        return "❌ Database connection failed!"

    cursor = connection.cursor(
        dictionary=True
    )

    try:

        cursor.execute(
            """
            SELECT
                scholarship_id,
                name,
                application_link
            FROM scholarships
            WHERE scholarship_id = %s
            """,
            (scholarship_id,)
        )

        scholarship = cursor.fetchone()

        if not scholarship:

            return "❌ Scholarship not found!"

        cursor.execute(
            """
            SELECT
                application_id,
                status
            FROM applications
            WHERE
                user_id = %s
                AND scholarship_id = %s
            """,
            (
                session["user_id"],
                scholarship_id
            )
        )

        existing = cursor.fetchone()

        if not existing:

            cursor.execute(
                """
                INSERT INTO applications
                (
                    user_id,
                    scholarship_id,
                    status
                )
                VALUES
                (
                    %s,
                    %s,
                    'pending'
                )
                """,
                (
                    session["user_id"],
                    scholarship_id
                )
            )

            connection.commit()

        elif existing["status"] == "saved":

            cursor.execute(
                """
                UPDATE applications
                SET status = 'pending'
                WHERE application_id = %s
                """,
                (
                    existing["application_id"],
                )
            )

            connection.commit()

        application_link = (
            scholarship.get(
                "application_link"
            )
        )

        if application_link:

            return redirect(
                application_link
            )

        return redirect(
            url_for(
                "applications_history"
            )
        )

    except Exception as e:

        connection.rollback()

        return (
            f"❌ Application failed: {e}"
        )

    finally:

        cursor.close()
        connection.close()


# =========================================================
# APPLICATION HISTORY
# =========================================================

@app.route("/applications")
def applications_history():

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )

    connection = get_connection()

    if not connection:

        return "❌ Database connection failed!"

    cursor = connection.cursor(
        dictionary=True
    )

    try:

        cursor.execute(
            """
            SELECT
                a.application_id,
                a.status,
                a.applied_date,
                s.scholarship_id,
                s.name,
                s.provider,
                s.amount,
                s.deadline,
                s.application_link
            FROM applications a
            INNER JOIN scholarships s
                ON a.scholarship_id =
                   s.scholarship_id
            WHERE a.user_id = %s
            ORDER BY
                a.applied_date DESC
            """,
            (
                session["user_id"],
            )
        )

        application_list = (
            cursor.fetchall()
        )

        return render_template(
            "applications.html",
            applications=application_list
        )

    except Exception as e:

        return (
            "❌ Applications history "
            f"loading failed: {e}"
        )

    finally:

        cursor.close()
        connection.close()


# =========================================================
# CONFIRM SCHOLARSHIP SUBMISSION
# =========================================================

@app.route(
    "/confirm-application/<int:application_id>",
    methods=["POST"]
)
def confirm_application(
    application_id
):

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )

    connection = get_connection()

    if not connection:

        return "❌ Database connection failed!"

    cursor = connection.cursor()

    try:

        cursor.execute(
            """
            UPDATE applications
            SET status = 'applied'
            WHERE
                application_id = %s
                AND user_id = %s
                AND status = 'pending'
            """,
            (
                application_id,
                session["user_id"]
            )
        )

        connection.commit()

        return redirect(
            url_for(
                "applications_history"
            )
        )

    except Exception as e:

        connection.rollback()

        return (
            f"❌ Confirmation failed: {e}"
        )

    finally:

        cursor.close()
        connection.close()


# =========================================================
# SKILL GAP ANALYSIS
# =========================================================

@app.route("/skill-gap")
def skill_gap():

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )

    connection = get_connection()

    if not connection:

        return "❌ Database connection failed!"

    cursor = connection.cursor(
        dictionary=True
    )

    try:

        cursor.execute(
            """
            SELECT
                user_id,
                full_name,
                branch,
                skills
            FROM users
            WHERE user_id = %s
            """,
            (
                session["user_id"],
            )
        )

        user = cursor.fetchone()

        if not user:

            return redirect(
                url_for("login")
            )

        # =================================================
        # GET SKILLS FROM PROFILE
        # =================================================

        profile_skills = build_skill_set(
            user.get("skills", "")
        )

        # =================================================
        # ALSO CHECK RESUME ANALYSIS
        # =================================================

        resume_skills = set()

        resume_analysis_data = session.get(
            "resume_analysis",
            {}
        )

        if isinstance(
            resume_analysis_data,
            dict
        ):

            extracted_skills = (
                resume_analysis_data.get(
                    "skills",
                    []
                )
            )

            if isinstance(
                extracted_skills,
                list
            ):

                for skill in extracted_skills:

                    resume_skills.update(
                        build_skill_set(
                            str(skill)
                        )
                    )

            elif isinstance(
                extracted_skills,
                str
            ):

                resume_skills.update(
                    build_skill_set(
                        extracted_skills
                    )
                )

        # =================================================
        # COMBINE PROFILE + RESUME SKILLS
        # =================================================

        user_skills = (
            profile_skills
            |
            resume_skills
        )

        # =================================================
        # TARGET CAREER
        # =================================================

        target_career = session.get(
            "target_career",
            "Software Developer"
        )

        # =================================================
        # SOFTWARE DEVELOPER SKILLS
        # =================================================

        required_skills = [
            "Python",
            "Java",
            "Data Structures",
            "Algorithms",
            "SQL",
            "Git",
            "Problem Solving",
            "HTML",
            "CSS",
            "JavaScript"
        ]

        strong_skills = []

        missing_skills = []

        # =================================================
        # MATCH SKILLS
        # =================================================

        for skill in required_skills:

            required = normalize_skill(
                skill
            )

            if required in user_skills:

                strong_skills.append(
                    skill
                )

            else:

                missing_skills.append(
                    skill
                )

        # =================================================
        # MATCH PERCENTAGE
        # =================================================

        total_skills = len(
            required_skills
        )

        matched_count = len(
            strong_skills
        )

        skill_match_percentage = (
            matched_count
            /
            total_skills
            *
            100
        )

        # =================================================
        # ROADMAP
        # =================================================

        roadmap = [
            "Learn programming fundamentals",
            "Practice Data Structures and Algorithms",
            "Strengthen SQL and database concepts",
            "Learn Git and GitHub",
            "Practice problem solving and coding questions",
            "Build 2-3 real-world projects",
            "Improve your resume and portfolio",
            "Prepare for technical interviews"
        ]

        session[
            "target_career"
        ] = target_career

        return render_template(
            "skill_gap.html",
            user=user,
            target_career=target_career,
            strong_skills=strong_skills,
            missing_skills=missing_skills,
            skill_match_percentage=skill_match_percentage,
            roadmap=roadmap
        )

    except Exception as e:

        return (
            f"❌ Skill Gap Error: {e}"
        )

    finally:

        cursor.close()
        connection.close()


# =========================================================
# LEARNING ROADMAP
# =========================================================

@app.route("/learning-roadmap")
def learning_roadmap():

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )

    connection = get_connection()

    if not connection:

        return "❌ Database connection failed!"

    cursor = connection.cursor(
        dictionary=True
    )

    try:

        cursor.execute(
            """
            SELECT
                user_id,
                full_name,
                branch
            FROM users
            WHERE user_id = %s
            """,
            (
                session["user_id"],
            )
        )

        user = cursor.fetchone()

        if not user:

            return redirect(
                url_for("login")
            )

        target_career = session.get(
            "target_career",
            "Software Developer"
        )

        roadmap = get_learning_roadmap(
            target_career
        )

        return render_template(
            "learning_roadmap.html",
            user=user,
            target_career=target_career,
            roadmap=roadmap
        )

    except Exception as e:

        return (
            f"Learning Roadmap Error: {e}"
        )

    finally:

        cursor.close()
        connection.close()
# =========================================================
# INTERVIEW PREPARATION
# =========================================================

@app.route("/interview")
def interview():

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )

    return render_template(
        "interview.html"
    )


# =========================================================
# DATABASE TEST
# =========================================================

@app.route("/db-test")
def db_test():

    connection = get_connection()

    if connection:

        connection.close()

        return (
            "✅ CareerCompassDB "
            "connected successfully!"
        )

    return (
        "❌ CareerCompassDB "
        "connection failed!"
    )


# =========================================================
# FILE TOO LARGE
# =========================================================

@app.errorhandler(413)
def file_too_large(error):

    return render_template(
        "resume_analysis.html",
        error=(
            "Resume file is too large. "
            "Maximum size is 5 MB."
        )
    ), 413


# =========================================================
# LOGOUT
# =========================================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect(
        url_for("login")
    )


# =========================================================
# RUN APPLICATION
# =========================================================

if __name__ == "__main__":

    app.run(
        debug=True
    )