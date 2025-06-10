from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
from PyPDF2 import PdfReader, PdfWriter
import requests

def generate_fillable_pdf(fields, logo_url=None, form_title=""):
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

    y = page_height - 60  # Top position for drawing
    if logo_url:
        try:
            response = requests.get(logo_url)
            if response.status_code == 200:
                logo_img = ImageReader(BytesIO(response.content))
                logo_width = 150
                logo_height = 50
                can.drawImage(
                    logo_img,
                    (page_width - logo_width) / 2,
                    y - logo_height,
                    width=logo_width,
                    height=logo_height,
                    preserveAspectRatio=True,
                    mask='auto'
                )
                y -= (logo_height + 20)
        except Exception as e:
            print("Logo fetch failed:", e)

    if form_title:
        can.setFont("Helvetica-Bold", 16)
        can.drawCentredString(page_width / 2, y, form_title)
        y -= 40

    x = left_margin
    current_row_width = 0
    row_height = spacing_y

    for i, field in enumerate(fields):
        label = field.get("label", f"Field {i+1}")
        field_type = field.get("dataType", field.get("type", "text")).lower()  # Ensures consistency
        width_key = field.get("width", "full")
        field_width = width_map.get(width_key, width_map["full"])

        if current_row_width + field_width > usable_width:
            y -= row_height
            x = left_margin
            current_row_width = 0

        if field_type == "message":
            can.drawString(x, y + (field_height * 3) - 4, label + ":")
        else:
            can.drawString(x, y + label_offset, label + ":")


        if field_type in ["select", "checkboxes"]:
            options = field.get("options", [])
            option_spacing = 18
            for j, option in enumerate(options):
                option_y = y - (j * option_spacing)

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
                can.drawString(x + 18, option_y + 2, option)

            y -= (len(options) - 1) * option_spacing

        else:
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
