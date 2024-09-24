# Base image with Python and GPU support (CUDA 11.3 and cuDNN 8 for development)
FROM nvidia/cuda:11.3.1-cudnn8-devel-ubuntu20.04

# Set environment variable to skip interactive timezone setup
ENV DEBIAN_FRONTEND=noninteractive

# Install Python, ffmpeg, and other necessary packages, including libsndfile1-dev for soundfile support
RUN apt-get update && apt-get install -y \
    supervisor \
    python3.8 \
    python3-pip \
    python3-venv \
    git \
    libsndfile1-dev \
    ffmpeg \
    tzdata && \
    rm -rf /var/lib/apt/lists/*

# Set working directory to /app
WORKDIR /app

# Copy the entire directory into /app
COPY . /app

# ------------------------------------------------
# Create and activate virtual environments
# ------------------------------------------------

# Audio processing virtual environment setup
RUN python3 -m venv /app/venvs/audio_env && \
    /app/venvs/audio_env/bin/pip install --upgrade pip && \
    /app/venvs/audio_env/bin/pip install -r /app/audio_requirements.txt && \
    /app/venvs/audio_env/bin/pip install flask pydub

# FastAPI starter virtual environment setup
RUN python3 -m venv /app/venvs/starter_env && \
    /app/venvs/starter_env/bin/pip install --upgrade pip && \
    /app/venvs/starter_env/bin/pip install -r /app/starter_requirements.txt

# Video processing virtual environment setup
RUN python3 -m venv /app/venvs/video_env && \
    /app/venvs/video_env/bin/pip install --upgrade pip && \
    /app/venvs/video_env/bin/pip install -r /app/video_requirements.txt

# Install PyTorch with CUDA from PyTorch official channel
RUN /app/venvs/video_env/bin/pip install torch==1.9.0+cu111 torchvision==0.10.0+cu111 torchaudio==0.9.0 -f https://download.pytorch.org/whl/torch_stable.html

# Install additional Python packages (Flask, pydub, fastapi, uvicorn)
RUN pip3 install flask pydub fastapi uvicorn

# Expose necessary ports
EXPOSE 8000 
EXPOSE 5000
EXPOSE 8080

# Copy the supervisor configuration file
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Start supervisor to manage all processes
CMD ["supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
