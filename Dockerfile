FROM tensorflow/tensorflow:2.18.0

WORKDIR /app

# Install system dependencies needed for OpenCV and other packages
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN pip install -e .

EXPOSE 8080
ENV FLASK_APP=app.py
ENV FLASK_ENV=production

CMD ["python", "app.py"]
