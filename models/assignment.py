from extensions import db
from datetime import datetime


class Assignment(db.Model):
    __tablename__ = 'assignments'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    due_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
    status = db.Column(db.String(20), default='pending', index=True)
    file_path = db.Column(db.String(200))  # path to uploaded assignment file
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # Assignment belongs to a class, not individual students
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id', ondelete='CASCADE'), nullable=False, index=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id', ondelete='SET NULL'), index=True)
    
    # Relationships
    teacher = db.relationship('Teacher', backref='assignments')
    submissions = db.relationship('Submission', backref='assignment', lazy='dynamic', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<Assignment {self.title}>"
    
    def is_overdue(self):
        """Check if assignment is past due date"""
        return datetime.utcnow() > self.due_date
    
    def get_submissions_count(self):
        """Get total number of submissions"""
        return self.submissions.count()
    
    def get_graded_count(self):
        """Get number of graded submissions"""
        try:
            # Filter for non-None grades - use direct iteration since we have dynamic relationship
            return sum(1 for sub in self.submissions.all() if sub.grade is not None)
        except (AttributeError, TypeError):
            return 0
