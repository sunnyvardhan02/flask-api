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

def generate_pdf_with_images(html_content: str) -> BytesIO:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        # Debugging requests and responses
        page.on("request", lambda request: print(f"Request: {request.url}"))
        page.on("response", lambda response: print(f"Response: {response.url}, Status: {response.status}"))

        # Load HTML content with base URL
        base_url = "http://localhost:3000"  # Change to your deployed app's URL in production
        page.set_content(html_content, wait_until="domcontentloaded", base_url=base_url)

        # Wait for images to load
        page.evaluate("""
            Array.from(document.images).forEach(img => {
                img.complete || img.decode();
            });
        """)

        # Wait for network to be idle
        page.wait_for_load_state("networkidle")

        # Generate PDF
        pdf_buffer = page.pdf(
            format="A4",
            print_background=True,
            margin={"top": "1mm", "left": "10mm", "bottom": "1mm", "right": "10mm"}
        )

        context.close()
        browser.close()

        pdf_stream = BytesIO(pdf_buffer)
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
