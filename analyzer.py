from pathlib import Path
import re
import json

try:
    import pytesseract
    from PIL import Image
except Exception:
    pytesseract = None

try:
    import fitz
except Exception:
    fitz = None

DATE_PATTERNS = [
    r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',
    r'\b\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}\b',
]
SECTION_RE = re.compile(r'\b(?:Section|Sec\.?|Article)\s*\d+[A-Za-z-]*\b', re.I)


def ocr_image(path):
    if not pytesseract:
        return ""
    return pytesseract.image_to_string(Image.open(path))


def pdf_text(path):
    if not fitz:
        return ""
    doc = fitz.open(path)
    return "\n".join(page.get_text() for page in doc)


def extract_dates(text):
    found = []
    for pattern in DATE_PATTERNS:
        found.extend(re.findall(pattern, text, re.I))
    return list(dict.fromkeys(found))


def extract_sections(text):
    return list(dict.fromkeys(SECTION_RE.findall(text)))


def extract_entities(text):
    lines = [x.strip() for x in text.splitlines() if x.strip()]
    people = []
    for line in lines:
        if re.search(r'\b(?:vs\.?|versus|v\.)\b', line, re.I):
            people.append(line[:180])
    return people[:10]


def build_facts(text):
    sentences = re.split(r'(?<=[.!?])\s+', re.sub(r'\s+', ' ', text).strip())
    keywords = ('alleged', 'complaint', 'incident', 'injury', 'police', 'court', 'agreement', 'notice', 'payment', 'arrest', 'witness', 'contract', 'appeal')
    facts = [s for s in sentences if any(k in s.lower() for k in keywords)]
    return facts[:12]


def analyze_file(path):
    ext = path.suffix.lower()
    text = pdf_text(path) if ext == '.pdf' else ocr_image(path)
    dates = extract_dates(text)
    sections = extract_sections(text)
    facts = build_facts(text)
    warnings = []
    if not text.strip():
        warnings.append('No readable text was detected. Try a clearer image or scanned PDF.')
    if len(text.strip()) < 80:
        warnings.append('Only a small amount of text was extracted; visual/legal conclusions may be incomplete.')
    return {
        'filename': path.name,
        'status': 'success' if text.strip() else 'warning',
        'extracted_text': text[:12000],
        'facts': facts,
        'dates': dates,
        'legal_references': sections,
        'possible_parties': extract_entities(text),
        'image_observations': [
            'OCR completed on the uploaded visual document.',
            'For photographs/evidence, visual-object analysis is enabled when a multimodal provider is configured.'
        ],
        'contradictions': [],
        'analysis': 'This MVP separates extracted evidence from legal interpretation. Add a multimodal model/API key for deeper image and fact reasoning.',
        'warnings': warnings,
    }
