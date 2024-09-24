import os
import cv2
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from basicsr.archs.rrdbnet_arch import RRDBNet
from basicsr.utils.download_util import load_file_from_url
from realesrgan import RealESRGANer
from tqdm import tqdm
import torch
from pathlib import Path
import uvicorn

app = FastAPI()

# Define the fixed directories
BASE_DIR = Path("/app/Documents/temp/Video")
INPUT_DIR = BASE_DIR / "input"
INPUT_CHUNKS_DIR = BASE_DIR / "temp_input"
OUTPUT_CHUNKS_DIR = BASE_DIR / "temp_output"
FINAL_OUTPUT_DIR = BASE_DIR / "final_output"

# Ensure all directories exist
for dir_path in [INPUT_DIR, INPUT_CHUNKS_DIR, OUTPUT_CHUNKS_DIR, FINAL_OUTPUT_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

# FastAPI request body model to accept the request (no tilesize or scale required in the request)
class EnhanceRequest(BaseModel):
    pass  # No parameters needed in the request for now


def extract_frames(input_video_path, frames_dir):
    """Extract frames from the video and save them to frames_dir, skipping already existing frames."""
    if not os.path.exists(frames_dir):
        os.makedirs(frames_dir)
        print(f"Directory {frames_dir} created.")

    # List all already existing frame files in the directory
    existing_frames = sorted([f for f in os.listdir(frames_dir) if f.endswith('.png')])
    existing_frame_count = len(existing_frames)
    
    # If frames already exist, skip processing those frames
    cap = cv2.VideoCapture(str(input_video_path))
    if not cap.isOpened():
        raise HTTPException(status_code=500, detail=f"Error opening video file {input_video_path}")

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    # Continue from the next frame if some frames are already present
    frame_idx = existing_frame_count

    with tqdm(total=total_frames, initial=existing_frame_count, desc="Extracting Video Frames") as pbar:
        while cap.isOpened() and frame_idx < total_frames:
            ret, frame = cap.read()
            if not ret:
                break

            # Skip frames that have already been extracted
            frame_path = os.path.join(frames_dir, f"frame_{frame_idx:06d}.png")
            if not os.path.exists(frame_path):
                cv2.imwrite(frame_path, frame)

            frame_idx += 1
            pbar.update(1)

    cap.release()
    return total_frames



def enhance_frame(upsampler, frame):
    """Enhance a single frame using Real-ESRGAN."""
    try:
        output, _ = upsampler.enhance(frame, outscale=2)  # Hardcoded scale
        return output
    except RuntimeError as error:
        print(f"Error: {error}")
        return frame


def enhance_frames(frames_dir, output_dir, upsampler):
    """Enhance extracted frames."""
    os.makedirs(output_dir, exist_ok=True)
    frame_paths = sorted([os.path.join(frames_dir, f) for f in os.listdir(frames_dir) if f.endswith('.png')])
    
    with tqdm(total=len(frame_paths), desc="Enhancing Frames") as pbar:
        for frame_path in frame_paths:
            frame = cv2.imread(frame_path)
            enhanced_frame = enhance_frame(upsampler, frame)
            frame_name = os.path.basename(frame_path)
            enhanced_frame_path = os.path.join(output_dir, frame_name)
            cv2.imwrite(enhanced_frame_path, enhanced_frame)
            pbar.update(1)


def combine_frames_to_video(frames_dir, output_video_path, fps=30):
    """Combine the frames in frames_dir back into a video."""
    frame_paths = sorted([os.path.join(frames_dir, f) for f in os.listdir(frames_dir) if f.endswith('.png')])
    if not frame_paths:
        raise HTTPException(status_code=500, detail="No frames found to combine into video")

    first_frame = cv2.imread(frame_paths[0])
    height, width, layers = first_frame.shape
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    video = cv2.VideoWriter(output_video_path, fourcc, fps, (width, height))

    for frame_path in frame_paths:
        frame = cv2.imread(frame_path)
        video.write(frame)

    video.release()
    print(f"Video saved at {output_video_path}")


@app.post("/process_video")
async def process_video(request: EnhanceRequest):
    # Path to input video
    video_files = list(INPUT_DIR.glob("*.mp4"))
    if not video_files:
        raise HTTPException(status_code=404, detail="No video file found in input directory")

    input_video_path = video_files[0]  # Assuming one video file in the input directory

    # Ensure the directories exist
    INPUT_CHUNKS_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_CHUNKS_DIR.mkdir(parents=True, exist_ok=True)
    FINAL_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Step 1: Extract frames from the video
    extract_frames(input_video_path, str(INPUT_CHUNKS_DIR))

    # Step 2: Initialize Real-ESRGAN model
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = RRDBNet(num_in_ch=3, num_out_ch=3, num_feat=64, num_block=23, num_grow_ch=32, scale=4)
    
    file_url = ['https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/RealESRGAN_x4plus.pth']
    
    # Updated model path for Docker-mounted directory
    model_path = '/app/weights/RealESRGAN_x4plus.pth'
    if not os.path.isfile(model_path):
        model_path = load_file_from_url(url=file_url[0], model_dir=os.path.join('weights'), progress=True)

    # Correct scale value based on the model
    netscale = 4  # RealESRGAN_x4plus uses a scale of 4

    # Initialize the Real-ESRGAN model
    upsampler = RealESRGANer(
        scale=netscale,  # Use the correct scale (4 in this case)
        model_path=model_path,
        model=model,
        tile=400,  # Default tile size
        tile_pad=10,
        pre_pad=0,
        half=True if device.type == 'cuda' else False
    )

    # Step 3: Enhance frames (with skipping already processed frames)
    def enhance_frames(frames_dir, output_dir, upsampler):
        """Enhance extracted frames, skipping those already processed."""
        os.makedirs(output_dir, exist_ok=True)
        
        # Get a sorted list of frames in the input directory
        frame_paths = sorted([os.path.join(frames_dir, f) for f in os.listdir(frames_dir) if f.endswith('.png')])
        
        with tqdm(total=len(frame_paths), desc="Enhancing Frames") as pbar:
            for frame_path in frame_paths:
                frame_name = os.path.basename(frame_path)
                enhanced_frame_path = os.path.join(output_dir, frame_name)

                # Skip enhancing this frame if it's already processed
                if os.path.exists(enhanced_frame_path):
                    print(f"Skipping already processed frame: {frame_name}")
                    pbar.update(1)
                    continue

                # Otherwise, enhance the frame
                frame = cv2.imread(frame_path)
                enhanced_frame = enhance_frame(upsampler, frame)
                cv2.imwrite(enhanced_frame_path, enhanced_frame)
                pbar.update(1)

    enhance_frames(str(INPUT_CHUNKS_DIR), str(OUTPUT_CHUNKS_DIR), upsampler)

    # Step 4: Combine the enhanced frames into a video
    final_output_path = str(FINAL_OUTPUT_DIR / "enhanced_video.mp4")
    combine_frames_to_video(str(OUTPUT_CHUNKS_DIR), final_output_path)

    return {"status": "Video processing completed", "output": final_output_path}



if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8080)
