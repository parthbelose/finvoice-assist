const video = document.getElementById('video');

Promise.all([
  faceapi.nets.tinyFaceDetector.loadFromUri('/static/models'),
  faceapi.nets.faceLandmark68Net.loadFromUri('/static/models'),
  faceapi.nets.faceRecognitionNet.loadFromUri('/static/models'),
]).then(startVideo);

function startVideo() {
  navigator.getUserMedia(
    { video: {} },
    stream => video.srcObject = stream,
    err => console.error(err)
  );
}

// Function to handle voice commands
function setupSpeechRecognition() {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  const recognition = new SpeechRecognition();
  recognition.lang = 'en-US';
  recognition.interimResults = false;

  recognition.addEventListener('result', async (event) => {
    const command = event.results[0][0].transcript.trim().toUpperCase();
    console.log(command);
    if (command === "CAPTURE") {
      console.log("CAPTURE command received. Processing...");
      await captureEmbedding();
    }
  });

  recognition.addEventListener('end', () => recognition.start()); // Keep the recognition active
  recognition.start();
}

async function captureEmbedding() {
  const detections = await faceapi
    .detectAllFaces(video, new faceapi.TinyFaceDetectorOptions())
    .withFaceLandmarks()
    .withFaceDescriptors(); // Compute embeddings

  if (detections.length > 0) {
    const embedding = Array.from(detections[0].descriptor); // Take the first detected face
    console.log("Embedding captured:", embedding);

    // Send embedding to the backend
    const response = await fetch('http://localhost:5000/signup', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        user_name: document.getElementById('user_name').value,
        password: document.getElementById('password').value,
        embedding
      })
    });

    if (response.ok) {
      console.log("Embedding saved successfully!");
      const result = await response.json();
      document.getElementById('resultMessage').textContent = result.message;
      // Only store the user ID if it has not been stored before
      if (!localStorage.getItem('user_id')) {
        localStorage.setItem('user_id', data.user_id);
      }
      window.location.href ="http://127.0.0.1:5000/home";
    } else {
      console.error("Error saving embedding:", await response.text());
      document.getElementById('resultMessage').textContent = "Error during signup. Please try again.";
    }
  } else {
    console.log("No face detected. Please try again.");
    document.getElementById('resultMessage').textContent = "No face detected. Please ensure your face is visible.";
  }
}

video.addEventListener('play', () => {
  const canvas = faceapi.createCanvasFromMedia(video);
  document.body.append(canvas);
  const displaySize = { width: video.width, height: video.height };
  faceapi.matchDimensions(canvas, displaySize);

  setInterval(async () => {
    const detections = await faceapi
      .detectAllFaces(video, new faceapi.TinyFaceDetectorOptions())
      .withFaceLandmarks();

    const resizedDetections = faceapi.resizeResults(detections, displaySize);
    canvas.getContext('2d').clearRect(0, 0, canvas.width, canvas.height);

    faceapi.draw.drawDetections(canvas, resizedDetections);
    faceapi.draw.drawFaceLandmarks(canvas, resizedDetections);
  }, 100);
});

// Start speech recognition
setupSpeechRecognition();
