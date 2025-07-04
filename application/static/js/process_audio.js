const startButton = document.getElementById('startButton');
    const stopButton = document.getElementById('stopButton');
    const statusDiv = document.getElementById('status');
    const resultsDiv = document.getElementById('results');
    const evalDiv = document.getElementById('eval');
    const bodyElm = document.body;

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
            startButton.style.display = 'none'
            stopButton.style.display = 'block'

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
                startButton.style.display = 'block'
                stopButton.style.display = 'none'

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
                        } else if (score >= 150){ // Example threshold
                            evalMessage = 'Likely illegal trap detected';
                            bodyElm.style.setProperty('background', 'var(--bg-gradient)', 'important');
                        } else {
                            evalMessage = 'Uncertain!';
                        }

                        evalDiv.textContent = evalMessage;

                    } else {
                        statusDiv.textContent = `Status: Error ${response.status} - ${result.detail || response.statusText}`;
                        resultsDiv.textContent = JSON.stringify(result, null, 2); // Show error detail JSON
                    }
                    resultsDiv.style.display = 'none';
                    console.log("Server Response:", result);

                } catch (error) {
                    statusDiv.textContent = 'Status: Upload failed. Network or server error.';
                    resultsDiv.textContent = `Workspace Error: ${error.message}`;
                    resultsDiv.style.display = 'block';
                    console.error("Fetch Error:", error);
                } finally {
                     startButton.disabled = false; stopButton.disabled = true; // Ensure reset
                    startButton.style.display = 'block'
                    stopButton.style.display = 'none'
                }
            }; // end of onstop

            mediaRecorder.onerror = (event) => {
                 console.error("MediaRecorder error:", event.error);
                 statusDiv.textContent = `Status: Recording Error - ${event.error.name}`;
                 alert(`Recording Error: ${event.error.name}`);
                 startButton.disabled = false; stopButton.disabled = true;
                 startButton.style.display = 'block'
                 stopButton.style.display = 'none'
                 if (audioStream) { audioStream.getTracks().forEach(track => track.stop()); }
            }

            mediaRecorder.start();

        } catch (err) {
            console.error("Error getting user media:", err);
            statusDiv.textContent = `Status: Error - ${err.message}`;
            alert(`Error accessing microphone: ${err.message} \n(Remember to use HTTPS or localhost)`);
            startButton.disabled = false; stopButton.disabled = true;
            startButton.style.display = 'block'
            stopButton.style.display = 'none'
        }
    }; // end of startButton.onclick

    stopButton.onclick = () => {
        if (mediaRecorder && mediaRecorder.state === "recording") {
            statusDiv.textContent = 'Status: Stopping recording...';
            mediaRecorder.stop();
        }
    }; // end of stopButton.onclick