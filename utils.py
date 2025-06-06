from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from PyPDF2 import PdfReader, PdfWriter

def generate_fillable_pdf(fields):
    # Step 1: Create base PDF with reportlab
    packet = BytesIO()
    can = canvas.Canvas(packet, pagesize=letter)
    y = 750

    for i, field in enumerate(fields):
        label = field.get("label", f"Field {i+1}")
        can.drawString(50, y, label + ":")
        can.acroForm.textfield(
            name=f'field_{i}',
            tooltip=label,
            x=150,
            y=y - 4,
            width=300,
            height=20,
            borderStyle='underlined',
            forceBorder=True,
        )
        y -= 40

    can.save()
    packet.seek(0)

    # Step 2: Load with PyPDF2 and output
    new_pdf = PdfReader(packet)
    output = PdfWriter()
    output.add_page(new_pdf.pages[0])
    output.update_page_form_field_values(output.pages[0], {})

    output_stream = BytesIO()
    output.write(output_stream)
    output_stream.seek(0)
    return output_stream
