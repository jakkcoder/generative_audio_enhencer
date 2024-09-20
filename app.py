import os
from flask import Flask, jsonify
import subprocess
import wave
import shutil
from pydub import AudioSegment
from tqdm import tqdm
import time

app = Flask(__name__)

# Input and Output directories
INPUT_DIR = "/app/Documents/input"
OUTPUT_DIR = "/app/Documents/output"
TEMP_INPUT_DIR = "/app/Documents/temp/input"
TEMP_OUTPUT_DIR = "/app/Documents/temp/output"
FINAL_OUTPUT_DIR = "/app/Documents/temp/final_output"

@app.route('/process', methods=['POST'])
def process_audio_files():
    # Ensure input and output directories exist
    for directory in [INPUT_DIR, OUTPUT_DIR, TEMP_INPUT_DIR, TEMP_OUTPUT_DIR, FINAL_OUTPUT_DIR]:
        if not os.path.exists(directory):
            os.makedirs(directory)

    # Process each .wav file in the input directory
    for filename in os.listdir(INPUT_DIR):
        if filename.endswith(".wav"):
            input_path = os.path.join(INPUT_DIR, filename)
            temp_output_file = os.path.join(FINAL_OUTPUT_DIR, f"enhanced_{filename}")

            # Step 1: Convert audio to mono
            audio = AudioSegment.from_wav(input_path)
            mono_audio = audio.set_channels(1)

            # Step 2: Split audio into 8-second chunks
            num_chunks = split_audio_into_chunks(mono_audio, filename)

            # Step 3: Process each chunk sequentially with the model
            process_chunks_with_model()

            # Step 4: Poll until all chunks are processed
            if check_all_chunks_processed(filename, num_chunks):
                # Step 5: Join the chunks back into a complete file
                join_chunks(filename, temp_output_file)

                # Step 6: Convert the final file back to stereo
                convert_to_stereo(temp_output_file)

    return jsonify({"status": "Processing complete", "output_dir": FINAL_OUTPUT_DIR})


def split_audio_into_chunks(audio, filename):
    chunk_length_ms = 8000  # 8 seconds
    chunks = [audio[i:i+chunk_length_ms] for i in range(0, len(audio), chunk_length_ms)]

    # Save chunks in the temp/input directory
    base_filename = os.path.splitext(filename)[0]  # Remove file extension
    for i, chunk in enumerate(chunks):
        chunk.export(os.path.join(TEMP_INPUT_DIR, f"{base_filename}_chunk_{i}.wav"), format="wav")

    return len(chunks)  # Return the number of chunks created




def process_chunks_with_model():
    print("Starting chunk processing...")

    # Get a list of chunk files to process
    chunk_files = sorted([chunk_file for chunk_file in os.listdir(TEMP_INPUT_DIR) if chunk_file.endswith(".wav")])

    # Wrap the chunk processing loop with tqdm to show progress
    for chunk_file in tqdm(chunk_files, desc="Processing chunks", unit="chunk"):
        input_chunk_path = os.path.join(TEMP_INPUT_DIR, chunk_file)
        output_chunk_path = os.path.join(TEMP_OUTPUT_DIR, chunk_file)

        # Check if the chunk is already processed
        if os.path.exists(output_chunk_path):
            print(f"Chunk {chunk_file} already processed, skipping...")
            continue  # Skip already processed chunks

        print(f"Processing chunk: {chunk_file}")

        # Run the enhancement model on the chunk
        command = [
            "python3", "/app/speech-enhancement-sgmse/enhancement.py",
            "--input_file", input_chunk_path,
            "--output_file", output_chunk_path,
            "--ckpt", "/app/speech-enhancement-sgmse/pretrained_checkpoints/speech_enhancement/train_wsj0_2cta4cov_epoch=159.ckpt",
            "--N", "50",
            "--snr", "0.33",
            "--device", "cuda"
        ]

        print(f"Running command: {' '.join(command)}")
        result = subprocess.run(command, capture_output=True, text=True)

        if result.returncode == 0:
            print(f"Successfully processed {chunk_file}")
        else:
            print(f"Error processing {chunk_file}: {result.stderr}")

    print("Finished processing all chunks.")




def check_all_chunks_processed(filename, num_chunks, check_interval=5):
    """
    Poll the TEMP_OUTPUT_DIR to check if all chunks are processed.
    """
    base_filename = os.path.splitext(filename)[0]
    while True:
        output_chunks = [f for f in os.listdir(TEMP_OUTPUT_DIR) if f.startswith(base_filename) and f.endswith(".wav")]
        if len(output_chunks) >= num_chunks:
            return True  # All chunks are processed
        time.sleep(check_interval)  # Wait before checking again


import re  # Import regex for extracting numbers from filenames

def join_chunks(filename, output_file):
    # Combine all chunks from TEMP_OUTPUT_DIR into a single file
    combined = AudioSegment.empty()
    base_filename = os.path.splitext(filename)[0]

    # Extract chunk number using regex and sort accordingly
    def extract_chunk_number(chunk_filename):
        match = re.search(r"_chunk_(\d+)\.wav$", chunk_filename)
        return int(match.group(1)) if match else -1  # Default to -1 if no match

    # List and sort all chunk files by their chunk number
    chunk_files = sorted(
        [f for f in os.listdir(TEMP_OUTPUT_DIR) if f.startswith(base_filename) and f.endswith(".wav")],
        key=extract_chunk_number
    )

    # Combine chunks in order
    for chunk_file in chunk_files:
        print(f"Joining chunk: {chunk_file}")
        chunk = AudioSegment.from_wav(os.path.join(TEMP_OUTPUT_DIR, chunk_file))
        combined += chunk

    combined.export(output_file, format="wav")
    print(f"Joined chunks saved to {output_file}")



def convert_to_stereo(file_path):
    # Convert mono file back to stereo by duplicating the mono channel
    mono_audio = AudioSegment.from_wav(file_path)
    stereo_audio = AudioSegment.from_mono_audiosegments(mono_audio, mono_audio)
    stereo_audio.export(file_path, format="wav")


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
