# GENERATIVE Audio and Video Enhancement Service

This repository provides a Docker-based service for **video enhancement** that uses GPU for processing. The service takes `.wav` audio files and `.mp4` video files from the input folder, processes them, and outputs the processed files to the output folder.
It uses generative AI for video as well as audio quality imporovement.

## Prerequisites

- A machine with **GPU** support and **Docker** installed.
- Ensure **Docker Compose** is installed.

## Getting Started

### 1. Clone the Repository

```bash
git clone <repository-url>
cd <repository-directory>
```

### 2. Download the Pre-trained Model for Speech Enhancement

Download the pre-trained model checkpoint from Hugging Face:

[Download the Model from Hugging Face](https://huggingface.co/sp-uhh/speech-enhancement-sgmse/resolve/main/pretrained_checkpoints/speech_enhancement/train_wsj0_2cta4cov_epoch%3D159.ckpt)

Once downloaded, move the file to the following directory structure:

```bash
mkdir -p pretrained_checkpoints/speech_enhancement/
mv train_wsj0_2cta4cov_epoch=159.ckpt pretrained_checkpoints/speech_enhancement/
```

### 3. Prepare Your Input and Output Folders

Make sure you have local directories for the input and output files. These directories will be mounted into the Docker container.

- The **input** folder will contain the `.wav` audio files and `.mp4` video files to be processed.
- The **output** folder will be used to store the processed files.

```bash
mkdir -p ~/Documents/input
mkdir -p ~/Documents/output
```

Place the audio files you want to enhance and video files you want to process inside the `input` folder.

### 4. Build and Run the Docker Container

Build the Docker container using **Docker Compose**:

```bash
docker-compose build
```

Start the service:

```bash
docker-compose up
```

### 5. Process Audio Files

Once the Docker container is up and running, you can start processing the audio files in the `input` folder by sending a `POST` request to the service using `curl`:

```bash
curl -X GET "http://localhost:8000/process_file"
```

### 6. Process Video Files

Similarly, you can start processing video files in the `input` folder by sending a `POST` request to the video service using `curl`:

```bash
curl -X POST http://localhost:8080/process_video
```

### 7. Retrieve Processed Files

After the processing is complete:
- The enhanced audio files will be saved in the `output` folder.
- The processed video files will also be saved in the `output` folder.

### 8. Accessing the APIs

- **Audio Processing**: The audio processing service runs on **port 5000**. You can interact with the Flask-based service for audio processing.
- **Video Processing**: The video processing service runs on **port 8080**. This FastAPI-based service handles video file processing.

## Docker Compose File

Your `docker-compose.yml` file is configured to use the GPU and mount the necessary volumes for input and output. It includes separate services for both audio and video processing, ensuring they run in isolated environments while sharing GPU resources.

Ensure it includes the necessary configurations for:

- **GPU access**
- **Volume mounts for the input and output folders**

Refer to the repository's existing `docker-compose.yml` file for configuration details.

## Example Folder Structure

```bash
.
├── docker-compose.yml
├── Dockerfile
├── starter.py           # FastAPI app for initial setup and processing
├── audio_app.py         # Flask app for audio processing
├── video_app.py         # FastAPI app for video processing
├── pretrained_checkpoints
│   └── speech_enhancement
│       └── train_wsj0_2cta4cov_epoch=159.ckpt
├── ~/Documents/input    # Contains .wav and .mp4 files to be processed
├── ~/Documents/output   # Processed files will be saved here
```

## Additional Information

- Ensure that your Docker container has access to a **GPU**. The `docker-compose.yml` file includes the necessary configurations to allocate GPU resources to the container.
- You can monitor the logs of both the audio and video processing services using the following commands:
  - **Audio service** logs: `docker logs audio-processing-service`
  - **Video service** logs: `docker logs video-processing-service`
  
---