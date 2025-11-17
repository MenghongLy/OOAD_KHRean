from extensions import db
from datetime import datetime


class Submission(db.Model):
    __tablename__ = 'submissions'

    id = db.Column(db.Integer, primary_key=True)
    assignment_id = db.Column(db.Integer, db.ForeignKey('assignments.id', ondelete='CASCADE'), nullable=False, index=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id', ondelete='CASCADE'), nullable=False, index=True)
    
    file_path = db.Column(db.String(200))  # path to submitted file
    comments = db.Column(db.Text)
    grade = db.Column(db.Float)  # Grade out of 100
    feedback = db.Column(db.Text)  # Teacher feedback
    submitted_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    graded_at = db.Column(db.DateTime)
    
    # Relationships
    student = db.relationship('Student', backref='submissions')
    
    def __repr__(self):
        return f"<Submission {self.id} by Student {self.student_id} for Assignment {self.assignment_id}>"
    
    def is_graded(self):
        """Check if submission has been graded"""
        return self.grade is not None
    
    def is_late(self):
        """Check if submission was submitted after due date"""
        if self.assignment and self.submitted_at and self.assignment.due_date:
            return self.submitted_at > self.assignment.due_date
        return False

