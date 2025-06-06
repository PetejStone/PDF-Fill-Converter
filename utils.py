from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from PyPDF2 import PdfReader, PdfWriter

def generate_fillable_pdf(fields):
    # Step 1: Create base PDF with reportlab
    packet = BytesIO()
    can = canvas.Canvas(packet, pagesize=letter)

    page_width, page_height = letter
    left_margin = 50
    top_margin = 750
    spacing_y = 50  # vertical space between rows
    field_height = 20
    label_offset = 14  # space above textfield for label

    # Width map: adjust widths based on page size minus margins
    usable_width = page_width - (2 * left_margin)
    width_map = {
        "full": usable_width,
        "half": usable_width / 2,
        "third": usable_width / 3,
    }

    x = left_margin
    y = top_margin
    current_row_width = 0
    row_height = spacing_y

    for i, field in enumerate(fields):
        label = field.get("label", f"Field {i+1}")
        width_key = field.get("width", "full")
        field_width = width_map.get(width_key, width_map["full"])

        # If the field won't fit in current row, wrap to next row
        if current_row_width + field_width > usable_width:
            y -= row_height
            x = left_margin
            current_row_width = 0

        # Draw label
        can.drawString(x, y + label_offset, label + ":")

        # Draw textfield
        can.acroForm.textfield(
            name=f'field_{i}',
            tooltip=label,
            x=x,
            y=y - 18,
            width=field_width - 5,  # small padding
            height=field_height,
            borderStyle='underlined',
            forceBorder=True,
        )

        # Advance x position
        x += field_width
        current_row_width += field_width

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
