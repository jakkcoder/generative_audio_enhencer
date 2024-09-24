# Video Enhancement Service

This repository provides a Docker-based speech enhancement service that uses GPU for processing. The service takes `.wav` audio files from the input folder, enhances them, and outputs the processed files to the output folder.

## Prerequisites

- A machine with **GPU** support and **Docker** installed.
- Ensure **Docker Compose** is installed.

## Getting Started

### 1. Clone the Repository

```bash
git clone <repository-url>
cd <repository-directory>
```

### 2. Download the Pre-trained Model

Download the pre-trained model checkpoint from Hugging Face:

[Download the Model from Hugging Face](https://huggingface.co/sp-uhh/speech-enhancement-sgmse/resolve/main/pretrained_checkpoints/speech_enhancement/train_wsj0_2cta4cov_epoch%3D159.ckpt)

Once downloaded, move the file to the following directory structure:

```bash
mkdir -p pretrained_checkpoints/speech_enhancement/
mv train_wsj0_2cta4cov_epoch=159.ckpt pretrained_checkpoints/speech_enhancement/
```

### 3. Prepare Your Input and Output Folders

Make sure you have local directories for the input and output files. These directories will be mounted into the Docker container.

- The **input** folder will contain the `.wav` files to be enhanced.
- The **output** folder will be used to store the enhanced files.

```bash
mkdir -p ~/Documents/input
mkdir -p ~/Documents/output
```

Place the audio files you want to enhance inside the `input` folder.

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
curl -X POST http://localhost:5000/process
```

### 6. Retrieve Enhanced Files

After the processing is complete, the enhanced audio files will be saved in the `output` folder.

## Docker Compose File

Your `docker-compose.yml` file should already be configured to use the GPU and mount the necessary volumes. Ensure it includes the necessary configurations for:

- **GPU access**
- **Volume mounts for the input and output folders**

Refer to the repository's existing `docker-compose.yml` file for configuration details.

## Example Folder Structure

```bash
.
├── docker-compose.yml
├── Dockerfile
├── app.py
├── pretrained_checkpoints
│   └── speech_enhancement
│       └── train_wsj0_2cta4cov_epoch=159.ckpt
├── ~/Documents/input  # Contains .wav files to be enhanced
├── ~/Documents/output # Processed files will be saved here
```
```

