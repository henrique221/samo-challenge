FROM ubuntu:22.04

# Prevent interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

# Update package list and install required packages
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    ffmpeg \
    wget \
    curl \
    software-properties-common \
    && add-apt-repository ppa:tomtomtom/yt-dlp \
    && apt-get update \
    && apt-get install -y yt-dlp \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements file first
COPY requirements.txt .

# Install Python dependencies
RUN pip3 install flask google-generativeai
RUN pip3 install -r requirements.txt

# Copy application files
COPY app.py .
COPY video_analyzer.py .
COPY templates templates/

# Create downloads directory
RUN mkdir -p downloads

# Expose port 5000
EXPOSE 5000

# Run the Flask application
CMD ["python3", "app.py"]