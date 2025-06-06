from fpdf import FPDF
from io import BytesIO

def generate_fillable_pdf(fields):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    y = 20
    for field in fields:
        label = field.get("label", "Field")
        pdf.text(10, y, f"{label}: __________________________")
        y += 10

    buffer = BytesIO()
    pdf_output = pdf.output(dest='S').encode('latin1')
    buffer = BytesIO(pdf_output)
    return buffer

    buffer.seek(0)
    return buffer
