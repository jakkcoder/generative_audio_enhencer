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

# ------------------------------------------------
# Set up environment for FastAPI (starter.py)
# ------------------------------------------------
WORKDIR /app/starter

# Copy the starter script files into the container
COPY ./starter.py /app/starter/
COPY starter_requirements.txt /app/starter/starter_requirements.txt

# Install the Python dependencies for the FastAPI app (starter)
RUN pip3 install -r /app/starter/starter_requirements.txt

# Expose port 8000 for FastAPI (starter.py)
EXPOSE 8000

# ------------------------------------------------
# Set up second environment for audio processing (audio_app.py)
# ------------------------------------------------
WORKDIR /app/audio_env

# Copy the audio app and dependencies
COPY ./audio_app.py /app/audio_env/
COPY ./speech-enhancement-sgmse /app/audio_env/speech-enhancement-sgmse

# Install the Python dependencies for the audio app
RUN pip3 install -r /app/audio_env/speech-enhancement-sgmse/requirements.txt

# Install Flask and pydub if not listed in requirements.txt
RUN pip3 install flask pydub

# Expose the Flask app port for audio (port 5000)
EXPOSE 5000

# ------------------------------------------------
# Set up third environment for video processing (video_app.py)
# ------------------------------------------------
WORKDIR /app/video_env

# Copy the video app and dependencies
COPY ./video_app.py /app/video_env/
COPY ./video_requirement.py /app/video_env/video_requirement.py

# Install the Python dependencies for the video app
RUN pip3 install fastapi uvicorn

# Expose the FastAPI port for video (port 8080)
EXPOSE 8080

# ------------------------------------------------
# Start all three apps using supervisord
# ------------------------------------------------

# Install supervisor to manage all processes
RUN apt-get install -y supervisor

# Copy the supervisor configuration file
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Start supervisor to manage all processes
CMD ["supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
