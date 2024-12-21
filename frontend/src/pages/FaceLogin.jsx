import React, { useRef, useEffect, useState } from "react";
import * as faceapi from "face-api.js";

const FaceLogin = () => {
  const videoRef = useRef(null);
  const [status, setStatus] = useState("Initializing...");
  const [modelsLoaded, setModelsLoaded] = useState(false);

  // Preloaded known face descriptors (replace with real data in production)
  const storedDescriptors = [
    // Example: new faceapi.LabeledFaceDescriptors("User1", [descriptor])
  ];

  // Load Face API.js models
  useEffect(() => {
    const loadModels = async () => {
      const MODEL_URL = "/models"; // Path to your models folder
      await faceapi.nets.ssdMobilenetv1.loadFromUri(MODEL_URL);
      await faceapi.nets.faceLandmark68Net.loadFromUri(MODEL_URL);
      await faceapi.nets.faceRecognitionNet.loadFromUri(MODEL_URL);
      setModelsLoaded(true);
    };

    loadModels();
  }, []);

  // Start the webcam
  useEffect(() => {
    const startVideo = async () => {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: true });
        videoRef.current.srcObject = stream;
      } catch (error) {
        console.error("Error accessing webcam:", error);
        setStatus("Error accessing webcam");
      }
    };

    if (modelsLoaded) {
      startVideo();
    }
  }, [modelsLoaded]);

  // Handle face recognition
  const handleLogin = async () => {
    setStatus("Analyzing face...");
    const video = videoRef.current;

    const detections = await faceapi
      .detectSingleFace(video)
      .withFaceLandmarks()
      .withFaceDescriptor();

    if (!detections) {
      setStatus("No face detected. Please try again.");
      return;
    }

    if (storedDescriptors.length === 0) {
      setStatus("No registered faces. Please set up descriptors.");
      return;
    }

    const faceMatcher = new faceapi.FaceMatcher(storedDescriptors);
    const bestMatch = faceMatcher.findBestMatch(detections.descriptor);

    if (bestMatch.label !== "unknown") {
      setStatus("Login successful!");
      setTimeout(() => {
        window.location.href = "/home"; // Redirect to home page
      }, 2000);
    } else {
      setStatus("Face not recognized. Try again.");
    }
  };

  return (
    <div style={styles.container}>
      <h1>Face Login</h1>
      <video
        ref={videoRef}
        autoPlay
        muted
        style={styles.video}
      ></video>
      <button
        onClick={handleLogin}
        style={styles.button}
        disabled={!modelsLoaded}
      >
        {modelsLoaded ? "Start Login" : "Loading Models..."}
      </button>
      <p style={styles.status}>{status}</p>
    </div>
  );
};

const styles = {
  container: {
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    justifyContent: "center",
    height: "100vh",
    fontFamily: "Arial, sans-serif",
  },
  video: {
    border: "2px solid #333",
    marginTop: 20,
    width: 320,
    height: 240,
  },
  button: {
    marginTop: 20,
    padding: "10px 20px",
    fontSize: 16,
    cursor: "pointer",
  },
  status: {
    marginTop: 20,
    fontWeight: "bold",
    color: "green",
  },
};

export default FaceLogin;
