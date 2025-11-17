from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, send_file
from flask_login import login_required, current_user
from extensions import db
from models.teacher import Teacher
from models.student import Student
from models.class_model import Class
from models.assignment import Assignment
from models.submission import Submission
from datetime import datetime
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
import os
from pathlib import Path
from utils.helpers import generate_secure_filename, validate_file_extension, validate_file_mime_type

teacher_bp = Blueprint("teacher_bp", __name__, url_prefix="/teacher")

# ---------------------------------------------------------
# Helper: Only allow teachers
# ---------------------------------------------------------


def teacher_required(f):
    from functools import wraps

    @wraps(f)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != "teacher":
            flash("Access denied.", "danger")
            return redirect(url_for("auth_bp.login"))
        return f(*args, **kwargs)
    return wrapper


# ---------------------------------------------------------
# Dashboard
# ---------------------------------------------------------
@teacher_bp.route("/dashboard")
@login_required
@teacher_required
def dashboard():
    teacher = Teacher.query.filter_by(user_id=current_user.id).first()

    # Calculate stats
    classes_taught = Class.query.filter_by(teacher_id=teacher.id).all()
    total_students = 0
    for cls in classes_taught:
        total_students += cls.students.count()
    total_classes = len(classes_taught)

    # Pending grading: submissions without a grade
    pending_assignments = Submission.query.join(Assignment, Submission.assignment_id == Assignment.id).join(
        Class, Assignment.class_id == Class.id).filter(Class.teacher_id == teacher.id, Submission.grade == None).count()

    # Upcoming deadlines: assignments with due dates in the future
    from datetime import datetime, timedelta
    upcoming = Assignment.query.join(Class, Assignment.class_id == Class.id).filter(
        Class.teacher_id == teacher.id, Assignment.due_date > datetime.utcnow()).count()

    stats = {
        "total_students": total_students,
        "total_classes": total_classes,
        "pending_assignments": pending_assignments,
        "upcoming_deadlines": upcoming,
    }

    # Recent classes (limit 5)
    recent_classes = Class.query.filter_by(
        teacher_id=teacher.id).limit(5).all()
    classes_formatted = []
    for cls in recent_classes:
        student_count = cls.students.count()
        classes_formatted.append({
            "id": cls.id,
            "name": cls.name,
            "student_count": student_count,
        })

    # Recent assignments (limit 5)
    recent_assignments = Assignment.query.join(Class, Assignment.class_id == Class.id).filter(
        Class.teacher_id == teacher.id).order_by(Assignment.created_at.desc()).limit(5).all()
    assignments_formatted = []
    for assignment in recent_assignments:
        assignments_formatted.append({
            "id": assignment.id,
            "title": assignment.title,
            "due_date": assignment.due_date.strftime("%b %d, %Y") if assignment.due_date else "No date",
            "status": "pending",  # or compute based on submission grades
        })

    # Recent students (limit 5) - those with recent submissions
    recent_students = (
        db.session.query(Student, Assignment, Submission)
        .join(Class, Student.classes)
        .join(Assignment, Assignment.class_id == Class.id)
        .join(Submission, Submission.student_id == Student.id)
        .filter(Class.teacher_id == teacher.id)
        .order_by(Submission.submitted_at.desc())
        .limit(5)
        .all()
    )
    students_formatted = []
    for student, assignment, submission in recent_students:
        students_formatted.append({
            "id": student.id,
            "first_name": student.first_name or "",
            "last_name": student.last_name or "",
            "class_name": assignment.class_obj.name if assignment.class_obj else "",
            "last_assignment": assignment.title,
            "grade": submission.grade if submission.grade else None,
        })

    return render_template("teacher/dashboard.html", teacher=teacher, stats=stats, recent_classes=classes_formatted, recent_assignments=assignments_formatted, recent_students=students_formatted)


# ---------------------------------------------------------
# Students Page
# ---------------------------------------------------------
@teacher_bp.route("/students")
@login_required
@teacher_required
def students():
    teacher = Teacher.query.filter_by(user_id=current_user.id).first()

    # Get all classes taught by this teacher
    classes_taught = Class.query.filter_by(teacher_id=teacher.id).all()

    # Get all students in those classes (remove duplicates)
    all_students = []
    student_ids = set()
    for cls in classes_taught:
        for student in cls.students:
            if student.id not in student_ids:
                all_students.append((student, cls))
                student_ids.add(student.id)

    formatted = []
    for student, cls in all_students:
        formatted.append({
            "id": student.id,
            "full_name": f"{student.first_name or ''} {student.last_name or ''}".strip(),
            "email": student.user.email if student.user else "",
            "class_name": cls.name,
        })

    return render_template("teacher/students.html", teacher=teacher, students=formatted)


# ---------------------------------------------------------
# Classes Page
# ---------------------------------------------------------
@teacher_bp.route("/classes")
@login_required
@teacher_required
def classes():
    teacher = Teacher.query.filter_by(user_id=current_user.id).first()

    classes = Class.query.filter_by(teacher_id=teacher.id).all()

    formatted = []
    for cls in classes:
        student_count = cls.students.count()
        assignment_count = cls.assignments.count()

        formatted.append({
            "id": cls.id,
            "name": cls.name,
            "description": cls.description,
            "class_code": cls.class_code,
            "student_count": student_count,
            "assignment_count": assignment_count,
            "created_at": cls.created_at.strftime('%b %d, %Y') if cls.created_at else 'N/A',
        })

    return render_template("teacher/classes.html", teacher=teacher, classes=formatted)


# ---------------------------------------------------------
# Assignments Page
# ---------------------------------------------------------
@teacher_bp.route("/assignments")
@login_required
@teacher_required
def assignments():
    teacher = Teacher.query.filter_by(user_id=current_user.id).first()

    assignments = (
        db.session.query(Assignment, Class)
        .join(Class, Assignment.class_id == Class.id)
        .filter(Class.teacher_id == teacher.id)
        .all()
    )

    formatted = []
    for assignment, cls in assignments:
        # Count total submissions and graded submissions
        total_submissions = Submission.query.filter_by(
            assignment_id=assignment.id).count()
        graded_submissions = Submission.query.filter_by(
            assignment_id=assignment.id).filter(Submission.grade != None).count()

        # Determine status
        if total_submissions == 0:
            status = "Pending"
        elif graded_submissions == total_submissions:
            status = "Completed"
        else:
            status = "Partial"

        formatted.append({
            "id": assignment.id,
            "title": assignment.title,
            "class_name": cls.name,
            "due_date": assignment.due_date.strftime("%b %d, %Y") if assignment.due_date else "No date",
            "total_submissions": total_submissions,
            "graded": graded_submissions,
            "status": status,
        })

    # Get all classes taught by this teacher for the create assignment modal
    classes_taught = Class.query.filter_by(teacher_id=teacher.id).all()
    classes_formatted = []
    for cls in classes_taught:
        classes_formatted.append({
            "id": cls.id,
            "name": cls.name,
        })

    return render_template("teacher/assignment.html", teacher=teacher, assignments=formatted, classes=classes_formatted)


# ---------------------------------------------------------
# Grades Page
# ---------------------------------------------------------
@teacher_bp.route("/grades")
@login_required
@teacher_required
def grades():
    teacher = Teacher.query.filter_by(user_id=current_user.id).first()

    grades = (
        db.session.query(Submission, Student, Assignment, Class)
        .join(Student, Submission.student_id == Student.id)
        .join(Assignment, Submission.assignment_id == Assignment.id)
        .join(Class, Assignment.class_id == Class.id)
        .filter(Class.teacher_id == teacher.id)
        .all()
    )

    formatted = []
    for submission, student, assignment, cls in grades:
        formatted.append({
            "submission_id": submission.id,
            "student_name": f"{student.first_name or ''} {student.last_name or ''}".strip(),
            "class_name": cls.name,
            "assignment_title": assignment.title,
            "grade": submission.grade if submission.grade else "Not graded",
        })

    return render_template("teacher/grades.html", teacher=teacher, grades=formatted)


# ---------------------------------------------------------
# Profile Page (GET + POST)
# ---------------------------------------------------------
@teacher_bp.route("/profile", methods=["GET", "POST"])
@login_required
@teacher_required
def profile():
    teacher = Teacher.query.filter_by(user_id=current_user.id).first()

    if request.method == "POST":
        try:
            teacher.first_name = request.form.get("first_name", "")
            teacher.last_name = request.form.get("last_name", "")
            teacher.phone = request.form.get("phone", "")
            teacher.bio = request.form.get("bio", "")

            db.session.commit()
            flash("Profile updated!", "success")
        except:
            db.session.rollback()
            flash("Update failed.", "danger")

        return redirect(url_for("teacher_bp.profile"))

    return render_template("teacher/profile.html", teacher=teacher)


# ---------------------------------------------------------
# View Student Details
# ---------------------------------------------------------
@teacher_bp.route("/students/<int:id>")
@login_required
@teacher_required
def view_student(id):
    student = Student.query.get_or_404(id)
    teacher = Teacher.query.filter_by(user_id=current_user.id).first()

    # Check that student is in one of teacher's classes
    # Use safe method to get student classes (handles both dynamic and list)
    student_classes = student.classes.all() if hasattr(student.classes, 'all') else (student.classes if student.classes else [])
    teacher_classes = Class.query.filter_by(teacher_id=teacher.id).all()
    teacher_class_ids = [c.id for c in teacher_classes]

    is_authorized = any(cls.id in teacher_class_ids for cls in student_classes)
    if not is_authorized:
        flash("Access denied.", "danger")
        return redirect(url_for("teacher_bp.students"))

    # Get student submissions and grades
    submissions = Submission.query.filter_by(student_id=student.id).all()

    formatted_submissions = []
    for submission in submissions:
        assignment = Assignment.query.get(submission.assignment_id)
        if assignment and assignment.class_id in teacher_class_ids:
            formatted_submissions.append({
                "id": submission.id,
                "assignment_title": assignment.title,
                "submitted_at": submission.submitted_at.strftime("%b %d, %Y %I:%M %p") if submission.submitted_at else "Not submitted",
                "grade": submission.grade if submission.grade else "Not graded",
                "feedback": submission.feedback or "No feedback yet",
            })

    return render_template("teacher/view_student.html", teacher=teacher, student=student, submissions=formatted_submissions)


# ---------------------------------------------------------
# Change Password
# ---------------------------------------------------------
@teacher_bp.route("/profile/password", methods=["POST"])
@login_required
@teacher_required
def change_password():
    current_password = request.form.get("current_password")
    new_password = request.form.get("new_password")
    confirm = request.form.get("confirm_password")

    if new_password != confirm:
        return jsonify({"success": False, "message": "Passwords do not match"}), 400

    if not check_password_hash(current_user.password, current_password):
        return jsonify({"success": False, "message": "Incorrect current password"}), 400

    current_user.password = generate_password_hash(new_password)
    db.session.commit()

    return jsonify({"success": True, "message": "Password updated"})


# ---------------------------------------------------------
# Grade Submission
# ---------------------------------------------------------
@teacher_bp.route("/submissions/<int:id>/grade", methods=["POST"])
@login_required
@teacher_required
def grade_submission(id):
    submission = Submission.query.get_or_404(id)
    teacher = Teacher.query.filter_by(user_id=current_user.id).first()

    # Verify submission belongs to teacher's class
    assignment = Assignment.query.get(submission.assignment_id)
    cls = Class.query.get(assignment.class_id)
    if cls.teacher_id != teacher.id:
        return jsonify({"success": False, "message": "Unauthorized"}), 403

    grade_str = request.form.get("grade", "").strip()
    feedback = request.form.get("feedback", "").strip()

    # Validate grade
    try:
        grade = float(grade_str)
        if grade < 0 or grade > 100:
            return jsonify({"success": False, "message": "Grade must be between 0 and 100"}), 400
    except (ValueError, TypeError):
        return jsonify({"success": False, "message": "Invalid grade format"}), 400

    submission.grade = grade
    submission.feedback = feedback
    submission.graded_at = datetime.utcnow()

    db.session.commit()

    return jsonify({"success": True, "message": "Grade saved!", "grade": grade})


# ---------------------------------------------------------
# Export Grades
# ---------------------------------------------------------
@teacher_bp.route("/export_grades", methods=["GET"])
@login_required
@teacher_required
def export_grades():
    teacher = Teacher.query.filter_by(user_id=current_user.id).first()

    grades = (
        db.session.query(Submission, Student, Assignment, Class)
        .join(Student, Submission.student_id == Student.id)
        .join(Assignment, Submission.assignment_id == Assignment.id)
        .join(Class, Assignment.class_id == Class.id)
        .filter(Class.teacher_id == teacher.id)
        .all()
    )

    formatted = []
    for submission, student, assignment, cls in grades:
        formatted.append({
            "student": f"{student.first_name or ''} {student.last_name or ''}".strip(),
            "class": cls.name,
            "assignment": assignment.title,
            "grade": submission.grade if submission.grade else "N/A",
        })

    return jsonify({"success": True, "data": formatted})


# ---------------------------------------------------------
# Export Students
# ---------------------------------------------------------
@teacher_bp.route("/export_students", methods=["GET"])
@login_required
@teacher_required
def export_students():
    teacher = Teacher.query.filter_by(user_id=current_user.id).first()
    classes_taught = Class.query.filter_by(teacher_id=teacher.id).all()

    all_students = []
    student_ids = set()
    for cls in classes_taught:
        for student in cls.students:
            if student.id not in student_ids:
                all_students.append((student, cls))
                student_ids.add(student.id)

    formatted = []
    for student, cls in all_students:
        formatted.append({
            "name": f"{student.first_name or ''} {student.last_name or ''}".strip(),
            "email": student.user.email if student.user else "",
            "class": cls.name,
        })

    return jsonify({"success": True, "data": formatted})


# ---------------------------------------------------------
# Create Class
# ---------------------------------------------------------
@teacher_bp.route("/classes", methods=["POST"])
@login_required
@teacher_required
def create_class():
    teacher = Teacher.query.filter_by(user_id=current_user.id).first()

    name = request.form.get("name", "").strip()
    description = request.form.get("description", "").strip()

    if not name:
        return jsonify({"success": False, "message": "Class name is required"}), 400

    cls = Class(name=name, description=description, teacher_id=teacher.id)
    db.session.add(cls)
    db.session.commit()

    # Generate join link
    join_link = cls.get_join_link(request.url_root.rstrip('/'))

    return jsonify({
        "success": True, 
        "message": "Class created!", 
        "class_id": cls.id,
        "class_code": cls.class_code,
        "class_name": cls.name,
        "join_link": join_link
    })


# ---------------------------------------------------------
# Create Assignment
# ---------------------------------------------------------
@teacher_bp.route("/assignments", methods=["POST"])
@login_required
@teacher_required
def create_assignment():
    teacher = Teacher.query.filter_by(user_id=current_user.id).first()

    class_id = request.form.get("class_id", type=int)
    title = request.form.get("title", "").strip()
    description = request.form.get("description", "").strip()
    due_date_str = request.form.get("due_date")

    if not title or not class_id:
        return jsonify({"success": False, "message": "Title and class are required"}), 400

    # Verify class belongs to teacher
    cls = Class.query.get(class_id)
    if not cls or cls.teacher_id != teacher.id:
        return jsonify({"success": False, "message": "Unauthorized"}), 403

    due_date = None
    if due_date_str:
        try:
            due_date = datetime.strptime(due_date_str, "%Y-%m-%d")
        except:
            pass

    assignment = Assignment(
        title=title, description=description, class_id=class_id, due_date=due_date)
    db.session.add(assignment)
    db.session.commit()

    # Handle file uploads
    if 'assignment_file' in request.files:
        files = request.files.getlist('assignment_file')

        # Create upload directory if it doesn't exist
        upload_dir = Path("static/uploads/assignments") / str(assignment.id)
        upload_dir.mkdir(parents=True, exist_ok=True)

        allowed_extensions = {'pdf', 'doc', 'docx',
                              'txt', 'jpg', 'jpeg', 'png', 'xlsx', 'xls'}

        for file in files:
            if file and file.filename:
                # Validate file extension
                if not validate_file_extension(file.filename, allowed_extensions):
                    continue
                
                # Validate MIME type (basic check)
                allowed_mime_types = [
                    'application/pdf',
                    'application/msword',
                    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                    'text/plain',
                    'image/jpeg',
                    'image/png',
                    'application/vnd.ms-excel',
                    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                ]
                if not validate_file_mime_type(file, allowed_mime_types):
                    continue
                
                # Generate secure filename
                filename = generate_secure_filename(file.filename)
                if filename:
                    # Save file
                    file_path = upload_dir / filename
                    file.save(str(file_path))

    return jsonify({"success": True, "message": "Assignment created!", "assignment_id": assignment.id})


# ---------------------------------------------------------
# Upload Avatar
# ---------------------------------------------------------
@teacher_bp.route("/upload_avatar", methods=["POST"])
@login_required
@teacher_required
def upload_avatar():
    teacher = Teacher.query.filter_by(user_id=current_user.id).first()

    if "avatar" not in request.files:
        return jsonify({"success": False, "message": "No file provided"}), 400

    file = request.files["avatar"]
    if file.filename == "":
        return jsonify({"success": False, "message": "No file selected"}), 400

    # For now, just return success without actually saving
    # In production, save file to disk/cloud storage
    return jsonify({"success": True, "message": "Avatar uploaded!"})


# ---------------------------------------------------------
# Update Notifications
# ---------------------------------------------------------
@teacher_bp.route("/update_notifications", methods=["POST"])
@login_required
@teacher_required
def update_notifications():
    teacher = Teacher.query.filter_by(user_id=current_user.id).first()

    # Get notification preferences from form
    email_notifications = request.form.get("email_notifications") == "on"
    sms_notifications = request.form.get("sms_notifications") == "on"

    # In a real app, save these preferences to a NotificationPreference model
    # For now, just return success
    return jsonify({"success": True, "message": "Notification preferences updated!"})


# ---------------------------------------------------------
# View Class Details
# ---------------------------------------------------------
@teacher_bp.route("/classes/<int:class_id>")
@login_required
@teacher_required
def view_class(class_id):
    cls = Class.query.get_or_404(class_id)
    teacher = Teacher.query.filter_by(user_id=current_user.id).first()

    # Check that class belongs to teacher
    if cls.teacher_id != teacher.id:
        flash("Access denied.", "danger")
        return redirect(url_for("teacher_bp.classes"))

    # Get students in this class
    students = cls.students.all()
    students_formatted = []
    for student in students:
        students_formatted.append({
            "id": student.id,
            "full_name": f"{student.first_name or ''} {student.last_name or ''}".strip(),
            "email": student.user.email if student.user else "",
        })

    # Get assignments for this class
    assignments = Assignment.query.filter_by(class_id=class_id).all()
    assignments_formatted = []
    for assignment in assignments:
        submissions_count = assignment.submissions.count() if assignment.submissions else 0
        assignments_formatted.append({
            "id": assignment.id,
            "title": assignment.title,
            "due_date": assignment.due_date.strftime("%b %d, %Y") if assignment.due_date else "No date",
            "submissions": submissions_count,
        })

    return render_template("teacher/view_class.html", teacher=teacher, class_obj=cls, students=students_formatted, assignments=assignments_formatted)


# ---------------------------------------------------------
# View Assignment Details
# ---------------------------------------------------------
@teacher_bp.route("/assignments/<int:assignment_id>")
@login_required
@teacher_required
def view_assignment(assignment_id):
    assignment = Assignment.query.get_or_404(assignment_id)
    teacher = Teacher.query.filter_by(user_id=current_user.id).first()
    cls = Class.query.get(assignment.class_id)

    # Check that assignment's class belongs to teacher
    if cls.teacher_id != teacher.id:
        flash("Access denied.", "danger")
        return redirect(url_for("teacher_bp.assignments"))

    # Get submissions for this assignment
    submissions = Submission.query.filter_by(assignment_id=assignment_id).all()
    submissions_formatted = []
    for submission in submissions:
        student = Student.query.get(submission.student_id)
        submissions_formatted.append({
            "id": submission.id,
            "student_name": f"{student.first_name or ''} {student.last_name or ''}".strip(),
            "student_id": student.id,
            "submitted_at": submission.submitted_at.strftime("%b %d, %Y %I:%M %p") if submission.submitted_at else "Not submitted",
            "grade": submission.grade if submission.grade is not None else "Not graded",
            "file_path": submission.file_path,
            "feedback": submission.feedback or "",
        })

    return render_template("teacher/view_assignment.html", teacher=teacher, assignment=assignment, cls=cls, submissions=submissions_formatted)


# ---------------------------------------------------------
# Download Submission File
# ---------------------------------------------------------
@teacher_bp.route("/submissions/<int:submission_id>/download")
@login_required
@teacher_required
def download_submission(submission_id):
    """Download a submission file"""
    submission = Submission.query.get_or_404(submission_id)
    teacher = Teacher.query.filter_by(user_id=current_user.id).first()
    
    # Get the assignment and verify teacher owns the class
    assignment = Assignment.query.get(submission.assignment_id)
    if not assignment:
        flash("Assignment not found.", "danger")
        return redirect(url_for("teacher_bp.assignments"))
    
    cls = Class.query.get(assignment.class_id)
    if not cls or cls.teacher_id != teacher.id:
        flash("Access denied.", "danger")
        return redirect(url_for("teacher_bp.assignments"))
    
    # Check if file exists
    if not submission.file_path:
        flash("No file attached to this submission.", "warning")
        return redirect(url_for("teacher_bp.view_assignment", assignment_id=assignment.id))
    
    # Get the base directory (project root)
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Handle Windows path separators and normalize
    file_path = submission.file_path.replace('\\', os.sep).replace('/', os.sep)
    
    # Construct full path
    if os.path.isabs(file_path):
        full_path = file_path
    else:
        # Relative path from project root
        full_path = os.path.join(base_dir, file_path)
    
    # Normalize path to handle .. and . correctly
    full_path = os.path.normpath(os.path.abspath(full_path))
    
    # Security check: ensure file is within project directory
    if not full_path.startswith(base_dir):
        flash("Access denied.", "danger")
        return redirect(url_for("teacher_bp.view_assignment", assignment_id=assignment.id))
    
    # Security check: ensure file exists
    if not os.path.exists(full_path) or not os.path.isfile(full_path):
        flash("File not found.", "danger")
        return redirect(url_for("teacher_bp.view_assignment", assignment_id=assignment.id))
    
    # Get filename for download
    filename = os.path.basename(full_path)
    
    return send_file(full_path, as_attachment=False, download_name=filename)


# ---------------------------------------------------------
# Grade Assignment (alias to view_assignment)
# ---------------------------------------------------------
@teacher_bp.route("/assignments/<int:assignment_id>/grade")
@login_required
@teacher_required
def grade_assignment(assignment_id):
    # Same as view_assignment - shows submission list with grading capability
    return view_assignment(assignment_id)
