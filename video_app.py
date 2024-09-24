from fastapi import FastAPI

# Create a FastAPI app instance
app = FastAPI()

# Simple root endpoint for testing
@app.get("/")
def read_root():
    return {"message": "Video processing API is running on port 8080!"}

# Another sample endpoint
@app.get("/process_video")
def process_video():
    return {"status": "Processing video..."}

# The app will run on port 8080 when executed with the following command:
# uvicorn video_app:app --host=0.0.0.0 --port=8080
