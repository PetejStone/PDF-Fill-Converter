from flask import Flask, request, send_file
from flask_cors import CORS
from utils import generate_fillable_pdf

app = Flask(__name__)
CORS(app)

@app.route("/generate-pdf", methods=["POST"])
def generate_pdf():
    data = request.json
    fields = data.get("fields", [])

    pdf_buffer = generate_fillable_pdf(fields)
    return send_file(
        pdf_buffer,
        as_attachment=True,
        download_name="fillable-form.pdf",
        mimetype="application/pdf"
    )

if __name__ == "__main__":
    app.run(debug=True)
