from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import shutil
from analyzer import analyze_case

BASE = Path(__file__).parent
UPLOADS = BASE / "uploads"
UPLOADS.mkdir(exist_ok=True)
app = FastAPI(title="Legal Case Evidence Analyzer")
app.mount("/static", StaticFiles(directory=str(BASE / "static")), name="static")

@app.get("/", response_class=HTMLResponse)
def home():
    return (BASE / "static" / "index.html").read_text()

@app.post("/api/analyze")
async def analyze(event: str = Form(...), files: list[UploadFile] = File(...)):
    allowed = {".png", ".jpg", ".jpeg", ".webp", ".pdf"}
    saved = []
    for i, file in enumerate(files[:8]):
        ext = Path(file.filename or "").suffix.lower()
        if ext not in allowed:
            return {"error": f"Unsupported file: {file.filename}. Use JPG, PNG, WEBP or PDF."}
        target = UPLOADS / f"evidence_{i}{ext}"
        with target.open("wb") as out:
            shutil.copyfileobj(file.file, out)
        saved.append(target)
    return analyze_case(event, saved)
