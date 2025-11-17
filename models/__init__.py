from .user import User
from .student import Student
from .teacher import Teacher
from .assignment import Assignment
from .class_model import Class
from .submission import Submission

# Import db from extensions instead of creating a new instance
from extensions import db

__all__ = ['User', 'Student', 'Teacher', 'Assignment', 'Class', 'Submission', 'db']
