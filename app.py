import gradio as gr
from PIL import Image
import pytesseract
import fitz  # PyMuPDF
import re

def parse_and_fill(image):
    # Step 1: OCR text extraction
    text = pytesseract.image_to_string(image)

    # Step 2: Parse key values
    test_id = re.search(r'TEST\\s*:\\s*(\\w+)', text)
    operator_p = re.search(r'P OPERATOR\\s*:\\s*(\\w+)', text)
    conformity_kN = re.search(r'CONFORMITY\\s*:\\s*(\\d+)\\s*kN', text)
    conformity_mm = re.search(r'&\\s*([\\d.]+)\\s*mm', text)

    # Step 3: Default safe values
    test_id = test_id.group(1) if test_id else "N/A"
    operator_p = operator_p.group(1) if operator_p else "N/A"
    conformity_kN = conformity_kN.group(1) if conformity_kN else "N/A"
    conformity_mm = conformity_mm.group(1) if conformity_mm else "N/A"

    # Step 4: Open the PDF and write fields
    template_path = "SBT_FBW_Qualification_Checklist.pdf"
    output_path = "output_filled_form.pdf"
    doc = fitz.open(template_path)
    page = doc[0]

    page.insert_text((100, 100), f"Test ID: {test_id}", fontsize=10)
    page.insert_text((100, 120), f"P Operator: {operator_p}", fontsize=10)
    page.insert_text((100, 140), f"Conformity: {conformity_kN} kN & {conformity_mm} mm", fontsize=10)

    doc.save(output_path)
    return output_path

iface = gr.Interface(
    fn=parse_and_fill,
    inputs=gr.Image(type="pil", label="Upload Snip"),
    outputs=gr.File(label="Download Filled PDF"),
    title="Flashbutt Welder Form Filler",
    description="Upload a snip of test data to auto-fill the Flashbutt Welder Qualification PDF form."
)

if __name__ == "__main__":
    iface.launch()
