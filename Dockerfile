FROM python:3.9-buster

# Install dependencies for Playwright and Chromium
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
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libcups2 \
    libdbus-1-3 \
    libgdk-pixbuf2.0-0 \
    libnspr4 \
    libxcomposite1 \
    libxrandr2 \
    ttf-ubuntu-font-family \
    libenchant-2-2 \
    libicu66 \
    libjpeg-turbo8 \
    libvpx6 \
    libevent-2.1-7 \
    && rm -rf /var/lib/apt/lists/*

# Install required python packages from requirements.txt
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright and its dependencies
RUN pip install playwright
RUN playwright install --with-deps

# Set environment variable for Playwright to use the installed Chromium browser
ENV PLAYWRIGHT_BROWSERS_PATH=/usr/local/share/.cache/ms-playwright

# Copy the application files to the container
COPY . /app

WORKDIR /app

# Expose port 5000 for the app
EXPOSE 5000

# Use Waitress to serve the Flask app
CMD ["waitress-serve", "--listen", "0.0.0.0:5000", "app:app"]
