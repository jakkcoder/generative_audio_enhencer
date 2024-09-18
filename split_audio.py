import os
from pydub import AudioSegment
from pydub.utils import make_chunks

def split_audio_to_mono(input_file, output_dir, chunk_length_ms=10000):
    """
    Splits an audio file into chunks of specified duration (default is 10 seconds)
    and converts the audio to mono.

    Args:
        input_file (str): Path to the input audio file.
        output_dir (str): Directory to save the split audio chunks.
        chunk_length_ms (int): Length of each chunk in milliseconds (default is 10 seconds).
    """
    # Load the audio file
    audio = AudioSegment.from_file(input_file)

    # Convert to mono (1 channel) if the audio is stereo
    if audio.channels > 1:
        print(f"Converting {input_file} to mono...")
        audio = audio.set_channels(1)

    # Make sure the output directory exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Split the audio into chunks
    chunks = make_chunks(audio, chunk_length_ms)

    # Export each chunk as a separate file
    for i, chunk in enumerate(chunks):
        chunk_name = os.path.join(output_dir, f"chunk_{i}.wav")
        print(f"Exporting {chunk_name}")
        chunk.export(chunk_name, format="wav")

if __name__ == "__main__":
    input_file = r"C:\Users\jaysh\Documents\output.wav"  # Replace with your input audio file path
    output_dir = r"C:\Users\jaysh\Documents\input"   # Replace with your desired output directory

    # Split the audio into 10-second chunks
    split_audio_to_mono(input_file, output_dir, chunk_length_ms=10000)  # 10,000 ms = 10 seconds
