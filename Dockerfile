# Use the specific Playwright base image with Python 3.9 and version 1.31.1
FROM mcr.microsoft.com/playwright/python:v1.31.1-jammy

# Install required Python packages from requirements.txt
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install required dependencies including the Google Chrome repository and key
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
    gnupg \
    # Add the Google Chrome signing key
    && curl -fsSL https://dl.google.com/linux/linux_signing_key.pub | tee /usr/share/keyrings/chrome-archive-keyring.gpg \
    # Add the Google Chrome repository
    && sh -c 'echo "deb [signed-by=/usr/share/keyrings/chrome-archive-keyring.gpg] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list' \
    # Update apt and install Chromium
    && apt-get update \
    && apt-get install -y chromium-browser \
    && rm -rf /var/lib/apt/lists/*

# Install Playwright browsers explicitly
RUN playwright install --with-deps

# Set environment variable for Playwright to use the installed Chromium browser
ENV PLAYWRIGHT_BROWSERS_PATH=/usr/bin

# Copy the application files to the container
COPY . /app

# Set the working directory to the app folder
WORKDIR /app

# Expose port 5000 for the app to listen on
EXPOSE 5000

# Use Waitress to serve the Flask app
CMD ["waitress-serve", "--listen", "0.0.0.0:5000", "app:app"]
