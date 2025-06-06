from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from PyPDF2 import PdfReader, PdfWriter

def generate_fillable_pdf(fields):
    packet = BytesIO()
    can = canvas.Canvas(packet, pagesize=letter)
    y = 750

    for i, field in enumerate(fields):
        label = field.get("label", f"Field {i+1}")
        field_type = field.get("type", "text")
        width = field.get("width", "full")
        options = field.get("options", [])

        field_width = 300 if width == "full" else 200 if width == "half" else 150
        field_height = 60 if field_type == "message" else 20

        can.drawString(50, y, label + ":")

        if field_type == "select":
            for j, option in enumerate(options):
                can.drawString(150, y - (j * 16), f"({chr(0x25EF)}) {option}")
            y -= 16 * len(options) + 10

        elif field_type == "checkboxes":
            for j, option in enumerate(options):
                can.drawString(150, y - (j * 16), f"[  ] {option}")
            y -= 16 * len(options) + 10

        elif field_type == "message":
            can.acroForm.textfield(
                name=f'field_{i}',
                tooltip=label,
                x=150,
                y=y - field_height + 5,
                width=field_width,
                height=field_height,
                borderStyle='underlined',
                forceBorder=True,
                multiline=True
            )
            y -= field_height + 20

        else:
            can.acroForm.textfield(
                name=f'field_{i}',
                tooltip=label,
                x=150,
                y=y - 4,
                width=field_width,
                height=field_height,
                borderStyle='underlined',
                forceBorder=True,
            )
            y -= 40

    can.save()
    packet.seek(0)

    new_pdf = PdfReader(packet)
    output = PdfWriter()
    output.add_page(new_pdf.pages[0])
    output.update_page_form_field_values(output.pages[0], {})
    output_stream = BytesIO()
    output.write(output_stream)
    output_stream.seek(0)
    return output_stream
