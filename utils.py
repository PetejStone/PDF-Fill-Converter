from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from PyPDF2 import PdfReader, PdfWriter

def generate_fillable_pdf(fields):
    packet = BytesIO()
    can = canvas.Canvas(packet, pagesize=letter)

    page_width, page_height = letter
    left_margin = 50
    top_margin = 750
    spacing_y = 50
    field_height = 20
    label_offset = 14

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
    row_elements = []  # store element heights to normalize after row

    for i, field in enumerate(fields):
        label = field.get("label", f"Field {i+1}")
        field_type = field.get("type", "text")
        width_key = field.get("width", "full")
        field_width = width_map.get(width_key, width_map["full"])

        # Wrap to next row if needed
        if current_row_width + field_width > usable_width:
            y -= max(row_elements or [spacing_y])
            x = left_margin
            current_row_width = 0
            row_elements = []

        can.drawString(x, y + label_offset, label + ":")

        if field_type in ["select", "checkboxes"]:
            options = field.get("options", [])
            option_spacing = 18
            total_height = len(options) * option_spacing
            for j, option in enumerate(options):
                option_y = y - (j * option_spacing)

                if field_type == "checkboxes":
                    can.acroForm.checkbox(
                        name=f'field_{i}_option_{j}',
                        tooltip=option,
                        x=x,
                        y=option_y,
                        buttonStyle='check',
                        borderStyle='solid',
                        forceBorder=True,
                        size=12,
                    )
                elif field_type == "select":
                    # RADIO buttons - all must share same name
                    can.acroForm.radio(
                        name=f'field_{i}',
                        tooltip=option,
                        value=option,
                        selected=False,  # not selected by default
                        x=x,
                        y=option_y,
                        buttonStyle='circle',
                        borderStyle='solid',
                        forceBorder=True,
                        size=12,
                    )

                can.drawString(x + 18, option_y + 2, option)

            # Store max height used so all items in row stay level
            row_elements.append(total_height)
        else:
            # Text field (message, phone, etc)
            height = field_height * 3 if field_type == "message" else field_height
            can.acroForm.textfield(
                name=f'field_{i}',
                tooltip=label,
                x=x,
                y=y - 18,
                width=field_width - 5,
                height=height,
                borderStyle='underlined',
                forceBorder=True,
            )
            row_elements.append(height + label_offset)

        x += field_width
        current_row_width += field_width

    # Final row spacing
    y -= max(row_elements or [spacing_y])

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
