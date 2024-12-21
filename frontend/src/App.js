import './App.css';
// import Dictaphone from './pages/Dictaphone';
// import Output from './pages/Output';
import FakeResponseGenerator from './pages/FakeResponseGenerator';
// import PrintEmbeddings from './pages/PrintEmbeddings';
function App() {
  const textToRead = "Welcome to the text-to-speech demo using React.";
  return (
    <div className="App">
      <FakeResponseGenerator/>
      {/* <Dictaphone /> */}
      {/* <Output text={textToRead}/> */}
      {/* <PrintEmbeddings/> */}
    </div>
  );
}

export default App;
// import React from "react";
// import Speech from "react-text-to-speech";

// export default function App() {
//   return (
//     <Speech text="This is a fully customized speech component." pitch={1.5} rate={2} volume={0.5} voiceURI="Microsoft Heera - English (India)">
//       {({ speechStatus, isInQueue, start, pause, stop }) => (
//         <div style={{ display: "flex", columnGap: "0.5rem" }}>
//           {speechStatus !== "started" ? <button onClick={start}>Start</button> : <button onClick={pause}>Pause</button>}
//           <button onClick={stop}>Stop</button>
//         </div>
//       )}
//     </Speech>
//   );
// }