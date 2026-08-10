FROM python:3.10-slim

WORKDIR /app

# Install system dependencies needed for OpenCV and other packages
RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgl1 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
# Chunk pip installations to prevent Render's 512MB build RAM from OOMing
RUN pip install --no-cache-dir --no-compile tensorflow-cpu==2.18.0
RUN pip install --no-cache-dir --no-compile scipy pandas scikit-learn numpy
RUN pip install --no-cache-dir --no-compile -r requirements.txt

COPY . .
RUN pip install -e .

EXPOSE 8080
ENV FLASK_APP=app.py
ENV FLASK_ENV=production

CMD ["python", "app.py"]
