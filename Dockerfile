# Use a lightweight python base image
FROM python:3.9-slim

# Install dependencies and Chromium for Playwright
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    ca-certificates \
    libx11-dev \
    libx264-dev \
    libfontconfig1 \
    libxss1 \
    libappindicator3-1 \
    libnss3 \
    chromium \
    && rm -rf /var/lib/apt/lists/*

# Install required python packages from requirements.txt
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Set environment variable for Playwright to use the installed Chromium browser
ENV PLAYWRIGHT_BROWSERS_PATH=/usr/local/share/.cache/ms-playwright

# Copy the application files to the container
COPY . /app

WORKDIR /app

# Expose port 5000 for the app
EXPOSE 5000

# Use Waitress to serve the Flask app
CMD ["waitress-serve", "--listen", "0.0.0.0:5000", "app:app"]
