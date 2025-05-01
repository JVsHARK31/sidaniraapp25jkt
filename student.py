from src.extensions import db # Import db from extensions
from sqlalchemy import JSON # Import generic JSON type

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # Assuming 'Unnamed: 1' is the student ID (NISN or similar)
    student_id = db.Column(db.String(50), unique=True, nullable=False)
    # Assuming 'Unnamed: 2' is the student name
    name = db.Column(db.String(150), nullable=False)
    # Store the rest of the scores/data from the Excel row as JSON
    # This avoids creating ~70 individual columns
    scores_data = db.Column(JSON)
    # Add a column to track the academic year or semester if needed for future use
    academic_year = db.Column(db.String(20), nullable=True, default='2024/2025') # Example default

    def __repr__(self):
        return f'<Student {self.student_id} - {self.name}>'

