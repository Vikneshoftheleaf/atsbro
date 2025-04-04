from flask import Flask, request, jsonify, render_template
import pdfplumber
import docx
from google import genai
from google.genai import types
import requests
import mimetypes
import os
client = genai.Client(api_key="AIzaSyCIYdBLuJe97rNB3gtcsI4RHGUumiioD8Y")

app = Flask(__name__)

MODEL_ID = "gemini-2.0-flash-exp"
# Define ATS-friendly keywords
ATS_KEYWORDS = ["Python", "Flask", "Machine Learning", "JavaScript", "React", "SQL", "API", "Software Engineer"]

def extract_text_from_pdf(pdf_file):
    """Extracts text from a PDF file."""
    text = ""
    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + " "
    return text.strip()

def extract_text_from_docx(docx_file):
    """Extracts text from a Word document."""
    doc = docx.Document(docx_file)
    return " ".join([para.text for para in doc.paragraphs])

def analyze_resume(text):
    """Analyzes the resume text for keyword matching."""
    found_keywords = [word for word in ATS_KEYWORDS if word.lower() in text.lower()]
    score = (len(found_keywords) / len(ATS_KEYWORDS)) * 100  # Percentage match
    return {"score": round(score, 2), "keywords_found": found_keywords}


def ai_report(txt_data):

    contents = f'Analyze the following resume for ATS compatibility and job relevance, and return a JSON report with: "ats_score" (0-100), "keyword_analysis" ("matched_keywords[array]"), "structure_formatting" ("sections_present", "format_issues", "bullet_points_used"), "work_experience" ("jobs_listed", "experience_quality", "quantified_achievements", "missing_details"), "skills_assessment" ("hard_skills", "soft_skills", "relevance"), "grammar_readability" ("spelling_errors", "clarity_score", "passive_voice_usage"), "recommendations" (list of improvements), and "projected_score" (estimated score after fixes); ensure output is valid JSON. Resume: {txt_data}, the result should only contain json structure, no additional text'
    response = client.models.generate_content(
        model=MODEL_ID,
        contents=contents,
        config=types.GenerateContentConfig(
            response_modalities=['Text']
        )
    )
    
    return response

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload_file():
    if "resume" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["resume"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    text = ""
    if file.filename.endswith(".pdf"):
        text = extract_text_from_pdf(file)
    elif file.filename.endswith(".docx"):
        text = extract_text_from_docx(file)
    else:
        return jsonify({"error": "Invalid file format. Only PDF and DOCX allowed."}), 400

    result = ai_report(text)
    return jsonify(result.text)

if __name__ == "__main__":
    app.run(debug=True)
