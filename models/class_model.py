# models/class_model.py
from extensions import db
from datetime import datetime
import secrets
import string

class_student = db.Table(
    'class_student',
    db.Column('class_id', db.Integer, db.ForeignKey('classes.id', ondelete='CASCADE')),
    db.Column('student_id', db.Integer, db.ForeignKey('students.id', ondelete='CASCADE'))
)


class Class(db.Model):
    __tablename__ = 'classes'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    class_code = db.Column(db.String(6), unique=True, nullable=False, index=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id', ondelete='SET NULL'), index=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    teacher = db.relationship('Teacher', backref='classes')
    students = db.relationship('Student', secondary=class_student, backref='classes', lazy='dynamic')
    assignments = db.relationship('Assignment', backref='class_obj', lazy='dynamic', cascade='all, delete-orphan')
    
    @staticmethod
    def generate_class_code():
        """Generate a unique 6-character alphanumeric class code"""
        while True:
            code = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(6))
            # Check if code already exists
            existing = db.session.query(Class).filter_by(class_code=code).first()
            if not existing:
                return code
    
    def __init__(self, **kwargs):
        super(Class, self).__init__(**kwargs)
        if not self.class_code:
            self.class_code = Class.generate_class_code()
    
    def get_join_link(self, base_url=''):
        """Generate a shareable join link for this class"""
        if base_url:
            return f"{base_url}/student/join/{self.class_code}"
        return f"/student/join/{self.class_code}"
    
    def get_students(self):
        """Get all students in this class"""
        return self.students.all()
    
    def __repr__(self):
        return f"<Class {self.name} ({self.class_code})>"
