# Use the specific Playwright base image with Python 3.9 and version 1.31.1
FROM mcr.microsoft.com/playwright/python:v1.31.1-jammy

# Install required python packages from requirements.txt
COPY requirements.txt . 
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers and necessary dependencies
RUN playwright install --with-deps

# Set environment variables for Playwright
ENV PLAYWRIGHT_BROWSERS_PATH=/usr/local/share/.cache/ms-playwright
ENV CHROME_BIN=/usr/local/share/.cache/ms-playwright/chromium-*/chrome-linux/chrome

# Copy the application files to the container
COPY . /app

WORKDIR /app

# Expose port 5000 for the app
EXPOSE 5000

# Use Waitress to serve the Flask app
CMD ["waitress-serve", "--listen", "0.0.0.0:5000", "app:app"]
