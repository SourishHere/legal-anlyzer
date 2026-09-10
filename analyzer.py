from pathlib import Path
import re

try:
    import pytesseract
    from PIL import Image
except Exception:
    pytesseract = None
    Image = None

try:
    import fitz
except Exception:
    fitz = None

DATE_PATTERNS = [
    r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',
    r'\b\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}\b',
]


def ocr_image(path):
    if not pytesseract or not Image:
        return ""
    try:
        return pytesseract.image_to_string(Image.open(path))
    except Exception:
        return ""


def pdf_text(path):
    if not fitz:
        return ""
    try:
        doc = fitz.open(path)
        return "\n".join(page.get_text() for page in doc)
    except Exception:
        return ""


def extract_text(path):
    return pdf_text(path) if path.suffix.lower() == '.pdf' else ocr_image(path)


def dates(text):
    found = []
    for pattern in DATE_PATTERNS:
        found.extend(re.findall(pattern, text, re.I))
    return list(dict.fromkeys(found))


def sentences(text):
    clean = re.sub(r'\s+', ' ', text).strip()
    return [x.strip() for x in re.split(r'(?<=[.!?])\s+', clean) if x.strip()]


def analyze_case(event, files):
    evidence = []
    all_text = []
    all_dates = []
    for path in files:
        text = extract_text(path)
        all_text.append(text)
        all_dates.extend(dates(text))
        evidence.append({
            'file': path.name,
            'ocr_text': text[:5000],
            'observations': visual_fallback_observations(path, text),
            'supports_event': support_score(event, text),
        })

    combined = ' '.join(all_text)
    event_lower = event.lower()
    event_words = set(re.findall(r'[a-z0-9]{4,}', event_lower))
    evidence_words = set(re.findall(r'[a-z0-9]{4,}', combined.lower()))
    overlap = sorted(event_words & evidence_words)
    score = round(100 * len(overlap) / max(len(event_words), 1))

    supporting = [e['file'] for e in evidence if e['supports_event'] >= 40]
    weak = [e['file'] for e in evidence if e['supports_event'] < 40]
    missing = []
    for concept, words in {
        'time': {'time', 'pm', 'am', 'oclock', 'morning', 'evening', 'night'},
        'location': {'near', 'road', 'street', 'gate', 'college', 'address'},
        'person/party': {'driver', 'victim', 'person', 'witness', 'owner'},
    }.items():
        if any(w in event_lower for w in words) and not any(w in combined.lower() for w in words):
            missing.append(f'{concept} is claimed in the event but not verified in the uploaded evidence.')

    return {
        'status': 'success',
        'event_description': event,
        'event_match_score': score,
        'event_match_summary': match_summary(score),
        'supported_claims': supporting,
        'unverified_or_weak_evidence': weak,
        'missing_verification': missing,
        'evidence': evidence,
        'dates': list(dict.fromkeys(all_dates)),
        'facts_from_evidence': evidence_facts(combined),
        'contradictions': [],
        'case_analysis': build_analysis(event, evidence, score, missing),
        'extracted_text': combined[:12000],
        'warnings': [
            'Visual observations are conservative in the no-AI-provider mode. Configure a vision model for object, scene and damage recognition.'
        ],
    }


def support_score(event, text):
    ew = set(re.findall(r'[a-z0-9]{4,}', event.lower()))
    tw = set(re.findall(r'[a-z0-9]{4,}', text.lower()))
    return round(100 * len(ew & tw) / max(len(ew), 1))


def match_summary(score):
    if score >= 65:
        return 'Strong textual overlap between the event description and extracted evidence.'
    if score >= 35:
        return 'Some parts of the event are supported by the evidence, but verification is incomplete.'
    return 'The uploaded evidence provides limited textual support for the event description.'


def evidence_facts(text):
    keywords = ('incident', 'accident', 'injury', 'damage', 'vehicle', 'witness', 'police', 'payment', 'message', 'complaint', 'occurred', 'happened')
    return [s for s in sentences(text) if any(k in s.lower() for k in keywords)][:15]


def visual_fallback_observations(path, text):
    obs = [f'Evidence file received: {path.name}.']
    if text.strip():
        obs.append('Readable text was extracted from this evidence.')
    else:
        obs.append('No reliable text was detected. A vision model is required for meaningful scene/object analysis.')
    return obs


def build_analysis(event, evidence, score, missing):
    lines = [f'Event described: {event}', f'Initial evidence-to-event match: {score}/100.']
    if evidence:
        lines.append(f'{len(evidence)} evidence file(s) were processed.')
    if missing:
        lines.append('Verification gaps: ' + ' '.join(missing))
    lines.append('Important: this is evidence analysis, not a final legal conclusion. Facts should be verified against the original evidence and applicable law.')
    return ' '.join(lines)
