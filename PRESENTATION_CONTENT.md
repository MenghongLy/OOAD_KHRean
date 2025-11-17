# 📊 Assignment Management System (AMS) - Complete Presentation Content

---

## 🎯 **SLIDE 1: Title Slide**

### Title
**Assignment Management System (AMS)**
*EduHub - Digital Learning Platform*

### Subtitle
A Web-Based Assignment Management System for Educational Institutions

### Presenter Information
- Course: Object-Oriented Analysis and Design (OOAD)
- Year 3, Semester 1
- Royal University of Phnom Penh (RUPP)

---

## 📋 **SLIDE 2: Project Overview**

### Title
**Project Description**

### Content Points
- **Web-based platform** for managing assignments, submissions, and grading
- **Three-tier user system**: Student, Teacher, Administrator roles
- **Complete workflow**: From assignment creation to grading and feedback
- **Class management**: Teachers create classes, students join via unique codes
- **File upload system**: Secure submission and assignment file handling
- **Real-time tracking**: Monitor submissions, grades, and student progress

---

## 🎯 **SLIDE 3: Project Objectives**

### Title
**Project Objectives**

### Content Points
- **Digitize assignment workflow**: Eliminate paper-based processes
- **Role-based access control**: Clear separation of responsibilities
- **Improve communication**: Direct teacher-student interaction
- **Streamline grading**: Efficient submission review and feedback system
- **Track student progress**: Comprehensive grade tracking and analytics
- **Enhance user experience**: Intuitive interface for all user types

---

## 👥 **SLIDE 4: User Roles**

### Title
**System Users & Roles**

### Content Points
- **Student**: Submit assignments, view grades, join classes
- **Teacher**: Create assignments, grade submissions, manage classes
- **Administrator**: System-wide management, user administration, monitoring

---

## 🎓 **SLIDE 5: Student Features**

### Title
**Student Features**

### Content Points
- **Dashboard**: Overview of assignments, classes, and grades
- **View Assignments**: Browse all assigned work with due dates
- **Assignment Details**: View full assignment description and attached files
- **Submit Assignments**: Upload files (PDF, DOC, DOCX, TXT, ZIP)
- **Submission History**: Track all past submissions
- **View Grades**: See grades and teacher feedback
- **Join Classes**: Enter class code or use join link
- **Class Management**: View enrolled classes, leave classes
- **Profile Management**: Update personal information

---

## 👨‍🏫 **SLIDE 6: Teacher Features**

### Title
**Teacher Features**

### Content Points
- **Dashboard**: Statistics on classes, students, and pending grading
- **Create Classes**: Generate unique 6-character class codes
- **Share Class Codes**: Copy code or shareable join links
- **Create Assignments**: Set title, description, due date, attach files
- **Edit/Delete Assignments**: Manage assignment lifecycle
- **View Submissions**: See all student submissions per assignment
- **Download Files**: Access submitted student work
- **Grade Submissions**: Assign grades (0-100) and provide feedback
- **View Students**: See all students in each class
- **Export Grades**: Download grade reports as CSV
- **Export Student Lists**: Export class rosters
- **Profile Management**: Update teacher profile and avatar

---

## 🔧 **SLIDE 7: Admin Features**

### Title
**Administrator Features**

### Content Points
- **Dashboard**: System-wide statistics and overview
- **User Management**: Create, edit, delete, and view all users
- **Teacher Management**: Add teachers, view teacher profiles
- **Student Management**: Add students, view student profiles
- **Role Management**: Change user roles (with security restrictions)
- **Assignment Management**: View and delete assignments system-wide
- **Activity Log**: Monitor system activity
- **System Settings**: Configure application settings
- **Profile Management**: Update admin profile

---

## 🛠️ **SLIDE 8: System Features**

### Title
**Core System Features**

### Content Points
- **User Authentication**: Flask-Login with secure session management
- **Password Security**: Werkzeug password hashing (bcrypt)
- **Role-Based Access Control**: Decorators ensure proper authorization
- **CSRF Protection**: Flask-WTF CSRF tokens on all forms
- **File Upload Security**: Secure filename generation, extension validation
- **Template Inheritance**: Jinja2 templates with base.html structure
- **Flask Blueprints**: Modular routing (auth, student, teacher, admin)
- **SQLAlchemy ORM**: Database abstraction layer
- **Automatic Schema Detection**: Detects and handles database schema changes
- **Error Handling**: Custom 404, 403, 500 error pages
- **Responsive Design**: Bootstrap 5 with custom styling
- **Session Management**: 30-minute session timeout

---

## 💻 **SLIDE 9: Technology Stack**

### Title
**Technology Stack**

### Content Points
- **Backend Framework**: Python 3.11+ with Flask 3.0+
- **Database**: SQLite (development) / MySQL (production-ready)
- **ORM**: SQLAlchemy 2.0+ (Flask-SQLAlchemy)
- **Authentication**: Flask-Login 0.6.3
- **Security**: Flask-WTF (CSRF protection), Werkzeug (password hashing)
- **Frontend**: HTML5, CSS3, Bootstrap 5.3
- **Icons**: Font Awesome 6.4
- **Templating**: Jinja2 (Flask's default)
- **Database Migrations**: Flask-Migrate 4.0+ (optional)
- **Environment Config**: python-dotenv
- **File Handling**: Werkzeug secure file utilities

---

## 📁 **SLIDE 10: Project Structure**

### Title
**Project Folder Structure**

### Content Points
- **`/routes`**: Application routing logic (Blueprints)
- **`/models`**: Database models and relationships
- **`/templates`**: HTML templates with Jinja2
- **`/static`**: CSS, JavaScript, images, uploads
- **`/utils`**: Helper functions and utilities
- **`/tests`**: Unit tests for authentication
- **`/instance`**: Database file (SQLite)
- **`/logs`**: Application log files
- **Root files**: `app.py`, `config.py`, `extensions.py`

---

## 📂 **SLIDE 11: Detailed Folder Descriptions**

### Title
**Folder Structure Details**

### `/routes` Folder
- **Purpose**: Contains all route handlers organized by user role
- **Files**:
  - `auth.py`: Login, register, logout routes
  - `student.py`: All student-specific routes (dashboard, assignments, submissions, classes, grades)
  - `teacher.py`: All teacher-specific routes (dashboard, classes, assignments, grading, students)
  - `admin.py`: All admin-specific routes (user management, system settings, activity logs)
- **Architecture**: Uses Flask Blueprints for modular organization
- **Security**: Each blueprint has role-based decorators (`@teacher_required`, `@admin_required`)

### `/models` Folder
- **Purpose**: Defines database schema and relationships
- **Files**:
  - `user.py`: User model (authentication, roles)
  - `student.py`: Student profile model
  - `teacher.py`: Teacher profile model
  - `class_model.py`: Class model with unique codes
  - `assignment.py`: Assignment model
  - `submission.py`: Submission model with grading
  - `models.py`: Central import file for all models
- **Relationships**: One-to-one (User-Student, User-Teacher), One-to-many (Class-Students, Assignment-Submissions)

### `/templates` Folder
- **Purpose**: HTML templates using Jinja2 templating engine
- **Structure**:
  - `base.html`: Base template with sidebar, navigation, styling
  - `home.html`: Landing page
  - `login.html`, `register.html`: Authentication pages
  - `/student/`: Student-specific templates (dashboard, assignments, classes, grades, profile)
  - `/teacher/`: Teacher-specific templates (dashboard, classes, assignments, students, grades, profile)
  - `/admin/`: Admin-specific templates (dashboard, user management, settings)
  - `/errors/`: Custom error pages (404, 403, 500)
- **Features**: Template inheritance, CSRF token injection, role-based navigation

### `/static` Folder
- **Purpose**: Static assets (CSS, JavaScript, images, uploaded files)
- **Structure**:
  - `/css/`: Bootstrap CSS, custom style.css
  - `/js/`: Bootstrap JavaScript, custom main.js
  - `/uploads/`: User-uploaded files
    - `/assignments/`: Assignment files uploaded by teachers
    - `/submissions/`: Student submission files
    - `/avatars/`: User profile pictures
    - `/images/`: Static images (login/signup illustrations)

### `/utils` Folder
- **Purpose**: Reusable utility functions
- **Files**:
  - `helpers.py`: Validation functions (email, password), file handling, display name formatting
- **Functions**: `validate_email()`, `validate_password()`, `sanitize_username()`, `generate_secure_filename()`, `get_user_display_name()`

### `/tests` Folder
- **Purpose**: Unit tests for application functionality
- **Files**:
  - `test_auth.py`: Authentication tests
  - `test_login.py`: Login functionality tests

### Root Configuration Files
- **`app.py`**: Main application file, creates Flask app, initializes extensions, registers blueprints, handles database setup
- **`config.py`**: Configuration class with database URI, secret key, upload settings, CSRF settings
- **`extensions.py`**: Initializes Flask extensions (SQLAlchemy, LoginManager, CSRFProtect)
- **`requirements.txt`**: Python package dependencies
- **`fix_database.py`**: Database migration and repair utility

---

## 🗄️ **SLIDE 12: Database Entities**

### Title
**Database Schema & Entities**

### Content Points
- **User**: Core authentication (username, email, password, role, status, timestamps)
- **Student**: Student profile (first_name, last_name, major, year, section)
- **Teacher**: Teacher profile (first_name, last_name, department, subject, phone, bio, avatar)
- **Class**: Class/course (name, description, unique 6-character code, teacher_id)
- **Assignment**: Assignment details (title, description, due_date, status, file_path, class_id)
- **Submission**: Student submissions (file_path, comments, grade, feedback, timestamps)
- **Association Table**: `class_student` (many-to-many relationship)

---

## 🔗 **SLIDE 13: Entity Relationships (ERD)**

### Title
**Entity Relationship Diagram**

### Relationships
- **User 1:1 Student**: One user account has one student profile
- **User 1:1 Teacher**: One user account has one teacher profile
- **Teacher 1:M Classes**: One teacher can create multiple classes
- **Class M:M Students**: Many students can enroll in many classes (via `class_student` table)
- **Class 1:M Assignments**: One class can have multiple assignments
- **Teacher 1:M Assignments**: One teacher can create multiple assignments
- **Assignment 1:M Submissions**: One assignment can have multiple student submissions
- **Student 1:M Submissions**: One student can submit multiple assignments

### Key Features
- **Cascade Deletes**: Deleting a user deletes associated student/teacher profile
- **Cascade Deletes**: Deleting a class deletes all assignments and enrollments
- **Cascade Deletes**: Deleting an assignment deletes all submissions
- **Soft Deletes**: Teacher deletion sets assignments.teacher_id to NULL

---

## 🔄 **SLIDE 14: User Flow Diagrams**

### Title
**User Workflow**

### Student Flow
1. **Login** → Authenticate with email/password
2. **Dashboard** → View assignments, classes, recent activity
3. **Join Class** → Enter class code or click join link
4. **View Assignment** → See assignment details and download files
5. **Submit Assignment** → Upload file with optional comments
6. **View Grade** → Check grade and teacher feedback
7. **Profile** → Update personal information

### Teacher Flow
1. **Login** → Authenticate with email/password
2. **Dashboard** → View statistics (classes, students, pending grading)
3. **Create Class** → Generate unique class code
4. **Share Code** → Copy code or share join link with students
5. **Create Assignment** → Set details, due date, upload file
6. **View Submissions** → See all student submissions
7. **Grade Submission** → Assign grade (0-100) and feedback
8. **Export Data** → Download grades or student lists as CSV

### Admin Flow
1. **Login** → Authenticate with email/password
2. **Dashboard** → View system-wide statistics
3. **Manage Users** → Create, edit, delete users
4. **Manage Roles** → Change user roles (with restrictions)
5. **View Activity** → Monitor system activity log
6. **System Settings** → Configure application settings

---

## ✨ **SLIDE 15: Key Strengths**

### Title
**Project Strengths**

### Content Points
- **Modular Architecture**: Flask Blueprints enable clean separation of concerns
- **Scalable Design**: Easy to add new features or modify existing ones
- **Security First**: CSRF protection, password hashing, role-based access control
- **User-Friendly**: Intuitive interface with clear navigation
- **Real-World Application**: Addresses actual educational workflow needs
- **Code Quality**: Well-organized, commented, follows Flask best practices
- **Database Design**: Proper relationships, cascade deletes, indexes for performance
- **Error Handling**: Comprehensive error pages and user-friendly messages
- **File Security**: Secure filename generation, extension validation
- **Responsive Design**: Works on desktop and mobile devices

---

## 🚀 **SLIDE 16: Future Improvements**

### Title
**Future Enhancements**

### Content Points
- **Email Notifications**: Send assignment reminders and grade notifications
- **In-App Messaging**: Direct communication between teachers and students
- **File Preview**: View PDFs and documents in browser without download
- **Analytics Dashboard**: Charts and graphs for grade distribution, submission rates
- **Rubric-Based Grading**: Structured grading rubrics for assignments
- **Discussion Forums**: Class discussion boards for Q&A
- **Calendar Integration**: Sync assignments with Google Calendar
- **Mobile App**: Native iOS/Android applications
- **Real-Time Notifications**: WebSocket-based live updates
- **Plagiarism Detection**: Integration with plagiarism checking services
- **Video Submissions**: Support for video file uploads
- **Peer Review**: Students can review each other's work

---

## 📝 **SLIDE 17: Technical Implementation Highlights**

### Title
**Technical Implementation**

### Content Points
- **Class Code Generation**: Unique 6-character alphanumeric codes using `secrets` module
- **Join Link System**: Shareable URLs for easy class enrollment
- **Automatic Schema Detection**: App detects outdated database and recreates tables
- **Helper Functions**: Reusable utilities for validation, file handling, display formatting
- **Secure File Uploads**: Random prefix + timestamp + sanitized filename
- **Letter Grade Conversion**: Percentage to letter grade (A+ to F) calculation
- **Late Submission Detection**: Automatic detection of overdue assignments
- **Export Functionality**: CSV export for grades and student lists
- **Avatar Upload**: Profile picture management for teachers
- **Password Validation**: Minimum 8 characters, requires letter and number

---

## 🎬 **FULL PRESENTATION SCRIPT**

### **Introduction (Slide 1)**
"Good [morning/afternoon], everyone. Today I'm presenting our Assignment Management System, also known as EduHub. This is a comprehensive web-based platform designed to digitize and streamline the assignment workflow in educational institutions. This project was developed for our Object-Oriented Analysis and Design course."

### **Project Overview (Slide 2)**
"Our system is a complete web-based platform that manages the entire assignment lifecycle - from creation to submission to grading. It supports three distinct user roles: Students, Teachers, and Administrators. Each role has access to features specifically designed for their needs. The system includes class management where teachers can create classes with unique codes, and students can easily join using these codes or shareable links, similar to platforms like Microsoft Teams."

### **Objectives (Slide 3)**
"The primary objectives of our system are to digitize the assignment workflow, eliminating paper-based processes. We've implemented clear role-based separation to ensure each user type has appropriate access. The system improves communication between students and teachers through direct interaction channels. We've streamlined the grading process, making it efficient for teachers to review submissions and provide feedback. Additionally, the system tracks student progress comprehensively with grade analytics."

### **User Roles (Slide 4)**
"Our system serves three types of users. Students can submit assignments and track their progress. Teachers can create assignments, manage classes, and grade submissions. Administrators have system-wide control to manage users, monitor activity, and configure settings."

### **Student Features (Slide 5)**
"Students have access to a comprehensive dashboard showing their assignments, classes, and grades. They can view assignment details including descriptions and attached files. The submission system allows students to upload files in multiple formats. Students can track their submission history and view grades with teacher feedback. A key feature is the class joining system - students can enter a 6-character class code or use a shareable link to enroll in classes."

### **Teacher Features (Slide 6)**
"Teachers have powerful tools for managing their classes and assignments. The dashboard provides statistics on classes, students, and pending grading work. Teachers can create classes and automatically generate unique 6-character codes. They can share these codes or create shareable join links. The assignment creation system allows teachers to set titles, descriptions, due dates, and attach files. Teachers can view all submissions, download student work, and grade submissions with numerical grades and written feedback. There's also functionality to export grades and student lists as CSV files."

### **Admin Features (Slide 7)**
"Administrators have system-wide management capabilities. The admin dashboard shows comprehensive statistics across all users and activities. Admins can manage all users - creating, editing, and deleting accounts. They can manage teachers and students separately, view and change user roles with security restrictions, and manage assignments system-wide. The activity log allows monitoring of system usage, and there are system settings for configuration."

### **System Features (Slide 8)**
"Our system implements several important security and architectural features. We use Flask-Login for secure session management and Werkzeug for password hashing. Role-based access control is enforced through decorators. All forms are protected with CSRF tokens using Flask-WTF. File uploads are secured with filename sanitization and extension validation. The application uses Flask Blueprints for modular routing, SQLAlchemy ORM for database operations, and includes automatic schema detection for database migrations."

### **Technology Stack (Slide 9)**
"We built this system using Python 3.11 with Flask 3.0 as our backend framework. For the database, we use SQLite for development, but the system is production-ready for MySQL. SQLAlchemy 2.0 provides our ORM layer. Authentication is handled by Flask-Login, and security features come from Flask-WTF and Werkzeug. The frontend uses HTML5, CSS3, and Bootstrap 5.3 for responsive design, with Font Awesome for icons. We use Jinja2 for templating, which is Flask's default template engine."

### **Project Structure (Slide 10)**
"Our project follows a clean, modular structure. The routes folder contains all our route handlers organized by user role. The models folder defines our database schema. Templates are organized by role in subdirectories. Static assets including CSS, JavaScript, and uploaded files are in the static folder. Utility functions are in the utils folder, and we have a tests folder for unit testing."

### **Folder Details (Slide 11)**
"Let me detail each folder. The routes folder uses Flask Blueprints - we have separate blueprints for authentication, student features, teacher features, and admin features. Each has role-based decorators for security. The models folder contains our database models with proper relationships - one-to-one for user profiles, one-to-many for classes and assignments, and many-to-many for class-student relationships. The templates folder uses Jinja2 template inheritance with a base template, and role-specific templates in subdirectories. The static folder organizes CSS, JavaScript, and uploaded files by type. The utils folder contains helper functions for validation, file handling, and formatting."

### **Database Entities (Slide 12)**
"Our database consists of six main entities. The User entity handles authentication with username, email, password, role, and status. Student and Teacher entities store profile information. The Class entity includes a unique 6-character code for joining. Assignment stores assignment details with due dates and file paths. Submission tracks student submissions with grades and feedback. We also have an association table for the many-to-many relationship between classes and students."

### **ERD Relationships (Slide 13)**
"The relationships in our database are carefully designed. Users have one-to-one relationships with Student and Teacher profiles. Teachers can create multiple classes, and classes can have multiple students through a many-to-many relationship. Classes can have multiple assignments, and assignments can have multiple submissions. We've implemented cascade deletes - when a user is deleted, their profile is deleted; when a class is deleted, all assignments and enrollments are deleted. This maintains data integrity."

### **User Flow (Slide 14)**
"Let me walk through the typical user workflows. For students: they login, view their dashboard, can join classes using codes or links, view assignments, submit work, and check grades. For teachers: they login, view statistics, create classes and share codes, create assignments, view submissions, grade work, and export data. For admins: they login, view system statistics, manage users and roles, monitor activity, and configure settings."

### **Strengths (Slide 15)**
"Our project has several key strengths. The modular architecture using Flask Blueprints makes the code maintainable and scalable. We've prioritized security with CSRF protection, password hashing, and role-based access control. The user interface is intuitive with clear navigation. The system addresses real-world educational workflow needs. Our code follows Flask best practices and is well-organized. The database design includes proper relationships and performance indexes. We have comprehensive error handling and secure file uploads."

### **Future Improvements (Slide 16)**
"Looking ahead, there are several enhancements we could implement. Email notifications for assignment reminders and grade updates would improve communication. An in-app messaging system would enable direct teacher-student communication. File preview functionality would allow viewing documents in the browser. Analytics dashboards with charts would provide insights into grade distributions and submission rates. Rubric-based grading would add structure to the grading process. Discussion forums, calendar integration, and mobile apps are also potential future features."

### **Technical Highlights (Slide 17)**
"Some technical implementation highlights: We generate unique class codes using Python's secrets module for cryptographic security. The join link system creates shareable URLs. Our app automatically detects outdated database schemas and recreates tables when needed. Helper functions provide reusable utilities for validation and file handling. File uploads use secure naming with random prefixes and timestamps. We've implemented letter grade conversion from percentages and automatic late submission detection."

### **Conclusion**
"In conclusion, our Assignment Management System provides a comprehensive solution for managing educational assignments. It's secure, user-friendly, and built with modern web technologies. The modular architecture makes it maintainable and scalable for future enhancements. Thank you for your attention, and I'm happy to answer any questions."

---

## 📊 **ADDITIONAL PRESENTATION NOTES**

### **Demo Flow Suggestions**
1. Start with landing page
2. Register as a new student
3. Show student dashboard
4. Switch to teacher account
5. Create a class (show code generation)
6. Create an assignment
7. Switch back to student
8. Join class using code
9. Submit assignment
10. Switch to teacher
11. Grade submission
12. Show admin dashboard

### **Key Points to Emphasize**
- Security features (CSRF, password hashing)
- Unique class code system
- File upload security
- Role-based access control
- Database relationships
- Modular architecture

### **Potential Questions & Answers**
- **Q: How do you ensure security?**  
  A: CSRF tokens on all forms, password hashing with Werkzeug, role-based decorators, secure file uploads with validation.

- **Q: Can the database scale?**  
  A: Yes, we use SQLAlchemy ORM which supports MySQL, PostgreSQL. Currently SQLite for development, but production-ready for larger databases.

- **Q: How do students join classes?**  
  A: Teachers generate unique 6-character codes. Students can enter the code manually or use a shareable link that automatically enrolls them.

- **Q: What file types are supported?**  
  A: PDF, DOC, DOCX, TXT, and ZIP files for assignments and submissions.

---

## 📁 **COMPLETE FOLDER DESCRIPTIONS**

### **Root Directory**
The root directory contains the main application files and configuration:
- **`app.py`**: Main Flask application factory. Creates the Flask app instance, initializes all extensions (database, login manager, CSRF), imports models, handles database setup with automatic schema detection, registers all blueprints, and defines error handlers.
- **`config.py`**: Configuration class that defines database URI, secret key, upload folder paths, CSRF settings, session configuration, and admin whitelist. Uses environment variables for sensitive data.
- **`extensions.py`**: Initializes Flask extensions (SQLAlchemy for database, LoginManager for authentication, CSRFProtect for security) before the app is created. This prevents circular imports.
- **`requirements.txt`**: Lists all Python package dependencies with version numbers for easy installation.
- **`fix_database.py`**: Utility script for database maintenance. Can check database status, recreate database (with confirmation), or migrate schema (add missing columns).
- **`migrate_add_class_code.py`**: Specific migration script to add the `class_code` column to existing databases.

### **`/routes` Directory**
Contains all route handlers organized by functionality:
- **`auth.py`**: Authentication blueprint (`auth_bp`). Handles user registration with validation (email format, password strength, username sanitization), login with session management, logout, and includes security restrictions for admin registration (whitelist system).
- **`student.py`**: Student blueprint (`student_bp`, prefix `/student`). Contains routes for: dashboard with statistics, viewing assignments, assignment details, file downloads, submission creation, viewing grades with letter grade conversion, profile management, class listing, joining classes by code or link, and leaving classes. Includes helper functions for class enrollment checking.
- **`teacher.py`**: Teacher blueprint (`teacher_bp`, prefix `/teacher`). Contains routes for: dashboard with statistics, student listing, class management, assignment creation/editing/deletion, grading submissions, grade export (CSV), student list export, avatar upload, class detail views, assignment detail views, and submission file downloads. Protected with `@teacher_required` decorator.
- **`admin.py`**: Admin blueprint (`admin_bp`, prefix `/admin`). Contains routes for: dashboard with system statistics, user management (CRUD operations), teacher management, student management, assignment management, role management with security checks, profile management, system settings, and activity log viewing. Protected with `@admin_required` decorator.

### **`/models` Directory**
Contains database model definitions:
- **`user.py`**: User model - core authentication entity. Fields: id, username (unique, indexed), email (unique, indexed), password (hashed), role (admin/teacher/student, indexed), status (active/inactive, indexed), created_at, last_login. Relationships: one-to-one with Student and Teacher profiles. Methods: `is_admin()`, `is_teacher()`, `is_student()`.
- **`student.py`**: Student model - student profile. Fields: id, user_id (foreign key, unique), first_name, last_name, major, year, section, created_at. Relationship: belongs to User. Property: `full_name` (combines first and last name).
- **`teacher.py`**: Teacher model - teacher profile. Fields: id, user_id (foreign key, unique), first_name, last_name, department, subject, phone, bio, avatar_path, created_at. Relationship: belongs to User. Property: `full_name`.
- **`class_model.py`**: Class model - class/course entity. Fields: id, name, description, class_code (unique 6-character alphanumeric, indexed), teacher_id (foreign key), created_at. Relationships: belongs to Teacher, many-to-many with Students (via `class_student` table), one-to-many with Assignments. Methods: `generate_class_code()` (static, creates unique codes), `get_join_link()` (generates shareable URL), `get_students()`.
- **`assignment.py`**: Assignment model - assignment entity. Fields: id, title, description, due_date (indexed), status (pending/completed, indexed), file_path, created_at, class_id (foreign key, indexed), teacher_id (foreign key, indexed). Relationships: belongs to Class and Teacher, one-to-many with Submissions. Methods: `is_overdue()`, `get_submissions_count()`, `get_graded_count()`.
- **`submission.py`**: Submission model - student submission entity. Fields: id, assignment_id (foreign key, indexed), student_id (foreign key, indexed), file_path, comments, grade (float, 0-100), feedback (text), submitted_at, graded_at. Relationships: belongs to Assignment and Student. Methods: `is_graded()`, `is_late()`.
- **`models.py`**: Central import file that imports all models. This ensures SQLAlchemy recognizes all models when imported in `app.py`.

### **`/templates` Directory**
Contains HTML templates using Jinja2:
- **`base.html`**: Base template with complete HTML structure, Bootstrap 5 CSS, Font Awesome icons, custom CSS styling, sidebar navigation (role-based menu items), header with user info, flash message display, and footer. All other templates extend this.
- **`home.html`**: Landing page with welcome message, feature highlights, and call-to-action buttons for login/register.
- **`login.html`**: Login form with email and password fields, CSRF token, validation, and links to register.
- **`register.html`**: Registration form with username, email, password, confirm password, role selection (student/teacher/admin with restrictions), CSRF token, and validation.
- **`/student/`**: Student-specific templates:
  - `dashboard.html`: Shows assignment statistics, recent assignments, enrolled classes, recent activity.
  - `assignments.html`: Lists all assignments with filters, due dates, submission status.
  - `classes.html`: Shows enrolled classes with option to join new classes or leave existing ones.
  - `grades.html`: Displays all grades with letter grade conversion, feedback, submission dates.
  - `join_class.html`: Form to enter class code manually.
  - `join_class_confirm.html`: Confirmation page before joining a class via link.
  - `profile.html`: Form to update student profile information.
- **`/teacher/`**: Teacher-specific templates:
  - `dashboard.html`: Statistics cards (total students, classes, pending grading, upcoming deadlines), recent classes, recent assignments, recent students.
  - `classes.html`: List of all classes with student counts, create class form, class code display.
  - `students.html`: List of all students across all classes.
  - `assignment.html`: Form to create/edit assignments.
  - `view_assignment.html`: Assignment details with all submissions, grading interface.
  - `view_class.html`: Class details with enrolled students, assignments in class.
  - `view_student.html`: Individual student profile with submission history.
  - `grades.html`: Grade management interface.
  - `profile.html`: Teacher profile update form with avatar upload.
- **`/admin/`**: Admin-specific templates:
  - `dashboard.html`: System-wide statistics, recent users, recent activities.
  - `manage_users.html`: List of all users with search/filter, create/edit/delete buttons.
  - `manage_user.html`: Individual user detail/edit page.
  - `add_user.html`: Form to create new users.
  - `manage_teachers.html`, `manage_students.html`: Role-specific user lists.
  - `add_teacher.html`, `add_student.html`: Forms to create role-specific users.
  - `manage_roles.html`: Interface to change user roles.
  - `change_role.html`: Form to change a specific user's role.
  - `manage_assignments.html`: List of all assignments system-wide.
  - `manage_assignment.html`: Individual assignment detail page.
  - `activity_log.html`: System activity log viewer.
  - `system_settings.html`: Application configuration interface.
  - `edit_profile.html`: Admin profile update form.
  - `view_user.html`: User detail view for admins.
- **`/errors/`**: Custom error pages:
  - `404.html`: Page not found error.
  - `403.html`: Access forbidden error.
  - `500.html`: Internal server error.

### **`/static` Directory**
Contains static assets:
- **`/css/`**: Stylesheets:
  - `bootstrap.min.css`: Bootstrap 5.3 minified CSS.
  - `bootstrap.css`: Bootstrap 5.3 full CSS (for development).
  - `style.css`: Custom application styles (colors, sidebar, cards, buttons, responsive design).
- **`/js/`**: JavaScript files:
  - `bootstrap.bundle.min.js`: Bootstrap 5.3 JavaScript bundle (includes Popper.js).
  - `main.js`: Custom JavaScript for application-specific functionality.
- **`/uploads/`**: User-uploaded files (created at runtime):
  - `/assignments/`: Assignment files uploaded by teachers, organized by assignment ID.
  - `/submissions/`: Student submission files with secure naming.
  - `/avatars/`: User profile pictures.
  - `/images/`: Static images like login/signup illustrations.

### **`/utils` Directory**
Contains utility functions:
- **`helpers.py`**: Helper functions used throughout the application:
  - `validate_email()`: Validates email format using regex.
  - `validate_password()`: Checks password strength (min 8 chars, letter, number).
  - `sanitize_username()`: Removes special characters, keeps alphanumeric and dots/underscores.
  - `get_user_display_name()`: Extracts first_name, last_name, full_name from user object (handles all user types).
  - `generate_secure_filename()`: Creates secure filenames with random prefix and timestamp.
  - `validate_file_extension()`: Checks if file extension is in allowed list.
  - `validate_file_mime_type()`: Validates file MIME type.
  - `format_datetime()`: Formats datetime objects to readable strings.

### **`/tests` Directory**
Contains unit tests:
- **`test_auth.py`**: Tests for authentication functionality (registration, login).
- **`test_login.py`**: Tests for login process and session management.

### **`/instance` Directory**
Created at runtime, contains:
- **`database.db`**: SQLite database file (created automatically on first run).

### **`/logs` Directory**
Created at runtime, contains:
- **`app.log`**: Application log file with rotation (max 10 backup files, 10KB each).

---

## 🎯 **QUICK REFERENCE: Key Features by Role**

### **Student**
- Join classes via code or link
- View assignments with due dates
- Submit files (PDF, DOC, DOCX, TXT, ZIP)
- View grades and feedback
- Track submission history
- Update profile

### **Teacher**
- Create classes with unique codes
- Share class codes/links
- Create assignments with files
- View all submissions
- Grade with feedback
- Export grades/student lists
- Manage class roster

### **Admin**
- Manage all users
- Change user roles
- View system statistics
- Monitor activity logs
- Configure system settings
- Manage assignments system-wide

---

**End of Presentation Content**

