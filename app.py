from flask import Flask, request, send_file
from flask_cors import CORS
from io import BytesIO
from fpdf import FPDF

app = Flask(__name__)
CORS(app)

@app.route("/generate-pdf", methods=["POST"])
def generate_pdf():
    data = request.json
    fields = data.get("fields", [])

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    y = 10
    for field in fields:
        label = field.get("label", "Field")
        pdf.text(10, y, f"{label}: ______________________")
        y += 10

    buffer = BytesIO()
    pdf.output(buffer)
    buffer.seek(0)

    return send_file(buffer, as_attachment=True, download_name="form.pdf", mimetype="application/pdf")

if __name__ == "__main__":
    app.run()
