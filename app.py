from flask import Flask, request, send_file
from PIL import Image
import pytesseract
import re
import io
import fitz  # PyMuPDF

app = Flask(__name__)

@app.route("/", methods=["GET"])
def index():
    return "✅ OCR-Powered PDF Filler is running."

@app.route("/upload", methods=["POST"])
def upload():
    if 'image' not in request.files:
        return "No file part", 400

    file = request.files['image']
    image = Image.open(file.stream)

    # Run OCR
    text = pytesseract.image_to_string(image)

    def extract(pattern):
        match = re.search(pattern, text)
        return match.group(1).strip() if match else ""

    # Extract fields
    date = extract(r'DATE\s*[:\-]?\s*(\d{1,2}/\w+/\d{2,4})')
    p_operator = extract(r'P OPERATOR\s*[:\-]?\s*([A-Z0-9]+)')
    rail1 = extract(r'RAIL 1\s*[:\-]?\s*([A-Z0-9\-]+)')
    rail2 = extract(r'RAIL 2\s*[:\-]?\s*([A-Z0-9\-]+)')
    w_operator = extract(r'W OPERATOR\s*[:\-]?\s*([A-Z0-9]+)')
    weld = extract(r'WELD\s*[:\-]?\s*([\w\-]+)')
    applied_kn = extract(r'APPLIED\s*[:\-]?\s*(\d+)\s*kN')
    applied_mm = extract(r'&\s*([\d.]+)\s*mm')

    # Load PDF and fill
    pdf_path = "SBT_FBW_Qualification_Checklist.pdf"
    doc = fitz.open(pdf_path)
    page = doc[0]

    positions = {
        "Date": (110, 720),
        "Rail Grade 1": (110, 685),
        "Rail Grade 2": (250, 685),
        "Welder name": (400, 685),
        "Checked by": (480, 590),
        "Test Date": (110, 535),
        "Tested by": (280, 535),
        "Weld #": (90, 550),
        "kN": (400, 535),
        "mm": (460, 535),
    }

    fields = {
        "Date": date,
        "Rail Grade 1": rail1,
        "Rail Grade 2": rail2,
        "Welder name": w_operator,
        "Checked by": p_operator,
        "Test Date": date,
        "Tested by": p_operator,
        "Weld #": weld,
        "kN": applied_kn,
        "mm": applied_mm
    }

    for key, value in fields.items():
        if value:
            x, y = positions.get(key, (0, 0))
            page.insert_text((x, y), value, fontsize=9)

    # Save to memory and return
    output = io.BytesIO()
    doc.save(output)
    output.seek(0)

    return send_file(output, as_attachment=True, download_name="filled_form.pdf", mimetype='application/pdf')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)

