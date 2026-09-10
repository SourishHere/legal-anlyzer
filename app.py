from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import shutil
from analyzer import analyze_file

BASE = Path(__file__).parent
UPLOADS = BASE / "uploads"
UPLOADS.mkdir(exist_ok=True)
app = FastAPI(title="Legal Fact Analyzer")
app.mount("/static", StaticFiles(directory=str(BASE / "static")), name="static")

@app.get("/", response_class=HTMLResponse)
def home():
    return (BASE / "static" / "index.html").read_text()

@app.post("/api/analyze")
async def analyze(file: UploadFile = File(...)):
    allowed = {".png", ".jpg", ".jpeg", ".webp", ".pdf"}
    ext = Path(file.filename or "").suffix.lower()
    if ext not in allowed:
        return {"error": "Use JPG, PNG, WEBP or PDF."}
    target = UPLOADS / ("case_input" + ext)
    with target.open("wb") as out:
        shutil.copyfileobj(file.file, out)
    return analyze_file(target)
