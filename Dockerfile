# Use the specific Playwright base image with Python 3.9 and version 1.31.1
FROM mcr.microsoft.com/playwright/python:v1.31.1-jammy

# Install required Python packages from requirements.txt
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Chromium manually and Playwright dependencies
RUN apt-get update && apt-get install -y \
    chromium \
    libx11-dev \
    libx264-dev \
    libfontconfig1 \
    libxss1 \
    libappindicator3-1 \
    libnss3 \
    && rm -rf /var/lib/apt/lists/*

# Set the Playwright path to use the system-installed Chromium
ENV PLAYWRIGHT_BROWSERS_PATH=/usr/bin

# Install Playwright (without the --with-deps flag)
RUN playwright install

# Copy the application files to the container
COPY . /app

# Set the working directory to the app folder
WORKDIR /app

# Expose port 5000 for the app to listen on
EXPOSE 5000

# Use Waitress to serve the Flask app
CMD ["waitress-serve", "--listen", "0.0.0.0:5000", "app:app"]
