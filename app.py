from flask import Flask, request, send_file
from flask_cors import CORS
from utils import generate_fillable_pdf

app = Flask(__name__)
CORS(app, origins=["https://v9yqwg.csb.app", "https://www.stonesquareddevelopment.com/pdf-form-builder"], resources={r"/*": {"origins": "*"}})

@app.route("/generate-pdf", methods=["POST"])
def generate_pdf():
    try:
        data = request.json
        print("Incoming JSON:", data)

        fields = data.get("fields", [])
        logo_url = data.get("logoUrl", None)
        form_title = data.get("formTitle", "")

        pdf_buffer = generate_fillable_pdf(fields, logo_url, form_title)

        return send_file(
            pdf_buffer,
            as_attachment=True,
            download_name="fillable-form.pdf",
            mimetype="application/pdf"
        )
    except Exception as e:
        print("Error generating PDF:", str(e))
        return {"error": str(e)}, 500
