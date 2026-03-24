import re
import math
import random
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
import PyPDF2
import requests
from bs4 import BeautifulSoup
from PIL import Image
import pytesseract
import io

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
    resume: UploadFile = File(...),
    job_description: str = Form(None),
    job_image: UploadFile = File(None)
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
    
    final_job_description = ""
    
    if job_description:
        if job_description.startswith("http://") or job_description.startswith("https://"):
            try:
                # Add headers to avoid some basic bot blocks
                headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
                response = requests.get(job_description, headers=headers, timeout=10)
                response.raise_for_status()
                soup = BeautifulSoup(response.content, "html.parser")
                # Remove script and style elements
                for script in soup(["script", "style"]):
                    script.decompose()
                final_job_description = soup.get_text(separator=' ', strip=True)
            except Exception as e:
                return {"error": f"Failed to fetch job description from URL: {str(e)}"}
        else:
            final_job_description = job_description
            
    if job_image:
        try:
            image_bytes = await job_image.read()
            image = Image.open(io.BytesIO(image_bytes))
            
            # Optimization: Resize if too large and convert to grayscale
            max_size = (1500, 1500)
            image.thumbnail(max_size, Image.Resampling.LANCZOS)
            image = image.convert('L') # Grayscale
            
            extracted_text = pytesseract.image_to_string(image)
            final_job_description += " " + extracted_text
        except Exception as e:
            return {"error": f"Failed to process job description image: {str(e)}"}
            
    if not final_job_description.strip():
        return {"error": "Please provide either a job description text, a valid URL, or an image."}

    job_skills = extract_skills(final_job_description)

    if not job_skills:
        return {"error": "Could not extract any technical skills from the job description. If you provided a URL, the site might be blocking bots. Please copy and paste the text directly."}

    matched_skills = list(job_skills.intersection(resume_skills))
    missing_skills = list(job_skills.difference(resume_skills))
    
    total_needed = len(job_skills)
    skill_match = int((len(matched_skills) / total_needed) * 100) if total_needed > 0 else 0

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
    text_lower_no_space = text_lower.replace(" ", "")
    has_phd = "phd" in text_lower or "doctorate" in text_lower
    has_master = "master" in text_lower or "m.s." in text_lower or "msc" in text_lower
    has_bachelor = "bachelor" in text_lower or "b.s." in text_lower or "bsc" in text_lower or "university" in text_lower or "college" in text_lower
    
    if has_phd:
        education_score = 100
    elif has_master:
        education_score = 90
    elif has_bachelor:
        education_score = 80
    else:
        education_score = 50

    # 4. Experience Score
    years_mentions = len(re.findall(r'\d+\s+years?', text_lower))
    experience_score = min(100, skill_match + (years_mentions * 10))

    # 5. Core Scores
    overall_match = int((skill_match * 0.5) + (experience_score * 0.3) + (education_score * 0.2))
    ats_score = int(overall_match * 0.9) if length_status != "Optimal" else min(100, overall_match + 5)
    industry_readiness = skill_match
    interview_readiness = max(0, overall_match - (len(missing_skills) * 2))

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
        
    conclusion_parts = []
    
    if overall_match >= 80:
        conclusion_parts.append("✅ Strong Match. Your resume looks great for this role.")
    elif overall_match >= 50:
        conclusion_parts.append("⚠️ Average Match. You meet some requirements but need updates to stand out.")
    else:
        conclusion_parts.append("❌ Weak Match. Your resume needs major updates to fit this job.")

    if missing_skills:
        missing_str = ", ".join([s.title() for s in missing_skills[:3]])
        conclusion_parts.append(f"What to ADD: You are missing important skills like {missing_str}.")
    else:
        conclusion_parts.append("What to ADD: Your core skills match! Just ensure your experience clearly proves them.")

    if found_weak_verbs:
        verbs_str = ", ".join(found_weak_verbs)
        conclusion_parts.append(f"What to AVOID: Remove weak words like '{verbs_str}' and use strong action verbs (e.g., 'Engineered', 'Directed').")
    elif length_status == "Too Short":
        conclusion_parts.append("What to AVOID: Avoid being too brief. Expand your bullet points with details.")
    elif length_status == "Too Long":
        conclusion_parts.append("What to AVOID: Avoid lengthy descriptions. Keep it concise to one or two pages.")
    else:
        conclusion_parts.append("What to AVOID: Try not to add unnecessary fluff. Keep your descriptions impactful.")

    conclusion = " ".join(conclusion_parts)

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
