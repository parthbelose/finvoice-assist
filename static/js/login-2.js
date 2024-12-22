const video = document.getElementById('video');

// Load face-api models when the page loads
Promise.all([
  faceapi.nets.tinyFaceDetector.loadFromUri('/static/models'),
  faceapi.nets.faceLandmark68Net.loadFromUri('/static/models'),
  faceapi.nets.faceRecognitionNet.loadFromUri('/static/models')
]).then(startVideo).catch((err) => {
  console.error("Error loading models:", err);
});

// Start webcam video stream immediately
function startVideo() 
{
  if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
    navigator.mediaDevices.getUserMedia({ video: true })
      .then((stream) => {
        video.srcObject = stream;
      })
      .catch((err) => {
        console.error("Error accessing the webcam:", err);
        alert("Unable to access the webcam. Please make sure the camera is connected and permissions are granted.");
      });
  } else {
    alert("Your browser does not support webcam access.");
  }

  // After video is playing, we start speech recognition
  video.addEventListener('play', setupSpeechRecognition);
}

// Function to handle voice commands
function setupSpeechRecognition() {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SpeechRecognition) {
    alert("Speech recognition is not supported in this browser.");
    return;
  }

  const recognition = new SpeechRecognition();
  recognition.lang = 'en-US';
  recognition.interimResults = false;

  recognition.addEventListener('result', async (event) => {
    const command = event.results[0][0].transcript.trim().toUpperCase();
    if (command === "CAPTURE") {
      console.log("CAPTURE command received. Starting face recognition...");
      await captureEmbedding();  // Start face recognition when "CAPTURE" is said
    }
  });

  recognition.addEventListener('end', () => recognition.start()); // Keep recognition active
  recognition.start();
}

// Capture face embedding function
// Capture face embedding function
async function captureEmbedding() {
  const detections = await faceapi
    .detectAllFaces(video, new faceapi.TinyFaceDetectorOptions())
    .withFaceLandmarks()
    .withFaceDescriptors();

  if (detections.length > 0) {
    const embedding = Array.from(detections[0].descriptor); // Take first detected face
    console.log("Embedding captured:", embedding);
    
    // Send captured embedding to the backend for verification
    await verifyUser(embedding);

    document.getElementById('resultMessage').innerText = "Face captured successfully!";
  } else {
    console.log("No face detected. Please try again.");
    document.getElementById('resultMessage').innerText = "No face detected. Please try again.";
  }
}

// Function to verify user using backend
async function verifyUser(embedding) {
  const userName = document.getElementById('user_name').value.trim();
  const password = document.getElementById('password').value.trim();

  if (!userName) {
    alert("Please enter both username and password.");
    return;
  }

  const payload = {
    user_name: userName,
    // password: password,
    embedding: embedding,
  };

  try {
    const response = await fetch('http://127.0.0.1:5000/verify_face', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    });

    const data = await response.json();
    if (data.success) {
      console.log(data);
      document.getElementById('resultMessage').innerText = `Login successful for user: ${data.user_name}`;
      const userId = localStorage.setItem('user_id',data._id);
      window.location.href="http://127.0.0.1:5000/home"
    } else {
      console.log(data.message);
      document.getElementById('resultMessage').innerText = `Error: ${data.message}`;
    }
  } catch (error) {
    console.error('Error during verification:', error);
    document.getElementById('resultMessage').innerText = `Error during verification.`;
  }
}

// Display face detection results on the video
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

