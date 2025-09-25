# backend/api.py
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from models import db, Candidate, Resume, Job
import io
from fpdf import FPDF
from docx import Document

# --- Pre-load all AI models and analysis functions ---
from jd_matcher import match_resume_to_jd
from keyword_analyzer import missing_keywords
from score_generator import generate_score
from ai_suggester import get_resume_suggestions
from resume_rewriter import rewrite_resume

# --- App Configuration ---
app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///resumes.db'
db.init_app(app)

# --- API Endpoints ---
@app.route('/analyze', methods=['POST'])
def analyze_resume_endpoint():
    data = request.get_json()
    resume_id = data.get('resume_id')
    job_id = data.get('job_id')

    # 1. Fetch data from the database
    with app.app_context():
        # Using the newer Session.get() method to avoid warnings
        resume_obj = db.session.get(Resume, resume_id)
        job_obj = db.session.get(Job, job_id)

    if not resume_obj or not job_obj:
        return jsonify({"error": "Resume or Job not found in the database."}), 404
        
    resume_text = resume_obj.full_text
    jd_text = job_obj.description
    
    # 2. Run your analysis functions
    print("Backend: Starting analysis...")
    similarity_score = match_resume_to_jd(resume_text, jd_text)
    missing = missing_keywords(resume_text, jd_text)
    final_score = generate_score(similarity_score, missing)
    suggestions = get_resume_suggestions(resume_text, jd_text)
    summary = rewrite_resume(resume_text, jd_text)
    print("Backend: Analysis complete.")

    # 3. Structure and return the final JSON output
    analysis_result = {
        "jobId": job_id,
        "candidateId": resume_obj.candidate_id,
        "jobFitAnalysis": {
            "matchScore": final_score,
            "semanticSimilarity": similarity_score,
            "missingKeywords": missing,
            "recruiterSummary": summary,
            "resumeImprovements": {
                "actionableAdvice": suggestions
            }
        },
    }
    
    return jsonify(analysis_result)

# --- Download Endpoints ---
@app.route('/download/txt', methods=['POST'])
def download_txt():
    data = request.get_json()
    resume_text = data.get('text', '')
    buffer = io.BytesIO(resume_text.encode('utf-8'))
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name='Optimized_Resume.txt', mimetype='text/plain')

@app.route('/download/pdf', methods=['POST'])
def download_pdf():
    data = request.get_json()
    resume_text = data.get('text', '')
    
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=11)
    pdf.multi_cell(0, 5, resume_text.encode('latin-1', 'replace').decode('latin-1'))
    
    buffer = io.BytesIO(pdf.output(dest='S').encode('latin-1'))
    return send_file(buffer, as_attachment=True, download_name='Optimized_Resume.pdf', mimetype='application/pdf')

@app.route('/download/docx', methods=['POST'])
def download_docx():
    data = request.get_json()
    resume_text = data.get('text', '')
    
    doc = Document()
    doc.add_paragraph(resume_text)
    
    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name='Optimized_Resume.docx', mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)