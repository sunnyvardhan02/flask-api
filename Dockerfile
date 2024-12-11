# Use the specific Playwright base image with Python 3.9 and version 1.31.1
FROM mcr.microsoft.com/playwright/python:v1.31.1-jammy

# Install required Python packages from requirements.txt
COPY requirements.txt . 
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers
RUN npx playwright install --with-deps

# Set the working directory
WORKDIR /app

# Copy the application files to the container
COPY . /app

# Expose port 5000 for the app
EXPOSE 5000

# Run the app using Waitress
CMD ["waitress-serve", "--listen", "0.0.0.0:5000", "app:app"]
