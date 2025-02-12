from flask import Flask, request, jsonify, render_template
import pdfplumber
import docx

app = Flask(__name__)

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

    result = analyze_resume(text)
    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True)
