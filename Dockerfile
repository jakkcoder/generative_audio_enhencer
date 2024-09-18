# Base image with Python and GPU support (CUDA 11.3 and cuDNN 8 for development)
FROM nvidia/cuda:11.3.1-cudnn8-devel-ubuntu20.04

# Set environment variable to skip interactive timezone setup
ENV DEBIAN_FRONTEND=noninteractive

# Install Python, ffmpeg, and other necessary packages, including libsndfile1-dev for soundfile support
RUN apt-get update && apt-get install -y \
    python3.8 \
    python3-pip \
    git \
    libsndfile1-dev \
    ffmpeg \
    tzdata && \
    rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy the rest of your project files into the container
COPY . /app

# Install Python dependencies from requirements.txt
RUN pip3 install -r /app/speech-enhancement-sgmse/requirements.txt

# Install Flask and pydub if not listed in requirements.txt
RUN pip3 install flask pydub

# Expose the Flask app port
EXPOSE 5000

# Command to run the Flask app
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]
