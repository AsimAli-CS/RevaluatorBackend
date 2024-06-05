import re
import spacy
import random
from pdfminer.high_level import extract_text
from spacy.matcher import Matcher
from .skills import skills_list

nlp = spacy.load('en_core_web_sm')


def extract_text_from_pdf(pdf_file):
    return extract_text(pdf_file)

def extract_contact_number_from_resume(text):
    pattern = r"\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b"
    match = re.search(pattern, text)
    return match.group() if match else None

def extract_email_from_resume(text):
    pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
    match = re.search(pattern, text)
    return match.group() if match else None

def extract_skills_from_resume(text, skills_list):
    skills = [skill for skill in skills_list if re.search(rf"\b{re.escape(skill)}\b", text, re.IGNORECASE)]
    skills_string = ', '.join(skills)  # Join the skills list into a string
    return skills_string

def extract_education_from_resume(text):
    pattern = r"(?i)(?:Bsc|BS|BSc|B\.S\.|B\.Sc|M\.S\.|M\.Sc|\bB\.\w+|\bM\.\w+|\bPh\.D\.\w+|\bBachelor(?:'s)?|\bMaster(?:'s)?|\bPh\.D)\s(?:\w+\s)*\w+"
    return re.findall(pattern, text)

def extract_name(resume_text):
    matcher = Matcher(nlp.vocab)
    patterns = [
        [{'POS': 'PROPN'}, {'POS': 'PROPN'}],
        [{'POS': 'PROPN'}, {'POS': 'PROPN'}, {'POS': 'PROPN'}],
        [{'POS': 'PROPN'}, {'POS': 'PROPN'}, {'POS': 'PROPN'}, {'POS': 'PROPN'}]
    ]
    for pattern in patterns:
        matcher.add('NAME', [pattern])
    doc = nlp(resume_text)
    matches = matcher(doc)
    for match_id, start, end in matches:
        span = doc[start:end]
        return span.text
    return None

def extract_details_from_pdf(pdf_file_path, pdf_file):
    text = extract_text_from_pdf(pdf_file_path)
    details = {
        "name": extract_name(text) or "N/A",
        "phone_no": extract_contact_number_from_resume(text) or "N/A",
        "email": extract_email_from_resume(text) or "N/A",
        "skills": extract_skills_from_resume(text, skills_list) or "N/A",
        "education": extract_education_from_resume(text) or "N/A",
        "cvScore": round(random.uniform(50, 100)), 
        "cvTitle": pdf_file.name 
    }
    return details
