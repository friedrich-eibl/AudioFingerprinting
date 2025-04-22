import tempfile
import io
import os
from pathlib import Path
from pydub import AudioSegment # For conversion
from pydub.exceptions import CouldntDecodeError

from http.client import HTTPException

import uvicorn
from starlette.responses import HTMLResponse
from fastapi import FastAPI, File, UploadFile
from starlette.responses import JSONResponse
from starlette.staticfiles import StaticFiles

from fingerprinting import endpoint_detection_app

app = FastAPI()
BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get('/api/')
async def read_root():
    return {'message': 'Hello World'}


@app.post("/api/process-audio/")
# Renamed function slightly to avoid confusion with the previous attempt
async def process_audio_upload_convert(audio_file: UploadFile = File(...)) -> JSONResponse:
    """
    Receives uploaded audio, converts to WAV, generates spectrogram from WAV path.
    """
    print(f"Received upload: {audio_file.filename}, content_type: {audio_file.content_type}")
    temp_wav_path = None # Initialize path variable

    try:
        # 1. Read uploaded audio bytes
        audio_bytes = await audio_file.read()
        if not audio_bytes:
            raise HTTPException(status_code=400, detail="No audio data received.")

        # 2. Use Pydub to load audio from bytes
        audio_stream = io.BytesIO(audio_bytes)
        try:
            print("Loading audio bytes with Pydub...")
            audio_segment = AudioSegment.from_file(audio_stream)
            print(f"Pydub loaded audio: {audio_segment.duration_seconds}s, {audio_segment.frame_rate}Hz, {audio_segment.channels}ch")
        except CouldntDecodeError as decode_err:
             print(f"Pydub decode error: {decode_err}. Is ffmpeg installed?")
             raise HTTPException(status_code=400, detail=f"Cannot decode uploaded audio format ({audio_file.content_type}). Error: {decode_err}")
        except Exception as pydub_err:
            print(f"Error loading audio with Pydub: {pydub_err}")
            raise HTTPException(status_code=500, detail=f"Server error processing audio with Pydub: {pydub_err}")

        # 3. Create a temporary file path for the WAV output
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_wav_file:
            temp_wav_path = temp_wav_file.name
        print(f"Created temporary WAV path: {temp_wav_path}")

        # 4. Export the audio segment to the temporary WAV file
        try:
            print(f"Exporting to WAV: {temp_wav_path}")
            # Export as WAV (generally safer for processing than MP3)
            audio_segment.export(temp_wav_path, format="wav")
            print("WAV export complete.")
        except Exception as export_err:
            print(f"Error exporting to WAV: {export_err}")
            raise HTTPException(status_code=500, detail=f"Server error converting audio to WAV: {export_err}")

        # 5. Call your function with the temporary WAV path
        print(f"Calling generate_spectrogram with path: {temp_wav_path}")
        # Make sure generate_spectogram expects a path string here
        match_name, score = endpoint_detection_app(temp_wav_path)

        # 6. Process the results
        result_data = {
            "message": "Spectrogram generated successfully from converted WAV.",
            "closest_match": match_name,
            "score": score,
        }
        print(f"Spectrogram processing complete. Result data: {result_data}")

        # 7. Return success response
        return JSONResponse(content={
            "status": "success",
            "filename": audio_file.filename,
            "original_content_type": audio_file.content_type,
            "processing_result": result_data
        })

    except HTTPException as http_exc:
        # Re-raise HTTPExceptions directly (already handled)
        print(f"Caught HTTPException: {http_exc.status_code} - {http_exc.detail}")
        raise http_exc
    except Exception as e:
        print(f"Unhandled error processing audio: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

    finally:
        # 8. Clean up: Ensure the temporary WAV file is deleted
        if temp_wav_path and os.path.exists(temp_wav_path):
            try:
                os.remove(temp_wav_path)
                print(f"Cleaned up temporary file: {temp_wav_path}")
            except OSError as cleanup_err:
                print(f"Error cleaning up temporary file {temp_wav_path}: {cleanup_err}")

        if audio_file:
            await audio_file.close()
            print("UploadFile closed.")


@app.get('/', response_class=HTMLResponse)
async def read_html_root():
    html_file_path = BASE_DIR / "templates/index.html"
    try:
        with open(html_file_path, "r", encoding="utf-8") as f:
            html_content = f.read()
        return HTMLResponse(content=html_content, status_code=200)
    except FileNotFoundError:
        return HTMLResponse(content="<h1>Error: index.html not found</h1>", status_code=500)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8800)