import React, { useRef, useEffect, useState } from "react";
import * as faceapi from "face-api.js";

const PrintEmbeddings = () => {
  const videoRef = useRef(null);
  const [modelsLoaded, setModelsLoaded] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");

  // Load models on component mount
  useEffect(() => {
    const loadModels = async () => {
      try {
        const MODEL_URL = "/models"; // Path to the models folder in your public directory
        await faceapi.nets.ssdMobilenetv1.loadFromUri(MODEL_URL);
        await faceapi.nets.faceLandmark68Net.loadFromUri(MODEL_URL);
        await faceapi.nets.faceRecognitionNet.loadFromUri(MODEL_URL);
        setModelsLoaded(true);
      } catch (error) {
        setErrorMessage("Failed to load models. Please check the path or your network connection.");
        console.error("Error loading models:", error);
      }
    };

    loadModels();
  }, []);

  // Start webcam once models are loaded
  useEffect(() => {
    const startVideo = async () => {
      if (!modelsLoaded || !navigator.mediaDevices?.getUserMedia) {
        setErrorMessage("Webcam access is not supported on this browser.");
        return;
      }

      try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: true });
        videoRef.current.srcObject = stream;
      } catch (error) {
        setErrorMessage("Error accessing webcam. Please allow webcam access.");
        console.error("Error accessing webcam:", error);
      }
    };

    startVideo();

    // Cleanup the video stream when component unmounts
    return () => {
      if (videoRef.current?.srcObject) {
        const tracks = videoRef.current.srcObject.getTracks();
        tracks.forEach((track) => track.stop());
      }
    };
  }, [modelsLoaded]);

  // Capture and print embeddings
  const handlePrintEmbeddings = async () => {
    if (!videoRef.current) return;

    try {
      const video = videoRef.current;
      const detection = await faceapi
        .detectSingleFace(video)
        .withFaceLandmarks()
        .withFaceDescriptor();

      if (!detection) {
        setErrorMessage("No face detected. Please ensure your face is in the frame.");
        return;
      }

      setErrorMessage("");
      console.log("Face Embeddings (Descriptor):", detection.descriptor);
    } catch (error) {
      setErrorMessage("Error during face detection. Please try again.");
      console.error("Error detecting face:", error);
    }
  };

  return (
    <div style={styles.container}>
      <h1>Print Face Embeddings</h1>
      {errorMessage && <p style={styles.error}>{errorMessage}</p>}
      <video ref={videoRef} autoPlay muted style={styles.video}></video>
      <button
        onClick={handlePrintEmbeddings}
        style={styles.button}
        disabled={!modelsLoaded}
      >
        {modelsLoaded ? "Print Embeddings" : "Loading Models..."}
      </button>
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
    width: "320px",
    height: "240px",
    border: "2px solid #333",
    marginTop: "20px",
  },
  button: {
    marginTop: "20px",
    padding: "10px 20px",
    fontSize: "16px",
    cursor: "pointer",
    backgroundColor: "#007BFF",
    color: "#fff",
    border: "none",
    borderRadius: "5px",
  },
  error: {
    color: "red",
    marginBottom: "20px",
  },
};

export default PrintEmbeddings;
