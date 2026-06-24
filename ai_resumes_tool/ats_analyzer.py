import re
from collections import Counter

def calculate_ats_score(resume, job_description):
    """
    Calculate ATS score (0-100) based on resume compatibility with job description.
    Returns score and detailed feedback.
    """
    
    score = 0
    feedback = []
    
    # 1. Keyword matching (35 points max)
    keyword_score = analyze_keywords(resume, job_description)
    score += keyword_score
    if keyword_score < 25:
        feedback.append("❌ Low keyword match - Add more job-specific keywords from the job description")
    elif keyword_score < 30:
        feedback.append("⚠️ Moderate keyword match - Include more technical terms and skills mentioned in the job")
    else:
        feedback.append("✅ Good keyword alignment with job description")
    
    # 2. Formatting quality (25 points max)
    format_score = analyze_formatting(resume)
    score += format_score
    if format_score < 15:
        feedback.append("❌ Poor formatting - Avoid tables, images, and complex formatting")
    elif format_score < 20:
        feedback.append("⚠️ Formatting could be cleaner - Use simple bullet points and standard fonts")
    else:
        feedback.append("✅ Clean, ATS-friendly formatting")
    
    # 3. Content structure (20 points max)
    structure_score = analyze_structure(resume)
    score += structure_score
    if structure_score < 12:
        feedback.append("❌ Weak structure - Add clear section headers (Experience, Skills, Education)")
    elif structure_score < 16:
        feedback.append("⚠️ Structure needs improvement - Make sections more distinct")
    else:
        feedback.append("✅ Well-organized structure")
    
    # 4. Keyword density (15 points max)
    density_score = analyze_keyword_density(resume, job_description)
    score += density_score
    if density_score < 8:
        feedback.append("❌ Low keyword density - Incorporate more relevant terms throughout")
    elif density_score < 12:
        feedback.append("⚠️ Keyword density is moderate - Add more industry-specific terms")
    else:
        feedback.append("✅ Good keyword density")
    
    # 5. Length and completeness (5 points max)
    length_score = analyze_length(resume)
    score += length_score
    if len(resume.strip()) < 200:
        feedback.append("❌ Resume too short - ATS systems need substantial content")
    
    # Extract key missing keywords
    missing_keywords = extract_missing_keywords(resume, job_description)
    
    return {
        "score": min(100, score),
        "keyword_score": keyword_score,
        "format_score": format_score,
        "structure_score": structure_score,
        "density_score": density_score,
        "length_score": length_score,
        "feedback": feedback,
        "missing_keywords": missing_keywords[:5]  # Top 5 missing keywords
    }

def analyze_keywords(resume, job_description):
    """Extract and match keywords between resume and job description."""
    resume_lower = resume.lower()
    job_lower = job_description.lower()
    
    # Extract important keywords from job description
    job_keywords = extract_technical_terms(job_lower)
    
    matched_keywords = sum(1 for keyword in job_keywords if keyword in resume_lower)
    
    # Score based on match percentage
    if len(job_keywords) == 0:
        return 25
    
    match_percentage = (matched_keywords / len(job_keywords)) * 100
    return min(35, int((match_percentage / 100) * 35))

def analyze_formatting(resume):
    """Check for ATS-unfriendly formatting."""
    score = 25
    
    # Check for problematic characters
    problematic_chars = ['•', '◆', '►', '■', '√', '©', '®', '™', '[', ']', '{', '}']
    for char in problematic_chars:
        if char in resume:
            score -= 2
    
    # Check for tables (common ATS issue)
    if '|' in resume or '\t' in resume:
        score -= 5
    
    # Check for multiple spaces or strange formatting
    if '  ' in resume:  # Multiple spaces
        score -= 2
    
    return max(0, score)

def analyze_structure(resume):
    """Check for proper resume structure and sections."""
    score = 0
    resume_lower = resume.lower()
    
    # Check for common section headers
    required_sections = ['experience', 'skills', 'education']
    found_sections = sum(1 for section in required_sections if section in resume_lower)
    
    score = int((found_sections / len(required_sections)) * 20)
    
    # Bonus for summary section
    if 'summary' in resume_lower or 'objective' in resume_lower:
        score += 2
    
    return min(20, score)

def analyze_keyword_density(resume, job_description):
    """Analyze how well keywords are distributed."""
    resume_words = resume.lower().split()
    job_keywords = extract_technical_terms(job_description.lower())
    
    if not job_keywords or not resume_words:
        return 15
    
    keyword_count = sum(1 for keyword in job_keywords if keyword in resume_words)
    density = (keyword_count / len(job_keywords)) * 100
    
    return min(15, int((density / 100) * 15))

def analyze_length(resume):
    """Check if resume has adequate content length."""
    word_count = len(resume.split())
    
    # Ideal resume is 200-600 words
    if word_count < 200:
        return 0
    elif word_count < 400:
        return 3
    elif word_count < 800:
        return 5
    else:
        return 5  # Cap at 5 for very long resumes

def extract_technical_terms(text):
    """Extract technical terms and important keywords from text."""
    # Common technical keywords to look for
    tech_keywords = {
        'python', 'java', 'javascript', 'typescript', 'sql', 'kotlin',
        'react', 'angular', 'vue', 'django', 'flask', 'spring',
        'aws', 'gcp', 'azure', 'docker', 'kubernetes', 'git',
        'agile', 'scrum', 'jira', 'ci/cd', 'api', 'rest',
        'machine learning', 'data science', 'ai', 'llm', 'rag',
        'playwright', 'selenium', 'testing', 'automation', 'qa',
        'leadership', 'communication', 'project management',
        'problem solving', 'team collaboration'
    }
    
    text_lower = text.lower()
    found_keywords = [kw for kw in tech_keywords if kw in text_lower]
    
    # Also extract capitalized words (likely titles/skills)
    capitalized_words = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)
    capitalized_lower = [w.lower() for w in set(capitalized_words) if len(w) > 3]
    
    return list(set(found_keywords + capitalized_lower))

def extract_missing_keywords(resume, job_description):
    """Find important keywords from job description that are missing in resume."""
    resume_lower = resume.lower()
    job_keywords = extract_technical_terms(job_description.lower())
    
    missing = [kw for kw in job_keywords if kw not in resume_lower]
    return missing

def get_ats_improvement_tips():
    """Return general ATS improvement tips."""
    return [
        "✅ Use standard fonts (Arial, Calibri, Times New Roman)",
        "✅ Stick to one column layout",
        "✅ Use standard section headers: EXPERIENCE, SKILLS, EDUCATION",
        "✅ Use bullet points (•) instead of dashes or special characters",
        "✅ Save as PDF or .docx (not images)",
        "✅ Include relevant keywords from the job description",
        "✅ Use consistent formatting throughout",
        "✅ Keep margins between 0.5 and 1 inch",
        "✅ Use standard bullet points and numbering",
        "✅ Avoid tables, text boxes, and graphics"
    ]
