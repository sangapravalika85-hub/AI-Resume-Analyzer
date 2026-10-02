import re
from io import BytesIO
from pypdf import PdfReader

SECTION_HEADERS = {"education":["education","academic"],"projects":["projects","project experience"],"certifications":["certifications","certificates","licenses"],"experience":["experience","work history","employment"]}
def clean(text): return re.sub(r"[ \t]+", " ", re.sub(r"\n{3,}", "\n\n", text)).strip()
def section(text, names):
    pattern = r"(?:^|\n)\s*(?:" + "|".join(map(re.escape,names)) + r")\s*[:\-]?\s*(.*?)(?=\n\s*(?:education|academic|projects?|certifications?|certificates?|experience|work history|skills?|summary|languages)\s*[:\-]?|\Z)"
    m = re.search(pattern, text, re.I|re.S); return clean(m.group(1)) if m else ""
def parse_pdf(content, fallback_name):
    reader = PdfReader(BytesIO(content)); text = clean("\n".join(p.extract_text() or "" for p in reader.pages))
    if not text: raise ValueError("No selectable text found in PDF")
    email = (re.search(r"[\w.+-]+@[\w-]+\.[\w.-]+",text) or [None])[0]
    phone = (re.search(r"(?:\+?\d[\d .()\-]{7,}\d)",text) or [None])[0]
    first = next((x.strip() for x in text.splitlines() if x.strip()), fallback_name.rsplit('.',1)[0])
    name = re.sub(r"[^A-Za-z .'-]", "", first).strip()[:180] or fallback_name.rsplit('.',1)[0]
    return {"text":text,"name":name,"email":email,"phone":phone,"education":section(text,SECTION_HEADERS['education']),"projects":section(text,SECTION_HEADERS['projects']),"certifications":section(text,SECTION_HEADERS['certifications']),"experience":section(text,SECTION_HEADERS['experience'])}
