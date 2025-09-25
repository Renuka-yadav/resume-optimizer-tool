import re

def extract_keywords(text):
    return list(set(re.findall(r'\b\w{4,}\b', text.lower())))

def missing_keywords(resume, jd):
    resume_words = extract_keywords(resume)
    jd_words = extract_keywords(jd)
    return list(set(jd_words) - set(resume_words))
