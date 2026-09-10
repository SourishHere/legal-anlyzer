# Legal Fact Analyzer

Multimodal-first legal evidence analysis MVP for documents and images.

## Run in GitHub Codespaces

```bash
pip install -r requirements.txt
sudo apt-get update && sudo apt-get install -y tesseract-ocr
uvicorn app:app --host 0.0.0.0 --port 8000
```

Open port 8000 in the Codespaces Ports tab.

## Current pipeline

Upload JPG/PNG/WEBP/PDF → OCR/text extraction → fact/date/legal-reference extraction → evidence-first dashboard.

## Next multimodal layer

The architecture deliberately keeps extraction separate from reasoning so a vision-language model can be added without rewriting the UI. The next layer should accept the original image plus extracted text and return structured visual observations, facts, contradictions, timeline and legal issues. Never present generated legal conclusions as professional legal advice.
