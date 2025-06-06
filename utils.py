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
    spacing_y = 50  # vertical space between rows
    field_height = 20
    label_offset = 14  # space above textfield for label

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
        options = field.get("options", [])
        field_type = field.get("type", "text")

        # Wrap row if needed
        if current_row_width + field_width > usable_width:
            y -= row_height
            x = left_margin
            current_row_width = 0

        can.drawString(x, y + label_offset, label + ":")

        if field_type in ["text", "phone", "email", "address", "date"]:
            # Draw a textfield
            can.acroForm.textfield(
                name=f"field_{i}",
                tooltip=label,
                x=x,
                y=y - 18,
                width=field_width - 5,
                height=field_height,
                borderStyle="underlined",
                forceBorder=True,
            )
        elif field_type == "message":
            # For message, make a bigger textarea
            textarea_height = field_height * 3
            can.acroForm.textfield(
                name=f"field_{i}",
                tooltip=label,
                x=x,
                y=y - textarea_height,
                width=field_width - 5,
                height=textarea_height,
                borderStyle="underlined",
                forceBorder=True,
                multiline=True,
            )
        elif field_type == "checkboxes":
            # Draw checkboxes for each option horizontally spaced
            box_size = 15
            option_spacing = 10 + box_size  # space between checkboxes
            start_x = x
            for idx, opt in enumerate(options):
                checkbox_x = start_x + idx * option_spacing
                can.drawString(checkbox_x + box_size + 2, y + label_offset, opt)
                can.acroForm.checkbox(
                    name=f"field_{i}_opt_{idx}",
                    tooltip=opt,
                    x=checkbox_x,
                    y=y - 18,
                    size=box_size,
                    borderStyle="solid",
                    forceBorder=True,
                )
        elif field_type == "select":
            # Draw radio buttons horizontally spaced
            button_size = 15
            option_spacing = 10 + button_size
            start_x = x
            group_name = f"field_{i}"
            for idx, opt in enumerate(options):
                radio_x = start_x + idx * option_spacing
                can.drawString(radio_x + button_size + 2, y + label_offset, opt)
                can.acroForm.radio(
                    name=group_name,
                    value=opt,
                    x=radio_x,
                    y=y - 18,
                    buttonStyle="circle",
                    borderStyle="solid",
                    size=button_size,
                    forceBorder=True,
                )
        else:
            # fallback to textfield
            can.acroForm.textfield(
                name=f"field_{i}",
                tooltip=label,
                x=x,
                y=y - 18,
                width=field_width - 5,
                height=field_height,
                borderStyle="underlined",
                forceBorder=True,
            )

        x += field_width
        current_row_width += field_width

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
