# Use an official Python runtime as a parent image, slim version for optimization
FROM python:3.10-slim-buster

# Set the working directory in the container
WORKDIR /app

# Install system dependencies (required for OpenCV/Pillow if needed)
RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
# We also install flask-cors here since we'll decouple the API
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /app
COPY . .

# Expose port 8080 for the Flask API
EXPOSE 8080

# Define environment variable for Flask
ENV FLASK_APP=app.py
ENV FLASK_ENV=production

# Run app.py when the container launches
CMD ["python", "app.py"]