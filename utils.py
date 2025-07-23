from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase.pdfmetrics import stringWidth
from PyPDF2 import PdfReader, PdfWriter
import requests

def generate_fillable_pdf(fields, logo_url=None, form_title=""):
    page_width, page_height = letter
    left_margin = 50
    top_margin = 750
    spacing_y = 50
    field_height = 20
    label_offset = 14
    min_y_threshold = 100  # Bottom margin

    usable_width = page_width - (2 * left_margin)
    width_map = {
        "full": usable_width,
        "half": usable_width / 2,
        "third": usable_width / 3,
    }

    def new_canvas():
        stream = BytesIO()
        c = canvas.Canvas(stream, pagesize=letter)
        return c, stream

    def wrap_label(label_text, max_width, font_size):
        words = label_text.split()
        lines = []
        current_line = ""
        for word in words:
            test_line = current_line + " " + word if current_line else word
            if stringWidth(test_line, "Helvetica", font_size) <= max_width:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word
        if current_line:
            lines.append(current_line)
        return lines

    page_streams = []
    can, current_stream = new_canvas()
    y = page_height - 60

    def finalize_page():
        can.save()
        page_streams.append(current_stream.getvalue())

    def draw_header():
        nonlocal y
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

    draw_header()

    i = 0
    while i < len(fields):
        row_fields = []
        current_row_width = 0

        while i < len(fields):
            field = fields[i]
            width_key = field.get("width", "full")
            field_width = width_map.get(width_key, width_map["full"])
            if current_row_width + field_width > usable_width:
                break
            row_fields.append((field, field_width, i))
            current_row_width += field_width
            i += 1

        max_field_height = 0
        for field, field_width, idx in row_fields:
            field_type = field.get("dataType", field.get("type", "text")).lower()
            height = field_height * 3 if field_type == "message" else field_height
            if field_type in ["select", "checkboxes"]:
                height = len(field.get("options", [])) * 18
            max_field_height = max(max_field_height, height)

        if y - (max_field_height + spacing_y) < min_y_threshold:
            finalize_page()
            can, current_stream = new_canvas()
            y = page_height - 60
            draw_header()

        x = left_margin
        for field, field_width, idx in row_fields:
            label = field.get("label", f"Field {idx+1}")
            field_type = field.get("dataType", field.get("type", "text")).lower()
            options = field.get("options", [])
            height = field_height * 3 if field_type == "message" else field_height
            font_size = 9
            can.setFont("Helvetica", font_size)

            wrapped_lines = wrap_label(label + ":", field_width, font_size)
            for line_idx, line in enumerate(wrapped_lines):
                can.drawString(x, y + (label_offset + (len(wrapped_lines) - line_idx - 1) * 10), line)

            if field_type in ["select", "checkboxes"]:
                option_spacing = 18
                for j, option in enumerate(options):
                    option_y = y - (j * option_spacing)
                    can.acroForm.checkbox(
                        name=f'field_{idx}_option_{j}',
                        tooltip=option,
                        x=x,
                        y=option_y,
                        buttonStyle='check',
                        borderStyle='solid',
                        forceBorder=True,
                        size=12,
                    )
                    can.drawString(x + 18, option_y + 2, option)
            else:
                can.acroForm.textfield(
                    name=f'field_{idx}',
                    tooltip=label,
                    x=x,
                    y=y - 18,
                    width=field_width - 5,
                    height=height,
                    borderStyle='underlined',
                    forceBorder=True,
                )

            x += field_width

        y -= (max_field_height + spacing_y)

    finalize_page()

    output = PdfWriter()
    for page_bytes in page_streams:
        reader = PdfReader(BytesIO(page_bytes))
        output.add_page(reader.pages[0])

    output.update_page_form_field_values(output.pages[0], {})

    output_stream = BytesIO()
    output.write(output_stream)
    output_stream.seek(0)
    return output_stream
