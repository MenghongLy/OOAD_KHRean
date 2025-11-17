from extensions import db
from flask_login import UserMixin


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False,
                     default='student', index=True)  # admin | teacher | student
    status = db.Column(db.String(20), nullable=False, default='active', index=True)
    created_at = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())
    last_login = db.Column(db.DateTime, nullable=True)

    student_profile = db.relationship('Student', backref='user', uselist=False, cascade='all, delete-orphan')
    teacher_profile = db.relationship('Teacher', backref='user', uselist=False, cascade='all, delete-orphan')

    def __repr__(self):
        return f"<User {self.username} ({self.role})>"
    
    def is_admin(self):
        """Check if user is an admin"""
        return self.role == 'admin'
    
    def is_teacher(self):
        """Check if user is a teacher"""
        return self.role == 'teacher'
    
    def is_student(self):
        """Check if user is a student"""
        return self.role == 'student'
