from flask import Flask, request, Response, jsonify, Blueprint
from flask_cors import CORS
from playwright.sync_api import sync_playwright
from io import BytesIO

# Create Flask app
app = Flask(__name__)

# Enable CORS for all routes
CORS(app)

# Define a Blueprint for routes
bp = Blueprint('main', __name__)

# Function to generate PDF from HTML content using Playwright
def generate_pdf(html_content: str) -> BytesIO:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.set_content(html_content)
        pdf_bytes = page.pdf(format="A4", print_background=True)
        browser.close()
    
    # Return PDF as a BytesIO stream
    pdf_stream = BytesIO(pdf_bytes)
    pdf_stream.seek(0)
    return pdf_stream

# Define route to handle PDF generation
@bp.route('/generate-pdf', methods=['POST'])
def generate_pdf_api():
    try:
        # Get HTML content from the request body
        data = request.get_json()
        html_content = data.get('htmlContent')

        if not html_content:
            return Response(
                '{"error": "HTML content is required"}',
                status=400,
                mimetype='application/json'
            )

        # Generate PDF from HTML content
        pdf_stream = generate_pdf(html_content)

        # Return the PDF file as an attachment in the response
        return Response(
            pdf_stream,
            content_type='application/pdf',
            headers={'Content-Disposition': 'attachment; filename=certificate.pdf'}
        )

    except Exception as e:
        # Handle errors and send a response
        return Response(
            '{"error": "Failed to generate PDF: ' + str(e) + '"}',
            status=500,
            mimetype='application/json'
        )

# Register the blueprint
app.register_blueprint(bp)

# Function to create and return the app
def create_app():
    return app

# Run the app if this script is executed directly
if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
