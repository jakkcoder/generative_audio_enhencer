import os
from flask import Flask, jsonify
import subprocess

app = Flask(__name__)

# Input and Output directories
INPUT_DIR = "/app/Documents/input"
OUTPUT_DIR = "/app/Documents/output"

@app.route('/process', methods=['POST'])
def process_audio_files():
    # Ensure input and output directories exist
    if not os.path.exists(INPUT_DIR):
        return jsonify({"error": "Input directory does not exist"}), 400

    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    # Process each .wav file in the input directory
    for filename in os.listdir(INPUT_DIR):
        if filename.endswith(".wav"):
            input_path = os.path.join(INPUT_DIR, filename)
            output_path = os.path.join(OUTPUT_DIR, f"enhanced_{filename}")

            # Run the enhancement script with the correct checkpoint
            command = [
                "python3", "/app/speech-enhancement-sgmse/enhancement.py",
                "--test_dir", INPUT_DIR,
                "--enhanced_dir", OUTPUT_DIR,
                "--ckpt", "/app/speech-enhancement-sgmse/pretrained_checkpoints/speech_enhancement/train_wsj0_2cta4cov_epoch=159.ckpt",  # Update to correct checkpoint path
                "--N", "50",
                "--snr", "0.33",
                "--device", "cuda"
            ]

            subprocess.run(command)

    return jsonify({"status": "Processing complete", "output_dir": OUTPUT_DIR})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
