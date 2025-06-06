from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from PyPDF2 import PdfReader, PdfWriter

def generate_fillable_pdf(fields):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    # Define page margins and usable width (A4 width = 210mm)
    left_margin = 10
    right_margin = 10
    full_width = 210 - left_margin - right_margin

    # Map width keywords to fractions of full_width
    width_map = {
        "full": full_width,
        "half": full_width / 2,
        "third": full_width / 3,
        # Add more if needed
    }

    y = 10  # Starting y position
    x = left_margin
    current_line_width = 0
    line_height = 10

    for field in fields:
        label = field.get("label", "Field")
        w_key = field.get("width", "full")
        field_width = width_map.get(w_key, full_width)

        # If adding this field exceeds the line, move to next line
        if current_line_width + field_width > full_width:
            y += line_height
            x = left_margin
            current_line_width = 0

        # Draw the label
        pdf.set_xy(x, y)
        pdf.cell(field_width, 5, f"{label}:", ln=2)

        # Draw a line for filling
        pdf.set_xy(x, y + 5)
        pdf.cell(field_width, 5, "_" * int(field_width / 3))  # Approx line length

        # Update x and current line width for next field
        x += field_width
        current_line_width += field_width

    buffer = BytesIO()
    pdf.output(buffer)
    buffer.seek(0)
    return buffer
