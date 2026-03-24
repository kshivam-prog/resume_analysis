import re
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
import PyPDF2

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

KNOWN_SKILLS = {
    "python", "django", "sql", "html", "css", "javascript", "react", "node", 
    "docker", "aws", "cloud", "java", "c++", "c", "c#", "ruby", "php", "go",
    "kubernetes", "linux", "git", "machine learning", "mongodb", "postgresql",
    "mysql", "sqlite", "fastapi", "flask", "spring", "angular", "vue",
    "system design", "data structures", "algorithms", "typescript",
    "tailwind", "bootstrap", "firebase", "gcp", "azure", "ci/cd",
    "agile", "scrum", "jira", "numpy", "pandas", "scikit-learn",
    "tensorflow", "pytorch", "deep learning", "nlp", "computer vision"
}

def extract_skills(text):
    text = text.lower()
    found_skills = set()
    for skill in KNOWN_SKILLS:
        if re.search(r'\b' + re.escape(skill) + r'\b', text):
            found_skills.add(skill)
    return found_skills

def generate_feedback(match_percentage, matched_skills, missing_skills):
    pros = []
    improvements = []
    
    if len(matched_skills) > 0:
        pros.append(f"Strong foundation with {len(matched_skills)} matching key skills including {', '.join([s.title() for s in list(matched_skills)[:3]])}.")
    if match_percentage >= 80:
        pros.append("Excellent overall match for the core technical requirements of this role.")
    elif match_percentage >= 50:
        pros.append("Solid baseline of skills that align with the job description.")
        
    if len(missing_skills) > 0:
        improvements.append(f"Consider familiarizing yourself with: {', '.join([s.title() for s in list(missing_skills)[:3]])}.")
    if match_percentage < 50:
        improvements.append("The resume is currently missing several core technologies mentioned in the job description. Try to add personal projects covering these areas.")
    elif match_percentage < 80:
        improvements.append("You have a good base, but highlighting a few more of the missing skills could push your resume to the top.")
        
    conclusion = ""
    if match_percentage >= 80:
        conclusion = "Your resume is highly competitive for this position! Focus on tailoring your experience bullet points to highlight the matched skills even further before applying."
    elif match_percentage >= 40:
        conclusion = "You have a fair chance, but bridging the skill gap will significantly increase your callback rate. Focus on learning the missing technologies and updating your resume."
    else:
        conclusion = "Your current resume shows a significant skill gap for this specific role. You may want to look for more closely aligned positions or dedicate time to upskilling in the missing areas."
        
    return pros, improvements, conclusion

@app.post("/analyze")
async def analyze_resume(
    job_description: str = Form(...),
    resume: UploadFile = File(...)
):
    text = ""
    try:
        reader = PyPDF2.PdfReader(resume.file)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + " "
    except Exception as e:
        return {"error": str(e)}

    resume_skills = extract_skills(text)
    job_skills = extract_skills(job_description)

    matched_skills = list(job_skills.intersection(resume_skills))
    missing_skills = list(job_skills.difference(resume_skills))
    
    total_needed = len(job_skills)
    # If no recognized skills in job desc, assume 100% just so it doesn't break, or 0 if it's completely empty
    match_percentage = int((len(matched_skills) / total_needed) * 100) if total_needed > 0 else 0
    if total_needed == 0 and len(resume_skills) > 0:
        match_percentage = 100 # They have skills, job desc had none known

    pros, improvements, conclusion = generate_feedback(match_percentage, matched_skills, missing_skills)

    return {
        "match_percentage": match_percentage,
        "matched_skills": [s.title() for s in matched_skills],
        "missing_skills": [s.title() for s in missing_skills],
        "pros": pros,
        "improvements": improvements,
        "conclusion": conclusion
    }
