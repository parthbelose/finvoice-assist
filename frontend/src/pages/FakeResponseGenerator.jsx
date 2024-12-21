// import React, { useState, useEffect } from "react";
// import SpeechRecognition, { useSpeechRecognition } from "react-speech-recognition";
// import Speech from "react-text-to-speech";
// import axios from "axios";
// const FakeResponseGenerator = () => {
//   const [response, setResponse] = useState(""); // State to store the fake response
//   const [isListening, setIsListening] = useState(false); // State to toggle microphone
//   const [isResponding, setIsResponding] = useState(false); // State to indicate response generation
//   const [speakNow, setSpeakNow] = useState(false); // State to control automatic playback

//   // Predefined fake responses
//   const fakeResponses = [
//     "Sure, I can help you with that!",
//     "Let me think about it...",
//     "It might take some time, but I'll get it done.",
//     "I'm not sure, but I'll try my best.",
//     "This looks interesting, let me explore further.",
//     "That's a great idea, let's proceed!",
//     "I'm sorry, I cannot do that right now.",
//     "I need more information to provide an answer.",
//   ];

//   // Speech recognition hooks
//   const { transcript, listening, resetTranscript, browserSupportsSpeechRecognition } =
//     useSpeechRecognition();

//   // Function to generate a random fake response
//   const generateResponse = async () => {
//     const randomResponse = fakeResponses[Math.floor(Math.random() * fakeResponses.length)];
//     setResponse(randomResponse);
//     setIsResponding(true);
//     setSpeakNow(true); // Trigger response playback

//     // Automatically reset responding state after 10 seconds
//     setTimeout(() => setIsResponding(false), 10000);
    
//   };

//   // Automatically generate a response when the user stops speaking
//   useEffect(() => {
//     if (!listening && transcript) {
//       generateResponse();
//     }
//   }, [listening, transcript]);

//   // Toggle microphone state
//   const toggleMicrophone = () => {
//     if (isListening) {
//       SpeechRecognition.stopListening();
//       setIsListening(false);
//     } else {
//       resetTranscript();
//       SpeechRecognition.startListening({ continuous: false });
//       setIsListening(true);
//     }
//   };

//   // Bind Space key for toggling the microphone
//   useEffect(() => {
//     const handleKeyDown = (event) => {
//       if (event.code === "Space") {
//         toggleMicrophone();
//       }
//     };

//     window.addEventListener("keydown", handleKeyDown);
//     return () => window.removeEventListener("keydown", handleKeyDown);
//   }, [isListening]);

//   if (!browserSupportsSpeechRecognition) {
//     return <p>Your browser does not support speech recognition.</p>;
//   }

//   return (
//     <div style={{ padding: "20px", textAlign: "center" }}>
//       <h2>Voice-to-Fake Response Generator</h2>

//       {/* Toggle Microphone Button */}
//       <button
//         onClick={toggleMicrophone}
//         style={{
//           padding: "10px 20px",
//           fontSize: "16px",
//           margin: "20px 0",
//           cursor: "pointer",
//         }}
//       >
//         {isListening ? "Stop Microphone" : "Start Microphone"}
//       </button>

//       {/* Display User Transcript */}
//       <p style={{ marginTop: "20px", fontSize: "18px", color: "#555" }}>
//         <strong>Your Input:</strong> {transcript || "Say something to get started..."}
//       </p>

//       {/* Automatically Read Out Generated Fake Response */}
//       {isResponding && (
//         <Speech
//           text={response}
//           pitch={1.5}
//           rate={1}
//           volume={0.8}
//           voiceURI="Microsoft Zira - English (United States)"
//           autoPlay={speakNow} // Automatically trigger playback when response changes
//         />
//       )}
//     </div>
//   );
// };

// export default FakeResponseGenerator;
import React, { useState, useEffect } from "react";
import SpeechRecognition, { useSpeechRecognition } from "react-speech-recognition";
import axios from "axios";

const FakeResponseGenerator = () => {
  const [response, setResponse] = useState(""); // State to store the response
  const [isListening, setIsListening] = useState(false); // State to toggle microphone
  const [isResponding, setIsResponding] = useState(false); // State to indicate response generation
  const [speakNow, setSpeakNow] = useState(false); // State to control automatic playback

  // Speech recognition hooks
  const { transcript, listening, resetTranscript, browserSupportsSpeechRecognition } =
    useSpeechRecognition();

  // Function to send user input to backend and fetch the response
  const generateResponse = async () => {
    try {
      const res = await axios.post("http://127.0.0.1:5000/chat", {
        message: transcript,
      });
      setResponse(res.data.message); // Set the response from the backend
      setIsResponding(true);
      setSpeakNow(true); // Trigger response playback
      resetTranscript(); // Reset transcript after processing
    } catch (error) {
      console.error("Error generating response:", error);
      setResponse("Sorry, there was an error processing your request.");
      setIsResponding(true);
    }

    // Automatically reset responding state after 10 seconds
    setTimeout(() => setIsResponding(false), 10000);
  };

  // Automatically generate a response when the user stops speaking
  useEffect(() => {
    if (!listening && transcript) {
      generateResponse();
    }
  }, [listening, transcript]);

  // Toggle microphone state
  const toggleMicrophone = () => {
    if (isListening) {
      SpeechRecognition.stopListening();
      setIsListening(false);
    } else {
      resetTranscript();
      SpeechRecognition.startListening({ continuous: false });
      setIsListening(true);
    }
  };

  // Bind Space key for toggling the microphone
  useEffect(() => {
    const handleKeyDown = (event) => {
      if (event.code === "Space") {
        toggleMicrophone();
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [isListening]);

  if (!browserSupportsSpeechRecognition) {
    return <p>Your browser does not support speech recognition.</p>;
  }

  return (
    <div style={{ padding: "20px", textAlign: "center" }}>
      <h2>Voice-to-Response Generator</h2>

      {/* Toggle Microphone Button */}
      <button
        onClick={toggleMicrophone}
        style={{
          padding: "10px 20px",
          fontSize: "16px",
          margin: "20px 0",
          cursor: "pointer",
        }}
      >
        {isListening ? "Stop Microphone" : "Start Microphone"}
      </button>

      {/* Display User Transcript */}
      <p style={{ marginTop: "20px", fontSize: "18px", color: "#555" }}>
        <strong>Your Input:</strong> {transcript || "Say something to get started..."}
      </p>

      {/* Display Backend Response */}
      {isResponding && (
        <p style={{ marginTop: "20px", fontSize: "18px", color: "#555" }}>
          <strong>Response:</strong> {response}
        </p>
      )}
    </div>
  );
};

export default FakeResponseGenerator;
