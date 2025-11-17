from extensions import db
from datetime import datetime


class Student(db.Model):
    __tablename__ = 'students'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(
        'users.id', ondelete='CASCADE'), nullable=False, unique=True, index=True)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    major = db.Column(db.String(100))
    year = db.Column(db.String(10))
    section = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, nullable=False,
                           default=datetime.utcnow)

    def __repr__(self):
        return f"<Student {self.user.username if self.user else 'Unknown'}>"

    @property
    def full_name(self):
        """Get full name of student"""
        if self.first_name or self.last_name:
            return f"{self.first_name or ''} {self.last_name or ''}".strip()
        return self.user.username if self.user else 'Unknown'
