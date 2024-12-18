from flask import Flask, request, Response, jsonify, Blueprint
from flask_cors import CORS
from playwright.sync_api import sync_playwright
from io import BytesIO


# Create Flask app
app = Flask(__name__)

# Enable CORS for all routes
CORS(app, origins=[
    "https://auto-certification.vercel.app",  # Production
    "http://localhost:3000",                  # Local development
])
# Define a Blueprint for routes
bp = Blueprint('main', __name__)

# Function to generate PDF from HTML content using Playwright
def generate_pdf(html_content: str, **pdf_options) -> BytesIO:


    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Set the HTML content and wait for network idle
        page.set_content(html_content, wait_until="networkidle")

        # Generate PDF with customizable options
        pdf_buffer = page.pdf(**pdf_options)

        page.close()
        browser.close()

        return pdf_buffer
    

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
        pdf_buffer = generate_pdf(html_content)

        # Return the PDF file as an attachment in the response
        return Response(
            pdf_buffer,
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
