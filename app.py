import tempfile
import io
import os
from pydub import AudioSegment # For conversion
from pydub.exceptions import CouldntDecodeError

from http.client import HTTPException

import uvicorn
from starlette.responses import HTMLResponse
from fastapi import FastAPI, File, UploadFile
from starlette.responses import JSONResponse

from fingerprinting import endpoint_detection_app

app = FastAPI()

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

    # --- Corrected Exception Handling ---
    except HTTPException as http_exc:
        # Re-raise HTTPExceptions directly (already handled)
        print(f"Caught HTTPException: {http_exc.status_code} - {http_exc.detail}")
        raise http_exc
    except Exception as e:
        # Catch other unexpected errors
        print(f"Unhandled error processing audio: {e}")
        # import traceback
        # print(traceback.format_exc()) # Useful for debugging
        # Raise a generic 500 error
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

    finally:
        # 8. Clean up: Ensure the temporary WAV file is deleted
        if temp_wav_path and os.path.exists(temp_wav_path):
            try:
                os.remove(temp_wav_path)
                print(f"Cleaned up temporary file: {temp_wav_path}")
            except OSError as cleanup_err:
                print(f"Error cleaning up temporary file {temp_wav_path}: {cleanup_err}")
        # Ensure the original upload file object is closed
        if audio_file:
            await audio_file.close()
            print("UploadFile closed.")



@app.get('/', response_class=HTMLResponse)
async def read_html_root():
    # --- HTML + JavaScript (No changes needed here from the previous version) ---
    # (Same HTML/JS as before)
    html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Audio Recorder (Server Processing)</title>
    <style>
        body { font-family: sans-serif; }
        #status { margin-top: 15px; font-weight: bold; }
        #results { margin-top: 10px; padding: 10px; border: 1px solid #ccc; background-color: #f9f9f9; white-space: pre-wrap; font-family: monospace;}
    </style>
</head>
<body>

    <h1>Record Audio and Process on Server</h1>

    <button id="startButton">Start Recording</button>
    <button id="stopButton" disabled>Stop Recording</button>

    <div id="status">Status: Ready</div>
    <div id="eval">Score</div>
    <div id="results" style="display: none;"></div>

    <script>
        const startButton = document.getElementById('startButton');
        const stopButton = document.getElementById('stopButton');
        const statusDiv = document.getElementById('status');
        const resultsDiv = document.getElementById('results');
        const evalDiv = document.getElementById('eval');

        let mediaRecorder;
        let audioChunks = [];
        let audioStream; // To keep track of the stream

        startButton.onclick = async () => {
            resultsDiv.style.display = 'none'; // Hide previous results
            resultsDiv.textContent = '';
            statusDiv.textContent = 'Status: Requesting microphone access...';

            try {
                audioStream = await navigator.mediaDevices.getUserMedia({ audio: true });
                startButton.disabled = true;
                stopButton.disabled = false;
                statusDiv.textContent = 'Status: Recording...';
                audioChunks = []; // Reset chunks for new recording

                // --- Determine mimeType ---
                const mimeTypes = [
                    'audio/webm;codecs=opus', 'audio/ogg;codecs=opus', 'audio/webm', 'audio/ogg',
                    'audio/mp4', 'audio/aac' // Less common for raw recording
                ];
                const supportedMimeType = mimeTypes.find(type => MediaRecorder.isTypeSupported(type));
                console.log("Using MIME Type:", supportedMimeType || 'default (likely audio/webm)');
                // -------------------------

                mediaRecorder = new MediaRecorder(audioStream, { mimeType: supportedMimeType });

                mediaRecorder.ondataavailable = event => {
                    if (event.data.size > 0) { audioChunks.push(event.data); }
                };

                mediaRecorder.onstop = async () => {
                    statusDiv.textContent = 'Status: Recording stopped. Preparing upload...';
                    const mimeType = mediaRecorder.mimeType || 'audio/webm';
                    const audioBlob = new Blob(audioChunks, { type: mimeType });

                    let ext = 'bin'; // fallback
                    if (mimeType.includes('webm')) ext = 'webm';
                    else if (mimeType.includes('ogg')) ext = 'ogg';
                    else if (mimeType.includes('mp4')) ext = 'mp4';
                    else if (mimeType.includes('aac')) ext = 'aac';
                    const filename = `recording_${Date.now()}.${ext}`;

                    if (audioStream) { audioStream.getTracks().forEach(track => track.stop()); console.log("Microphone tracks stopped."); }

                    startButton.disabled = false; stopButton.disabled = true;

                    // --- Send data to backend ---
                    const formData = new FormData();
                    formData.append('audio_file', audioBlob, filename);

                    statusDiv.textContent = `Status: Uploading ${filename}...`;

                    try {
                        const response = await fetch('/api/process-audio/', { method: 'POST', body: formData });
                        const result = await response.json(); // Always expect JSON now

                        if (response.ok) {
                            statusDiv.textContent = 'Status: Upload successful. Processing complete.';
                            resultsDiv.textContent = JSON.stringify(result, null, 2);
                            const score = result.processing_result.score;
                            
                            if (score === null || typeof score === 'undefined') {
                                 evalMessage = 'Score not available.';
                            } else if (score < 30) { // Example threshold
                                evalMessage = 'No match found!';
                            } else if (score >= 30){ // Example threshold
                                evalMessage = 'Likely illegal trap detected';
                            }
                            
                            evalDiv.textContent = evalMessage;
                            
                        } else {
                            statusDiv.textContent = `Status: Error ${response.status} - ${result.detail || response.statusText}`;
                            resultsDiv.textContent = JSON.stringify(result, null, 2); // Show error detail JSON
                        }
                        resultsDiv.style.display = 'block';
                        console.log("Server Response:", result);

                    } catch (error) {
                        statusDiv.textContent = 'Status: Upload failed. Network or server error.';
                        resultsDiv.textContent = `Workspace Error: ${error.message}`;
                        resultsDiv.style.display = 'block';
                        console.error("Fetch Error:", error);
                    } finally {
                         startButton.disabled = false; stopButton.disabled = true; // Ensure reset
                    }
                }; // end of onstop

                mediaRecorder.onerror = (event) => {
                     console.error("MediaRecorder error:", event.error);
                     statusDiv.textContent = `Status: Recording Error - ${event.error.name}`;
                     alert(`Recording Error: ${event.error.name}`);
                     startButton.disabled = false; stopButton.disabled = true;
                     if (audioStream) { audioStream.getTracks().forEach(track => track.stop()); }
                }

                mediaRecorder.start();

            } catch (err) {
                console.error("Error getting user media:", err);
                statusDiv.textContent = `Status: Error - ${err.message}`;
                alert(`Error accessing microphone: ${err.message} \n(Remember to use HTTPS or localhost)`);
                startButton.disabled = false; stopButton.disabled = true;
            }
        }; // end of startButton.onclick

        stopButton.onclick = () => {
            if (mediaRecorder && mediaRecorder.state === "recording") {
                statusDiv.textContent = 'Status: Stopping recording...';
                mediaRecorder.stop();
            }
        }; // end of stopButton.onclick

    </script>

</body>
</html>
        """
    return HTMLResponse(content=html_content, status_code=200)


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8800)