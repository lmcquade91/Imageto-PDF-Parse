import streamlit as st
from PyPDF2 import PdfReader, PdfWriter
from PIL import Image
import pytesseract
import io
import re

st.title("FBW Snip to Editable PDF")
st.markdown("Upload up to 5 snips. We'll extract the key details and insert them into the PDF.")

uploaded_files = st.file_uploader("Upload up to 5 snips (images)", accept_multiple_files=True, type=["png", "jpg", "jpeg"])

pdf_template_path = "blank pdf.pdf"  # Assumes this is present in the working dir

# Mapping function to extract fields from OCR text
def parse_fields(text):
    fields = {}
    
    # Basic extraction logic
    fields['P_OPERATOR'] = re.search(r"P OPERATOR\s*[:\-]?\s*(\w+)", text)
    fields['W_OPERATOR'] = re.search(r"W OPERATOR\s*[:\-]?\s*(\w+)", text)
    fields['WELD'] = re.search(r"WELD\s*[:\-]?\s*([\w\-]+)", text)
    fields['RAIL_1'] = re.search(r"RAIL 1\s*[:\-]?\s*(\w+)", text)
    fields['RAIL_2'] = re.search(r"RAIL 2\s*[:\-]?\s*(\w+)", text)
    fields['TEST'] = re.search(r"TEST\s*[:\-]?\s*(G\d+)", text)
    fields['APPLIED_KN'] = re.search(r"APPLIED[^\d]*(\d+\.?\d*)\s*kN", text)
    fields['APPLIED_MM'] = re.search(r"(\d+\.?\d*)\s*mm", text)
    fields['DATE'] = re.search(r"DATE\s*[:\-]?\s*(\d{2}/\w{3}/\d{4})", text)
    fields['DURATION_LINE'] = re.search(r"DURATION.*\n(.*)", text)

    # Format results
    return {
        "Checked by": fields['P_OPERATOR'].group(1) if fields['P_OPERATOR'] else "",
        "Tested by": fields['P_OPERATOR'].group(1) if fields['P_OPERATOR'] else "",
        "Welder name": fields['W_OPERATOR'].group(1) if fields['W_OPERATOR'] else "",
        "Weld #": fields['WELD'].group(1) if fields['WELD'] else "",
        "Rail Grade 1": fields['RAIL_1'].group(1) if fields['RAIL_1'] else "",
        "Rail Grade 2": fields['RAIL_2'].group(1) if fields['RAIL_2'] else "",
        "SBT Test #": fields['TEST'].group(1) if fields['TEST'] else "",
        "kN": fields['APPLIED_KN'].group(1) if fields['APPLIED_KN'] else "",
        "mm": fields['APPLIED_MM'].group(1) if fields['APPLIED_MM'] else "",
        "FBW Machine ID": fields['DURATION_LINE'].group(1).strip() if fields['DURATION_LINE'] else "",
        "Date": fields['DATE'].group(1) if fields['DATE'] else "",
        "Test Date": fields['DATE'].group(1) if fields['DATE'] else "",
    }

# Run on button press
if st.button("Parse and Generate PDF"):
    if not uploaded_files:
        st.warning("Please upload at least one snip.")
    else:
        parsed_entries = []

        for file in uploaded_files[:5]:
            image = Image.open(file).convert("RGB")
            text = pytesseract.image_to_string(image)
            parsed_data = parse_fields(text)
            parsed_entries.append(parsed_data)

        # For now, just preview the extracted entries
        st.success("Parsed entries:")
        for i, entry in enumerate(parsed_entries):
            st.write(f"### Snip {i+1}")
            st.json(entry)

        # PDF filling step will be added next once parsing confirmed
