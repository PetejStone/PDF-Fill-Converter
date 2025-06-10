from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
from io import BytesIO
import requests
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
from PyPDF2 import PdfReader, PdfWriter
from pdfrw import PdfDict, PdfName, PdfObject

app = Flask(__name__)
CORS(app)

@app.route('/generate-pdf', methods=['POST'])
def generate_pdf():
    data = request.json
    fields = data.get("fields", [])
    logo_url = data.get("logoUrl", "").strip()
    form_title = data.get("formTitle", "").strip()

    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    y = height - 50  # start near top of page

    # Draw logo if provided
    if logo_url:
        try:
            response = requests.get(logo_url)
            if response.status_code == 200:
                image = ImageReader(BytesIO(response.content))
                logo_width = width * 0.33
                logo_height = logo_width * 0.33  # approx aspect
                c.drawImage(
                    image,
                    (width - logo_width) / 2,
                    y - logo_height,
                    width=logo_width,
                    height=logo_height,
                    preserveAspectRatio=True,
                    mask='auto'
                )
                y -= logo_height + 20
        except Exception as e:
            print(f"Error loading logo: {e}")

    # Draw title if provided
    if form_title:
        c.setFont("Helvetica-Bold", 16)
        c.drawCentredString(width / 2, y, form_title)
        y -= 30

    c.save()

    # Read static portion and prepare for fields
    buffer.seek(0)
    base_pdf = PdfReader(buffer)
    writer = PdfWriter()
    page = base_pdf.pages[0]
    writer.add_page(page)

    # Start placing fields below logo/title
    field_y = y - 20
    field_margin = 40
    field_height = 20
    field_gap = 10

    def create_field(name, x, y, w, h, field_type="Tx", options=None):
        field = {
            "/FT": PdfName(field_type),
            "/T": PdfObject(f"({name})"),
            "/Ff": 0,
            "/Rect": [x, y, x + w, y + h],
            "/V": PdfObject("()")
        }
        if field_type == "Btn" and options:
            field["/Kids"] = []
        elif field_type == "Ch" and options:
            field["/Opt"] = [PdfObject(f"({opt})") for opt in options]
        return PdfDict(field)

    acro_form_fields = []

    for field in fields:
        label = field["label"]
        field_type = field["type"]
        width_percent = field["width"]
        options = field.get("options", [])

        if field_type == "message":
            h = field_height * 3
        else:
            h = field_height

        w = {
            "full": width - 2 * field_margin,
            "half": (width - 3 * field_margin) / 2,
            "third": (width - 4 * field_margin) / 3
        }.get(width_percent, width - 2 * field_margin)

        if field_type == "checkboxes":
            # Render each checkbox option
            for i, option in enumerate(options):
                if field_y < 60:
                    writer.add_page(page)
                    field_y = height - 60

                checkbox_width = 12
                checkbox_height = 12

                x = field_margin
                y_pos = field_y
                writer.add_annotation({
                    "/Subtype": "/Widget",
                    "/FT": "/Btn",
                    "/T": PdfObject(f"({label}_{option})"),
                    "/Rect": [x, y_pos, x + checkbox_width, y_pos + checkbox_height],
                    "/Ff": 0,
                    "/V": "/Off",
                    "/AS": "/Off"
                })
                field_y -= (checkbox_height + field_gap)
        else:
            if field_y < 60:
                writer.add_page(page)
                field_y = height - 60

            x = field_margin
            y_pos = field_y

            form_field_type = {
                "select": "Ch",
                "checkboxes": "Btn"
            }.get(field_type, "Tx")

            field_dict = create_field(label, x, y_pos, w, h, field_type=form_field_type, options=options)
            annotation = PdfDict(
                FT=field_dict["/FT"],
                T=field_dict["/T"],
                Rect=field_dict["/Rect"],
                V=field_dict["/V"],
                Ff=field_dict["/Ff"],
                Type=PdfName("Annot"),
                Subtype=PdfName("Widget"),
                DA=PdfObject("/Helv 0 Tf 0 g")
            )
            if "/Opt" in field_dict:
                annotation["/Opt"] = field_dict["/Opt"]
            acro_form_fields.append(annotation)
            writer._pages[-1].Annots = writer._pages[-1].Annots or []
            writer._pages[-1].Annots.append(annotation)
            field_y -= (h + field_gap)

    # Create AcroForm
    writer._root.AcroForm = PdfDict(
        Fields=acro_form_fields,
        DA=PdfObject("/Helv 0 Tf 0 g"),
        NeedAppearances=PdfObject("true")
    )

    output = BytesIO()
    writer.write(output)
    output.seek(0)
    return send_file(output, as_attachment=True, download_name="fillable-form.pdf", mimetype="application/pdf")


if __name__ == '__main__':
    app.run(debug=True)
