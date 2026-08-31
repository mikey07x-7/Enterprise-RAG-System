import { Mic, MicOff } from "lucide-react";
import { useEffect, useRef, useState } from "react";

function VoiceMode({
  onSendMessage,
  loading,
  disabled = false,
}) {
  const [isListening, setIsListening] =
    useState(false);

  const [supported, setSupported] =
    useState(true);

  const recognitionRef =
    useRef(null);

  useEffect(() => {
    const SpeechRecognition =
      window.SpeechRecognition ||
      window.webkitSpeechRecognition;

    if (!SpeechRecognition) {
      setSupported(false);
      return;
    }

    const recognition =
      new SpeechRecognition();

    recognition.continuous = false;
    recognition.interimResults = true;
    recognition.lang = "en-US";

    recognition.onstart = () => {
      setIsListening(true);
    };

    recognition.onresult = (event) => {
      let transcript = "";

      for (
        let i = event.resultIndex;
        i < event.results.length;
        i++
      ) {
        transcript +=
          event.results[i][0].transcript;
      }

      if (transcript.trim()) {
        onSendMessage?.(transcript.trim());
      }
    };

    recognition.onerror = (event) => {
      console.error(
        "Voice recognition error:",
        event.error
      );

      setIsListening(false);
    };

    recognition.onend = () => {
      setIsListening(false);
    };

    recognitionRef.current = recognition;

    return () => {
      try {
        recognition.stop();
      } catch {
        // Ignore.
      }

      recognitionRef.current = null;
    };
  }, [onSendMessage]);

  const handleVoice = () => {
    if (
      loading ||
      disabled ||
      !supported ||
      !recognitionRef.current
    ) {
      return;
    }

    if (isListening) {
      try {
        recognitionRef.current.stop();
      } catch {
        // Ignore.
      }

      return;
    }

    try {
      recognitionRef.current.start();
    } catch (error) {
      console.error(
        "Could not start speech recognition:",
        error
      );
    }
  };

  return (
    <button
      type="button"
      className={`voice-chat-button ${
        isListening
          ? "voice-chat-button-active"
          : ""
      }`}
      onClick={handleVoice}
      disabled={
        loading ||
        disabled ||
        !supported
      }
      title={
        !supported
          ? "Voice input is not supported"
          : isListening
            ? "Stop listening"
            : "Voice input"
      }
    >
      {isListening ? (
        <MicOff size={19} />
      ) : (
        <Mic size={19} />
      )}

      <span>
        {isListening
          ? "Listening"
          : "Voice"}
      </span>
    </button>
  );
}

export default VoiceMode;