import React from "react";
import { useSpeech } from "react-text-to-speech";

export default function Output({ text }) {
  const { speechStatus, start, pause, stop } = useSpeech({
    text,
    pitch: 1,
    rate: 1,
    volume: 1,
    lang: "en-GB",
    voiceURI: "Google UK English Female",
    autoPlay: true,
    highlightText: true,
  });

  return (
    <div style={{ margin: "1rem", whiteSpace: "pre-wrap" }}>
      <div style={{ display: "flex", columnGap: "1rem", marginBottom: "1rem" }}>
        <button disabled={speechStatus === "started"} onClick={start}>
          Start
        </button>
        <button disabled={speechStatus === "paused"} onClick={pause}>
          Pause
        </button>
        <button disabled={speechStatus === "stopped"} onClick={stop}>
          Stop
        </button>
      </div>
      <p>{text}</p> {/* Render text as a plain string */}
    </div>
  );
}
