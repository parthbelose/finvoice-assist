import React, { useEffect } from "react";
import SpeechRecognition, { useSpeechRecognition } from "react-speech-recognition";

const Dictaphone = () => {
  const {
    transcript,
    listening,
    resetTranscript,
    browserSupportsSpeechRecognition,
  } = useSpeechRecognition();

  // Function to make the browser speak the transcript
  const speak = (text) => {
    const speech = new SpeechSynthesisUtterance(text);
    window.speechSynthesis.speak(speech);
  };

  // Automatically repeat the transcript when it updates
  useEffect(() => {
    if (transcript) {
      speak(transcript);
    }
  }, [transcript]);

  if (!browserSupportsSpeechRecognition) {
    return <span>Browser doesn't support speech recognition.</span>;
  }

  return (
    <div style={{ padding: "20px", textAlign: "center" }}>
      <p>Microphone: {listening ? "on" : "off"}</p>
      <button onClick={SpeechRecognition.startListening} style={{ marginRight: "10px" }}>
        Start
      </button>
      <button onClick={SpeechRecognition.stopListening} style={{ marginRight: "10px" }}>
        Stop
      </button>
      <button onClick={resetTranscript}>Reset</button>
      <p style={{ marginTop: "20px", fontSize: "18px" }}>
        <strong>Transcript:</strong> {transcript}
      </p>
    </div>
  );
};

export default Dictaphone;
