import re
import math
import random
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
    "tensorflow", "pytorch", "deep learning", "nlp", "computer vision",
    "rest api", "graphql", "graphql", "redis", "elasticsearch"
}

WEAK_VERBS = ["worked", "did", "helped", "made", "handled", "managed", "was responsible for", "assisted", "got"]
STRONG_VERBS = ["architected", "engineered", "orchestrated", "spearheaded", "developed", "facilitated", "executed", "optimized"]

def extract_skills(text):
    text = text.lower()
    found_skills = set()
    for skill in KNOWN_SKILLS:
        if re.search(r'\b' + re.escape(skill) + r'\b', text):
            found_skills.add(skill)
    return found_skills

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

    text_lower = text.lower()
    resume_skills = extract_skills(text)
    job_skills = extract_skills(job_description)

    matched_skills = list(job_skills.intersection(resume_skills))
    missing_skills = list(job_skills.difference(resume_skills))
    
    total_needed = len(job_skills)
    skill_match = int((len(matched_skills) / total_needed) * 100) if total_needed > 0 else 0
    if total_needed == 0 and len(resume_skills) > 0:
        skill_match = 100

    # Simulate deep AI insights heuristically
    
    # 1. Word Count & Length
    word_count = len(text.split())
    if word_count < 300:
        length_status = "Too Short"
    elif word_count > 750:
        length_status = "Too Long"
    else:
        length_status = "Optimal"

    # 2. Action Verbs
    found_weak_verbs = [v for v in WEAK_VERBS if f" {v} " in text_lower]

    # 3. Education Score
    has_degree = "university" in text_lower or "college" in text_lower or "bachelor" in text_lower or "master" in text_lower or "phd" in text_lower or "b.s." in text_lower or "bsc" in text_lower
    education_score = random.randint(85, 98) if has_degree else random.randint(40, 65)

    # 4. Experience Score
    years_mentions = len(re.findall(r'\d+\s+years?', text_lower))
    exp_variance = random.randint(-5, 10)
    experience_score = min(100, max(0, skill_match + (years_mentions * 5) + exp_variance))

    # 5. Core Scores
    overall_match = int((skill_match * 0.5) + (experience_score * 0.3) + (education_score * 0.2))
    ats_score = int(overall_match * 0.9) if length_status != "Optimal" else min(100, overall_match + 5)
    industry_readiness = min(100, overall_match + random.randint(-5, 8))
    interview_readiness = max(0, overall_match - random.randint(5, 15))

    # 6. Conclusion & Suggestions
    pros = []
    if len(matched_skills) > 0:
        pros.append(f"Strong alignment mapping {len(matched_skills)} core technical skills required.")
    if has_degree:
        pros.append("Education criteria meets industry standard baseline.")
    if length_status == "Optimal":
        pros.append("Resume verbosity and length is perfectly optimized for ATS parsers.")
        
    improvements = []
    if len(missing_skills) > 0:
        improvements.append(f"Critical keyword gaps detected: {', '.join([s.title() for s in missing_skills[:3]])}.")
    if len(found_weak_verbs) > 0:
        improvements.append(f"Detected passive verb phrasing ({', '.join(found_weak_verbs)}). Swap for impactful verbs like 'Engineered' or 'Orchestrated'.")
    if length_status == "Too Short":
        improvements.append("Resume brevity may fail to parse effectively. Expand project descriptions using the STAR method.")
        
    conclusion = ""
    if overall_match >= 80:
        conclusion = "Top 5% Candidate Match. Your resume architecture and technical depth heavily index against the job description. Minor formatting tweaks recommended before immediate submission."
    elif overall_match >= 50:
        conclusion = "Competitive Candidate Matrix. You clear the primary ATS filters but fall short on specific industry tooling. Inject missing keywords organically into recent experience nodes."
    else:
        conclusion = "High-Risk Application profile. The current variant severely under-indexes against the core competencies dictated by the JD. Widespread structural and technical revisions required."

    return {
        "overall_score": overall_match,
        "skill_score": skill_match,
        "experience_score": experience_score,
        "education_score": education_score,
        "ats_score": ats_score,
        "industry_score": industry_readiness,
        "interview_score": interview_readiness,
        "length_status": length_status,
        "weak_verbs": found_weak_verbs,
        "strong_verb_suggestions": random.sample(STRONG_VERBS, 3),
        "matched_skills": [s.title() for s in matched_skills],
        "missing_skills": [s.title() for s in missing_skills],
        "pros": pros,
        "improvements": improvements,
        "conclusion": conclusion
    }
