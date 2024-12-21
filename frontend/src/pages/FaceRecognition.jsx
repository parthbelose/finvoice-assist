import React, { useRef, useEffect, useState } from "react";
import * as faceapi from "face-api.js";

const FaceRecognition = () => {
  const videoRef = useRef(null);
  const [modelsLoaded, setModelsLoaded] = useState(false);
  const [status, setStatus] = useState("Initializing...");

  // Example preloaded embeddings (replace these with real data)
  const storedDescriptors = [
    new faceapi.LabeledFaceDescriptors("John Doe", [
      new Float32Array([/* Face descriptor array for John Doe */]),
    ]),
  ];

  useEffect(() => {
    const loadModels = async () => {
      const MODEL_URL = "/models";
      await faceapi.nets.ssdMobilenetv1.loadFromUri(MODEL_URL);
      await faceapi.nets.faceLandmark68Net.loadFromUri(MODEL_URL);
      await faceapi.nets.faceRecognitionNet.loadFromUri(MODEL_URL);
      setModelsLoaded(true);
    };

    loadModels();
  }, []);

  useEffect(() => {
    const startVideo = async () => {
      if (!modelsLoaded) return;

      try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: true });
        videoRef.current.srcObject = stream;
      } catch (error) {
        console.error("Error accessing webcam:", error);
      }
    };

    startVideo();
  }, [modelsLoaded]);

  const handleFaceRecognition = async () => {
    if (!videoRef.current) return;

    const video = videoRef.current;
    setStatus("Detecting...");

    const detection = await faceapi
      .detectSingleFace(video)
      .withFaceLandmarks()
      .withFaceDescriptor();

    if (!detection) {
      setStatus("No face detected. Try again.");
      return;
    }

    const faceMatcher = new faceapi.FaceMatcher(storedDescriptors);
    const bestMatch = faceMatcher.findBestMatch(detection.descriptor);

    setStatus(bestMatch.toString());
  };

  return (
    <div style={styles.container}>
      <h1>Face Recognition</h1>
      <video ref={videoRef} autoPlay muted style={styles.video}></video>
      <button
        onClick={handleFaceRecognition}
        style={styles.button}
        disabled={!modelsLoaded}
      >
        {modelsLoaded ? "Recognize Face" : "Loading Models..."}
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
  },
  video: {
    width: "320px",
    height: "240px",
    border: "2px solid #333",
    marginTop: "20px",
  },
  button: {
    marginTop: "20px",
    padding: "10px 20px",
    fontSize: "16px",
  },
  status: {
    marginTop: "20px",
    fontSize: "18px",
    color: "green",
  },
};

export default FaceRecognition;
