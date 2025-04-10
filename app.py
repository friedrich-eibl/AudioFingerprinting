from fastapi import FastAPI
import uvicorn
from starlette.responses import HTMLResponse

app = FastAPI()

@app.get('/api/')
async def read_root():
    return {'message': 'Hello World'}

@app.get('/', response_class=HTMLResponse)
async def read_root():
    html_content = """
        <!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Basic Audio Recorder (Download Only)</title>
</head>
<body>

    <h1>Record and Download Audio</h1>

    <button id="startButton">Start Recording</button>
    <button id="stopButton" disabled>Stop Recording</button>

    <hr>

    <a id="downloadLink" style="display: none;">Download Recording</a>

    <script>
        const startButton = document.getElementById('startButton');
        const stopButton = document.getElementById('stopButton');
        const downloadLink = document.getElementById('downloadLink');

        let mediaRecorder;
        let audioChunks = [];
        let audioStream; // To keep track of the stream

        startButton.onclick = async () => {
            // Hide previous download link if any
            downloadLink.style.display = 'none';
            downloadLink.href = ''; // Clear old URL

            try {
                audioStream = await navigator.mediaDevices.getUserMedia({ audio: true });
                startButton.disabled = true;
                stopButton.disabled = false;
                audioChunks = []; // Reset chunks for new recording

                mediaRecorder = new MediaRecorder(audioStream);

                mediaRecorder.ondataavailable = event => {
                    audioChunks.push(event.data);
                };

                mediaRecorder.onstop = () => {
                    const audioBlob = new Blob(audioChunks, { type: mediaRecorder.mimeType || 'audio/webm' });
                    const audioUrl = URL.createObjectURL(audioBlob);

                    // Setup the download link
                    downloadLink.href = audioUrl;
                    downloadLink.download = `recording_${Date.now()}.webm`; // Add timestamp for unique names
                    downloadLink.style.display = 'inline'; // Show download link

                    // Stop the microphone stream tracks
                    audioStream.getTracks().forEach(track => track.stop());

                    // Reset buttons
                    startButton.disabled = false;
                    stopButton.disabled = true;
                };

                mediaRecorder.onerror = (event) => {
                     console.error("MediaRecorder error:", event.error);
                     alert(`Recording Error: ${event.error.name}`);
                     startButton.disabled = false;
                     stopButton.disabled = true;
                     // Stop tracks on error too
                     if (audioStream) {
                         audioStream.getTracks().forEach(track => track.stop());
                     }
                }

                mediaRecorder.start();

            } catch (err) {
                console.error("Error getting user media:", err);
                alert(`Error accessing microphone: ${err.message} \n(Remember to use HTTPS or localhost)`);
                startButton.disabled = false; // Re-enable start if it failed
                stopButton.disabled = true;
            }
        };

        stopButton.onclick = () => {
            if (mediaRecorder && mediaRecorder.state === "recording") {
                mediaRecorder.stop();
                // UI updates (disabling stop, enabling start, showing link) are handled in onstop
            }
        };

    </script>

</body>
</html>
        """
    return HTMLResponse(content=html_content, status_code=200)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8800)