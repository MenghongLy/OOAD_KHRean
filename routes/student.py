from flask import Blueprint, render_template, flash, redirect, url_for, request, jsonify, send_file
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from models.student import Student
from models.assignment import Assignment
from models.submission import Submission
from models.class_model import Class, class_student
from models.user import User
from models.teacher import Teacher
from extensions import db
from sqlalchemy import func
from werkzeug.utils import secure_filename
import os
from utils.helpers import generate_secure_filename, validate_file_extension, validate_file_mime_type

student_bp = Blueprint("student_bp", __name__, url_prefix="/student")

# Configuration for file uploads
UPLOAD_FOLDER = 'uploads/submissions'
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'txt', 'zip'}


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_student_or_redirect():
    """Helper function to get student profile or redirect if not found"""
    student = Student.query.filter_by(user_id=current_user.id).first()
    if not student:
        flash("Student profile not found. Please contact administrator.", "danger")
        return None
    return student


def get_student_classes(student):
    """Helper function to safely get student's classes list"""
    try:
        # Try dynamic relationship first
        if hasattr(student.classes, 'all'):
            return student.classes.all()
        else:
            # If it's already a list, return it directly
            return student.classes if student.classes else []
    except Exception:
        # Fallback: query classes directly
        from models.class_model import class_student
        return Class.query.join(class_student).filter(
            class_student.c.student_id == student.id
        ).all()


def is_student_enrolled(student, class_obj):
    """Helper function to check if student is enrolled in a class"""
    try:
        enrolled_classes = get_student_classes(student)
        enrolled_class_ids = [c.id for c in enrolled_classes]
        return class_obj.id in enrolled_class_ids
    except Exception:
        # Fallback: query the association table directly
        from models.class_model import class_student
        result = db.session.query(class_student).filter_by(
            student_id=student.id,
            class_id=class_obj.id
        ).first()
        return result is not None


def calculate_letter_grade(percentage):
    """Convert percentage to letter grade"""
    if percentage >= 97:
        return "A+"
    elif percentage >= 93:
        return "A"
    elif percentage >= 90:
        return "A-"
    elif percentage >= 87:
        return "B+"
    elif percentage >= 83:
        return "B"
    elif percentage >= 80:
        return "B-"
    elif percentage >= 77:
        return "C+"
    elif percentage >= 73:
        return "C"
    elif percentage >= 70:
        return "C-"
    elif percentage >= 67:
        return "D+"
    elif percentage >= 63:
        return "D"
    elif percentage >= 60:
        return "D-"
    else:
        return "F"


# -------------------------
# Dashboard
# -------------------------
@student_bp.route("/dashboard")
@login_required
def dashboard():
    student = get_student_or_redirect()
    if not student:
        return redirect(url_for('auth_bp.login'))

    # Calculate actual stats
    enrolled_classes = len(get_student_classes(student))

    # Get all assignments and submissions
    pending_assignments = 0
    submitted_assignments = 0
    total_grades = []

    for cls in get_student_classes(student):
        for assignment in cls.assignments.all():
            submission = assignment.submissions.filter_by(
                student_id=student.id).first()
            if submission:
                submitted_assignments += 1
                if submission.grade is not None:
                    total_grades.append(submission.grade)
            else:
                pending_assignments += 1

    average_grade = sum(total_grades) / \
        len(total_grades) if total_grades else 0

    stats = {
        "enrolled_classes": enrolled_classes,
        "pending_assignments": pending_assignments,
        "submitted_assignments": submitted_assignments,
        "average_grade": round(average_grade, 1)
    }

    # Get recent assignments
    recent_assignments = []
    all_cls_assignments = []
    for cls in get_student_classes(student):
        for assignment in cls.assignments.all():
            submission = assignment.submissions.filter_by(
                student_id=student.id).first()
            all_cls_assignments.append({
                'assignment': assignment,
                'submission': submission,
                'class_name': cls.name,
                'due_date': assignment.due_date or datetime.utcnow()
            })
    # Sort by due_date descending and take top 5
    recent_assignments = sorted(
        all_cls_assignments, key=lambda x: x['due_date'], reverse=True)[:5]
    # Remove the helper key
    for a in recent_assignments:
        a.pop('due_date', None)

    # Get recent grades
    recent_grades = []
    all_submissions = list(student.submissions) if student.submissions else []
    # Sort by submitted_at descending
    all_submissions.sort(
        key=lambda s: s.submitted_at if s.submitted_at else datetime.utcnow(), reverse=True)
    for submission in all_submissions[:5]:
        if submission.grade is not None:
            recent_grades.append({
                'assignment_title': submission.assignment.title if submission.assignment else 'Unknown',
                'grade': submission.grade,
                'submitted_at': submission.submitted_at
            })

    return render_template(
        "student/dashboard.html",
        student=student,
        stats=stats,
        assignments=recent_assignments[:5],
        grades=recent_grades,
    )


# -------------------------
# Assignments
# -------------------------
@student_bp.route("/assignments")
@login_required
def assignments():
    student = get_student_or_redirect()
    if not student:
        return redirect(url_for('auth_bp.login'))

    # Get all assignments from student's classes
    all_assignments = []
    subjects = set()

    for cls in get_student_classes(student):
        subjects.add(cls.name)
        for assignment in cls.assignments.all():
            submission = assignment.submissions.filter_by(
                student_id=student.id).first()

            # Determine status
            if submission:
                if submission.grade is not None:
                    status = 'graded'
                else:
                    status = 'submitted'
            else:
                if assignment.due_date and assignment.due_date < datetime.utcnow():
                    status = 'overdue'
                else:
                    status = 'pending'

            # Calculate days left
            days_left = None
            if assignment.due_date and status == 'pending':
                delta = assignment.due_date - datetime.utcnow()
                if delta.days >= 0:
                    days_left = f"{delta.days} days left" if delta.days > 0 else "Due today"

            all_assignments.append({
                'id': assignment.id,
                'title': assignment.title,
                'description': assignment.description,
                'subject': cls.name,
                'professor': cls.teacher.full_name if cls.teacher else 'No Teacher',
                'due_date': assignment.due_date,
                'due_date_formatted': assignment.due_date.strftime('%b %d, %Y') if assignment.due_date else 'N/A',
                'status': status,
                'status_label': status.upper(),
                'days_left': days_left,
                'submission': submission,
                'grade': submission.grade if submission else None,
                'letter_grade': calculate_letter_grade(submission.grade) if submission and submission.grade else None,
                'submitted_date': submission.submitted_at.strftime('%b %d, %Y') if submission and submission.submitted_at else None,
                'graded_date': submission.graded_at.strftime('%b %d, %Y') if submission and submission.graded_at else None,
                'card_class': 'urgent' if status == 'overdue' else status,
                'icon': 'fas fa-book',
                'icon_bg': 'rgba(59, 130, 246, 0.1)',
                'icon_color': '#3b82f6',
                'grade_class': 'excellent' if submission and submission.grade and submission.grade >= 90 else 'good' if submission and submission.grade and submission.grade >= 80 else 'average',
                'file_path': assignment.file_path
            })

    # Calculate stats
    today = datetime.utcnow()
    week_from_now = today + timedelta(days=7)

    due_this_week = sum(1 for a in all_assignments
                        if a['due_date'] and today <= a['due_date'] <= week_from_now and a['status'] == 'pending')
    pending = sum(1 for a in all_assignments if a['status'] == 'pending')
    submitted = sum(1 for a in all_assignments if a['status'] in [
                    'submitted', 'graded'])
    overdue = sum(1 for a in all_assignments if a['status'] == 'overdue')

    stats = {
        'due_this_week': due_this_week,
        'pending': pending,
        'submitted': submitted,
        'overdue': overdue
    }

    # Organize assignments into sections
    assignment_sections = []

    # Due this week section
    due_this_week_assignments = [a for a in all_assignments
                                 if a['due_date'] and today <= a['due_date'] <= week_from_now and a['status'] == 'pending']
    if due_this_week_assignments:
        assignment_sections.append({
            'key': 'due-this-week',
            'title': 'Due This Week',
            'icon': 'fas fa-calendar-week',
            'badge': {'class': 'urgent', 'text': 'Urgent'},
            'assignments': sorted(due_this_week_assignments, key=lambda x: x['due_date'])
        })

    # Upcoming assignments
    upcoming = [a for a in all_assignments
                if a['status'] == 'pending' and (not a['due_date'] or a['due_date'] > week_from_now)]
    if upcoming:
        assignment_sections.append({
            'key': 'upcoming',
            'title': 'Upcoming Assignments',
            'icon': 'fas fa-calendar-alt',
            'badge': None,
            'assignments': sorted(upcoming, key=lambda x: x['due_date'] if x['due_date'] else datetime.max)
        })

    # Overdue
    overdue_assignments = [
        a for a in all_assignments if a['status'] == 'overdue']
    if overdue_assignments:
        assignment_sections.append({
            'key': 'overdue',
            'title': 'Overdue',
            'icon': 'fas fa-exclamation-triangle',
            'badge': {'class': 'urgent', 'text': 'Action Required'},
            'assignments': sorted(overdue_assignments, key=lambda x: x['due_date'] if x['due_date'] else datetime.min, reverse=True)
        })

    # Recently submitted
    recently_submitted = [
        a for a in all_assignments if a['status'] == 'submitted']
    if recently_submitted:
        assignment_sections.append({
            'key': 'submitted',
            'title': 'Recently Submitted',
            'icon': 'fas fa-check-circle',
            'badge': None,
            'assignments': sorted(recently_submitted, key=lambda x: x['submission'].submitted_at if x['submission'] else datetime.min, reverse=True)[:5]
        })

    # Recently graded
    recently_graded = [a for a in all_assignments if a['status'] == 'graded']
    if recently_graded:
        assignment_sections.append({
            'key': 'graded',
            'title': 'Recently Graded',
            'icon': 'fas fa-star',
            'badge': None,
            'assignments': sorted(recently_graded, key=lambda x: x['submission'].graded_at if x['submission'] and x['submission'].graded_at else datetime.min, reverse=True)[:5]
        })

    return render_template(
        "student/assignments.html",
        student=student,
        stats=stats,
        subjects=sorted(subjects),
        assignment_sections=assignment_sections,
        all_assignments=all_assignments
    )


# -------------------------
# Assignment API Endpoints
# -------------------------
@student_bp.route("/assignments/<int:assignment_id>/details")
@login_required
def assignment_details(assignment_id):
    """Get assignment details for modal"""
    student = get_student_or_redirect()
    if not student:
        return jsonify({'error': 'Student not found'}), 404

    assignment = Assignment.query.get_or_404(assignment_id)

    # Check if student is enrolled in the class
    enrolled_classes = get_student_classes(student)
    if assignment.class_obj not in enrolled_classes:
        return jsonify({'error': 'Unauthorized'}), 403

    # Get assignment files from the upload directory
    attachments = []
    assignment_files_dir = os.path.join('static', 'uploads', 'assignments', str(assignment.id))
    
    if os.path.exists(assignment_files_dir):
        for filename in os.listdir(assignment_files_dir):
            file_path = os.path.join(assignment_files_dir, filename)
            if os.path.isfile(file_path):
                # Determine file icon based on extension
                ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
                icon_map = {
                    'pdf': 'pdf',
                    'doc': 'word',
                    'docx': 'word',
                    'txt': 'alt',
                    'jpg': 'image',
                    'jpeg': 'image',
                    'png': 'image',
                    'xlsx': 'excel',
                    'xls': 'excel',
                    'zip': 'archive'
                }
                icon = icon_map.get(ext, 'file')
                
                attachments.append({
                    'filename': filename,
                    'icon': icon,
                    'url': f'/student/assignments/{assignment_id}/download/{filename}'
                })

    return jsonify({
        'id': assignment.id,
        'title': assignment.title,
        'description': assignment.description or 'No description provided',
        'subject': assignment.class_obj.name,
        'professor': assignment.class_obj.teacher.full_name if assignment.class_obj.teacher else 'No Teacher',
        'due_date_formatted': assignment.due_date.strftime('%b %d, %Y at %I:%M %p') if assignment.due_date else 'N/A',
        'weight': 100,
        'attachments': attachments
    })


@student_bp.route("/assignments/<int:assignment_id>/download/<filename>")
@login_required
def download_assignment_file(assignment_id, filename):
    """Download an assignment file"""
    student = get_student_or_redirect()
    if not student:
        return jsonify({'error': 'Student not found'}), 404

    assignment = Assignment.query.get_or_404(assignment_id)

    # Check if student is enrolled in the class
    enrolled_classes = get_student_classes(student)
    if assignment.class_obj not in enrolled_classes:
        return jsonify({'error': 'Unauthorized'}), 403

    # Get the base directory (project root)
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Construct file path
    file_path = os.path.join('static', 'uploads', 'assignments', str(assignment.id), filename)
    full_path = os.path.join(base_dir, file_path)
    
    # Normalize path to handle .. and . correctly
    full_path = os.path.normpath(os.path.abspath(full_path))
    base_dir = os.path.normpath(os.path.abspath(base_dir))
    
    # Security check: ensure file is within project directory
    if not full_path.startswith(base_dir):
        return jsonify({'error': 'Access denied'}), 403
    
    # Security check: ensure file exists
    if not os.path.exists(full_path) or not os.path.isfile(full_path):
        return jsonify({'error': 'File not found'}), 404
    
    # Security check: prevent directory traversal
    if '..' in filename or '/' in filename or '\\' in filename:
        return jsonify({'error': 'Invalid filename'}), 400
    
    return send_file(full_path, as_attachment=False, download_name=filename)


@student_bp.route("/assignments/<int:assignment_id>/feedback")
@login_required
def assignment_feedback(assignment_id):
    """Get assignment feedback for modal"""
    student = get_student_or_redirect()
    if not student:
        return jsonify({'error': 'Student not found'}), 404

    assignment = Assignment.query.get_or_404(assignment_id)
    submission = assignment.submissions.filter_by(
        student_id=student.id).first()

    if not submission or submission.grade is None:
        return jsonify({'error': 'No feedback available'}), 404

    return jsonify({
        'title': assignment.title,
        'grade': submission.grade,
        'letter_grade': calculate_letter_grade(submission.grade),
        'grade_class': 'excellent' if submission.grade >= 90 else 'good' if submission.grade >= 80 else 'average',
        'graded_by': assignment.class_obj.teacher.full_name if assignment.class_obj.teacher else 'Unknown',
        'graded_date': submission.graded_at.strftime('%b %d, %Y at %I:%M %p') if submission.graded_at else 'N/A',
        'feedback': submission.feedback or 'No feedback provided'
    })


@student_bp.route("/assignments/<int:assignment_id>/submission")
@login_required
def assignment_submission(assignment_id):
    """Get assignment submission details for modal"""
    student = get_student_or_redirect()
    if not student:
        return jsonify({'error': 'Student not found'}), 404

    assignment = Assignment.query.get_or_404(assignment_id)
    submission = assignment.submissions.filter_by(
        student_id=student.id).first()

    if not submission:
        return jsonify({'error': 'No submission found'}), 404

    return jsonify({
        'title': assignment.title,
        'submitted_date': submission.submitted_at.strftime('%b %d, %Y at %I:%M %p') if submission.submitted_at else 'N/A',
        'submission_file': os.path.basename(submission.file_path) if submission.file_path else 'No file',
        'file_icon': 'pdf',
        'comments': submission.comments or 'No comments provided',
        'grading_status': 'Graded' if submission.grade is not None else 'Pending grading'
    })


@student_bp.route("/assignments/submit", methods=['POST'])
@login_required
def submit_assignment():
    """Submit an assignment"""
    student = get_student_or_redirect()
    if not student:
        return jsonify({'success': False, 'message': 'Student not found'}), 404

    try:
        assignment_id = request.form.get('assignment_id')
        comments = request.form.get('comments', '')
        file = request.files.get('file')

        if not assignment_id:
            return jsonify({'success': False, 'message': 'Assignment ID required'}), 400

        assignment = Assignment.query.get_or_404(assignment_id)

        # Check if student is enrolled in the class
        enrolled_classes = get_student_classes(student)
        if assignment.class_obj not in enrolled_classes:
            return jsonify({'success': False, 'message': 'Unauthorized'}), 403

        # Check if already submitted
        existing_submission = assignment.submissions.filter_by(
            student_id=student.id).first()
        if existing_submission:
            return jsonify({'success': False, 'message': 'Assignment already submitted'}), 400

        # Handle file upload
        file_path = None
        if file and file.filename:
            # Validate file extension
            if not validate_file_extension(file.filename, ALLOWED_EXTENSIONS):
                return jsonify({'success': False, 'message': 'Invalid file type. Allowed: PDF, DOC, DOCX, TXT, ZIP'}), 400
            
            # Validate MIME type
            allowed_mime_types = [
                'application/pdf',
                'application/msword',
                'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                'text/plain',
                'application/zip'
            ]
            if not validate_file_mime_type(file, allowed_mime_types):
                return jsonify({'success': False, 'message': 'Invalid file type. Allowed: PDF, DOC, DOCX, TXT, ZIP'}), 400
            
            # Generate secure filename
            filename = generate_secure_filename(file.filename)
            if filename:
                os.makedirs(UPLOAD_FOLDER, exist_ok=True)
                file_path = os.path.join(UPLOAD_FOLDER, filename)
                file.save(file_path)
            else:
                return jsonify({'success': False, 'message': 'Invalid filename'}), 400
        else:
            return jsonify({'success': False, 'message': 'No file provided'}), 400

        # Create submission
        submission = Submission(
            assignment_id=assignment_id,
            student_id=student.id,
            file_path=file_path,
            comments=comments,
            submitted_at=datetime.utcnow()
        )

        db.session.add(submission)
        db.session.commit()

        flash('Assignment submitted successfully!', 'success')
        return jsonify({'success': True, 'message': 'Assignment submitted successfully'})

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500


# -------------------------
# Grades
# -------------------------
@student_bp.route("/grades")
@login_required
def grades():
    student = get_student_or_redirect()
    if not student:
        return redirect(url_for('auth_bp.login'))

    # Get all graded submissions
    all_submissions = []
    total_grades = []

    for cls in get_student_classes(student):
        for assignment in cls.assignments.all():
            submission = assignment.submissions.filter_by(
                student_id=student.id).first()
            if submission and submission.grade is not None:
                all_submissions.append({
                    'assignment': assignment,
                    'submission': submission,
                    'class': cls,
                    'teacher': cls.teacher
                })
                total_grades.append(submission.grade)

    # Calculate overall stats
    overall_average = sum(total_grades) / \
        len(total_grades) if total_grades else 0
    overall_letter = calculate_letter_grade(
        overall_average) if total_grades else "N/A"
    graded_count = len(all_submissions)

    # Count pending grades
    pending_grades = 0
    for cls in get_student_classes(student):
        for assignment in cls.assignments.all():
            submission = assignment.submissions.filter_by(
                student_id=student.id).first()
            if submission and submission.grade is None:
                pending_grades += 1

    overall_stats = {
        'average': round(overall_average, 1),
        'letter_grade': overall_letter,
        'graded_count': graded_count,
        'pending_count': pending_grades
    }

    # Calculate performance by subject
    subjects_performance = []
    for cls in get_student_classes(student):
        class_grades = []
        class_submissions = []

        for assignment in cls.assignments.all():
            submission = assignment.submissions.filter_by(
                student_id=student.id).first()
            if submission and submission.grade is not None:
                class_grades.append(submission.grade)
                class_submissions.append(submission)

        if class_grades:
            avg = sum(class_grades) / len(class_grades)
            subjects_performance.append({
                'class': cls,
                'teacher': cls.teacher,
                'average': round(avg, 1),
                'letter_grade': calculate_letter_grade(avg),
                'assignments_count': len(class_submissions),
                'highest': max(class_grades),
                'lowest': min(class_grades)
            })

    # Sort submissions by date
    all_submissions.sort(
        key=lambda x: x['submission'].graded_at or x['submission'].submitted_at, reverse=True)

    # Calculate grade distribution
    grade_distribution = {
        'A': sum(1 for g in total_grades if g >= 90),
        'B': sum(1 for g in total_grades if 80 <= g < 90),
        'C': sum(1 for g in total_grades if 70 <= g < 80),
        'D': sum(1 for g in total_grades if 60 <= g < 70),
        'F': sum(1 for g in total_grades if g < 60)
    }

    total = sum(grade_distribution.values())
    if total > 0:
        grade_distribution_percent = {
            'A': round((grade_distribution['A'] / total) * 100),
            'B': round((grade_distribution['B'] / total) * 100),
            'C': round((grade_distribution['C'] / total) * 100),
            'D': round((grade_distribution['D'] / total) * 100),
            'F': round((grade_distribution['F'] / total) * 100)
        }
    else:
        grade_distribution_percent = {'A': 0, 'B': 0, 'C': 0, 'D': 0, 'F': 0}

    return render_template(
        "student/grades.html",
        student=student,
        overall_stats=overall_stats,
        subjects_performance=subjects_performance,
        all_submissions=all_submissions,
        grade_distribution=grade_distribution_percent
    )


# -------------------------
# Profile
# -------------------------
@student_bp.route("/profile", methods=['GET', 'POST'])
@login_required
def profile():
    student = get_student_or_redirect()
    if not student:
        return redirect(url_for('auth_bp.login'))

    if request.method == 'POST':
        try:
            # Update student fields
            student.first_name = request.form.get('first_name', '').strip()
            student.last_name = request.form.get('last_name', '').strip()
            student.major = request.form.get('major', '').strip()
            student.year = request.form.get('year', '').strip()
            student.section = request.form.get('section', '').strip()

            # Update user email if provided and changed
            new_email = request.form.get('email', '').strip()
            if new_email and new_email != current_user.email:
                # Check if email is already taken
                existing_user = User.query.filter(
                    User.email == new_email,
                    User.id != current_user.id
                ).first()

                if existing_user:
                    flash('Email is already registered to another user.', 'danger')
                    return redirect(url_for('student_bp.profile'))

                current_user.email = new_email

            # Commit all changes
            db.session.commit()
            flash('Profile updated successfully!', 'success')

        except Exception as e:
            db.session.rollback()
            flash(f'Error updating profile: {str(e)}', 'danger')
            print(f"Profile update error: {str(e)}")

        return redirect(url_for('student_bp.profile'))

    # GET request - calculate stats
    enrolled_classes = len(get_student_classes(student))

    total_grades = []
    total_assignments = 0

    for cls in get_student_classes(student):
        for assignment in cls.assignments.all():
            total_assignments += 1
            submission = assignment.submissions.filter_by(
                student_id=student.id).first()
            if submission and submission.grade is not None:
                total_grades.append(submission.grade)

    average_grade = round(sum(total_grades) /
                          len(total_grades), 1) if total_grades else 0

    profile_stats = {
        'courses': enrolled_classes,
        'average_grade': average_grade,
        'total_assignments': total_assignments
    }

    # Get current courses with grades
    current_courses = []
    for cls in get_student_classes(student):
        class_grades = []

        for assignment in cls.assignments.all():
            submission = assignment.submissions.filter_by(
                student_id=student.id).first()
            if submission and submission.grade is not None:
                class_grades.append(submission.grade)

        course_average = round(sum(class_grades) /
                               len(class_grades), 1) if class_grades else None

        current_courses.append({
            'class': cls,
            'teacher': cls.teacher,
            'average': course_average,
            'letter_grade': calculate_letter_grade(course_average) if course_average else 'N/A'
        })

    return render_template(
        "student/profile.html",
        student=student,
        profile_stats=profile_stats,
        current_courses=current_courses
    )


# -------------------------
# Classes - View and Join
# -------------------------
@student_bp.route("/classes")
@login_required
def classes():
    """View available classes and enrolled classes"""
    student = get_student_or_redirect()
    if not student:
        return redirect(url_for('auth_bp.login'))

    # Get all available classes
    all_classes = Class.query.all()
    
    # Get enrolled class IDs
    student_classes = get_student_classes(student)
    enrolled_class_ids = [cls.id for cls in student_classes]
    
    # Separate into enrolled and available
    enrolled_classes = []
    available_classes = []
    
    for cls in all_classes:
        class_info = {
            'id': cls.id,
            'name': cls.name,
            'description': cls.description or 'No description',
            'teacher': cls.teacher.full_name if cls.teacher else 'No Teacher',
            'teacher_id': cls.teacher_id,
            'created_at': cls.created_at.strftime('%b %d, %Y') if cls.created_at else 'N/A',
            'student_count': cls.students.count() if cls.students else 0,
            'assignment_count': cls.assignments.count() if cls.assignments else 0
        }
        
        if cls.id in enrolled_class_ids:
            enrolled_classes.append(class_info)
        else:
            available_classes.append(class_info)
    
    return render_template(
        "student/classes.html",
        student=student,
        enrolled_classes=enrolled_classes,
        available_classes=available_classes
    )


@student_bp.route("/join", methods=['GET', 'POST'])
@login_required
def join_class_page():
    """Page to join a class by entering class code"""
    student = get_student_or_redirect()
    if not student:
        return redirect(url_for('auth_bp.login'))
    
    if request.method == 'POST':
        class_code = request.form.get('class_code', '').strip().upper()
        
        if not class_code:
            flash('Please enter a class code', 'error')
            return render_template("student/join_class.html", student=student)
        
        try:
            cls = Class.query.filter_by(class_code=class_code).first()
            
            if not cls:
                flash('Invalid class code. Please check and try again.', 'error')
                return render_template("student/join_class.html", student=student)
            
            # Check if already enrolled
            if is_student_enrolled(student, cls):
                flash(f'You are already enrolled in {cls.name}', 'info')
                return redirect(url_for('student_bp.classes'))
            
            # Enroll student in class
            student.classes.append(cls)
            db.session.commit()
            
            flash(f'Successfully joined {cls.name}!', 'success')
            return redirect(url_for('student_bp.classes'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error joining class: {str(e)}', 'error')
            return render_template("student/join_class.html", student=student)
    
    return render_template("student/join_class.html", student=student)


@student_bp.route("/join/<class_code>", methods=['GET', 'POST'])
@login_required
def join_class_by_code(class_code):
    """Join a class using a class code (from link or direct entry)"""
    student = get_student_or_redirect()
    if not student:
        return redirect(url_for('auth_bp.login'))
    
    class_code = class_code.strip().upper()
    
    try:
        cls = Class.query.filter_by(class_code=class_code).first()
        
        if not cls:
            flash('Invalid class code. Please check and try again.', 'error')
            return redirect(url_for('student_bp.join_class_page'))
        
        # Check if already enrolled
        if is_student_enrolled(student, cls):
            flash(f'You are already enrolled in {cls.name}', 'info')
            return redirect(url_for('student_bp.classes'))
        
        # If GET request, show confirmation page
        if request.method == 'GET':
            return render_template(
                "student/join_class_confirm.html",
                student=student,
                class_obj=cls,
                class_code=class_code
            )
        
        # If POST request, enroll the student
        student.classes.append(cls)
        db.session.commit()
        
        flash(f'Successfully joined {cls.name}!', 'success')
        return redirect(url_for('student_bp.classes'))
    except Exception as e:
        db.session.rollback()
        flash(f'Error joining class: {str(e)}', 'error')
        return redirect(url_for('student_bp.join_class_page'))


@student_bp.route("/classes/<int:class_id>/join", methods=['POST'])
@login_required
def join_class(class_id):
    """Join a class by ID (legacy route for backward compatibility)"""
    student = get_student_or_redirect()
    if not student:
        return jsonify({'success': False, 'message': 'Student not found'}), 404
    
    try:
        cls = Class.query.get_or_404(class_id)
        
        # Check if already enrolled
        if is_student_enrolled(student, cls):
            return jsonify({'success': False, 'message': 'Already enrolled in this class'}), 400
        
        # Enroll student in class
        student.classes.append(cls)
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'message': f'Successfully joined {cls.name}!'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500


@student_bp.route("/classes/<int:class_id>/leave", methods=['POST'])
@login_required
def leave_class(class_id):
    """Leave a class"""
    student = get_student_or_redirect()
    if not student:
        return jsonify({'success': False, 'message': 'Student not found'}), 404
    
    try:
        cls = Class.query.get_or_404(class_id)
        
        # Check if enrolled
        if not is_student_enrolled(student, cls):
            return jsonify({'success': False, 'message': 'Not enrolled in this class'}), 400
        
        # Remove student from class
        student.classes.remove(cls)
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'message': f'Successfully left {cls.name}'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500
