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
        # Launch the browser in headless mode
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        # Intercept requests to manage loading of resources
        def handle_route(route):
            request = route.request
            if request.resource_type == "stylesheet":
                route.abort()  # Block stylesheets to optimize PDF generation
            else:
                route.continue_()

        page.route("**/*", handle_route)

        # Set the HTML content with proper wait times
        page.set_content(html_content, wait_until="domcontentloaded", timeout=120000)

        # Ensure network activity is settled for dynamic content
        page.wait_for_load_state("networkidle", timeout=120000)

        # Ensure the page is ready (e.g., images are loaded)
        page.wait_for_selector("body", timeout=120000)

        # Generate PDF with custom margins and background
        pdf_buffer = page.pdf(
            format="A4",
            print_background=True,
            margin={"top": "1mm", "left": "10mm", "bottom": "1mm", "right": "10mm"},
        )

        # Clean up browser context and close the browser
        context.close()
        browser.close()

        # Return the PDF as a BytesIO object
        pdf_stream = BytesIO(pdf_buffer)
        pdf_stream.seek(0)
        return pdf_stream
        
def generate_pdf(html_content: str) -> BytesIO:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()  # Create a browser context
        page = context.new_page()  # Create a new page instance

        # Debugging logs for requests and responses
        page.on("request", lambda request: print(f"Request: {request.url}"))
        page.on("response", lambda response: print(f"Response: {response.url} - {response.status}"))

        # Set HTML content and wait for all resources to load
        page.set_content(html_content)
        page.wait_for_load_state("networkidle")  # Ensure all resources are loaded

        # Generate PDF with A4 format and background
        pdf_bytes = page.pdf(format="A4", print_background=True)

        # Close the browser
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
