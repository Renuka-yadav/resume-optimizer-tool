# backend/seed_db.py
from api import app, db
from models import Candidate, Resume, Job
from resume_parser import extract_resume_text
import os

def seed_data():
    print("Seeding database...")
    
    # --- Add a Candidate and Resume ---
    # Use a basic try-except block to prevent errors if the user already exists
    try:
        candidate1 = Candidate(name='Renuka Yadav', email='renuka121yadav@gmail.com', phone='+91 9691397751')
        db.session.add(candidate1)
        db.session.commit()
    except Exception as e:
        print("Candidate already exists or another DB error occurred:", e)
        db.session.rollback() # Rollback the session in case of error
        candidate1 = Candidate.query.filter_by(email='renuka121yadav@gmail.com').first()


    # Make sure the path to the resume is correct relative to the 'backend' folder
    resume_path = os.path.join(os.path.dirname(__file__), '..', 'resumes', 'Renuka_Yadav_Data_Analyst_Resume.pdf')
    resume_text = extract_resume_text(resume_path)
    
    # Check if a resume for this candidate already exists to avoid duplicates
    existing_resume = Resume.query.filter_by(candidate_id=candidate1.id, full_text=resume_text).first()
    if not existing_resume:
        new_resume = Resume(candidate_id=candidate1.id, full_text=resume_text)
        db.session.add(new_resume)

    # --- Add a Job Description ---
    job_description_text = """
    **Data Analyst Position**
    We are seeking a detail-oriented Data Analyst to join our growing team. The ideal candidate will be responsible for cleaning, analyzing, and visualizing large datasets to provide actionable insights.
    """
    
    # Check if the job already exists
    existing_job = Job.query.filter_by(title='Data Analyst').first()
    if not existing_job:
        new_job = Job(title='Data Analyst', description=job_description_text)
        db.session.add(new_job)

    db.session.commit()
    print("Database has been seeded successfully.")

if __name__ == '__main__':
    with app.app_context():
        # This will create tables if they don't exist
        db.create_all()
        seed_data()