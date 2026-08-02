# Use an official Python runtime as a parent image, slim version for optimization
FROM python:3.10-slim

# Set working directory in container
WORKDIR /app

# Install system dependencies required for OpenCV and image processing
RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgl1 \
    && rm -rf /var/lib/apt/lists/*

# Copy project files into container
COPY . .

# Install dependencies and local Respire package
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install -e .

# Expose port
EXPOSE 8080

# Environment variables
ENV FLASK_APP=app.py
ENV FLASK_ENV=production

# Run Flask application
CMD ["python", "app.py"]