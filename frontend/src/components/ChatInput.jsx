import {
  useEffect,
  useRef,
  useState,
} from "react";

import {
  Mic,
  MicOff,
  Send,
} from "lucide-react";

function ChatInput({
  onSend,
  loading,
  disabled = false,
}) {
  const [message, setMessage] =
    useState("");

  const [isListening, setIsListening] =
    useState(false);

  const [speechSupported, setSpeechSupported] =
    useState(true);

  const recognitionRef =
    useRef(null);

  const textareaRef =
    useRef(null);

  // ==========================================================
  // SPEECH RECOGNITION
  // ==========================================================

  useEffect(() => {
    const SpeechRecognition =
      window.SpeechRecognition ||
      window.webkitSpeechRecognition;

    if (!SpeechRecognition) {
      setSpeechSupported(false);
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

      setMessage(transcript);
    };

    recognition.onerror = (event) => {
      console.error(
        "Speech recognition error:",
        event.error
      );

      setIsListening(false);
    };

    recognition.onend = () => {
      setIsListening(false);
    };

    recognitionRef.current =
      recognition;

    return () => {
      try {
        recognition.stop();
      } catch {
        // Ignore.
      }

      recognitionRef.current = null;
    };
  }, []);

  // ==========================================================
  // MICROPHONE
  // ==========================================================

  const handleMicrophone = () => {
    if (
      loading ||
      disabled ||
      !speechSupported ||
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

  // ==========================================================
  // SEND
  // ==========================================================

  const handleSubmit = (event) => {
    event.preventDefault();

    const trimmed =
      message.trim();

    if (
      !trimmed ||
      loading ||
      disabled
    ) {
      return;
    }

    if (isListening) {
      try {
        recognitionRef.current?.stop();
      } catch {
        // Ignore.
      }
    }

    onSend(trimmed);

    setMessage("");

    if (textareaRef.current) {
      textareaRef.current.style.height =
        "auto";
    }
  };

  // ==========================================================
  // KEYBOARD
  // ==========================================================

  const handleKeyDown = (event) => {
    if (
      event.key === "Enter" &&
      !event.shiftKey
    ) {
      event.preventDefault();

      handleSubmit(event);
    }
  };

  // ==========================================================
  // AUTO RESIZE
  // ==========================================================

  const handleChange = (event) => {
    setMessage(event.target.value);

    const textarea =
      event.target;

    textarea.style.height =
      "auto";

    textarea.style.height =
      `${Math.min(
        textarea.scrollHeight,
        150
      )}px`;
  };

  // ==========================================================
  // RENDER
  // ==========================================================

  return (
    <form
      className="chat-input-container"
      onSubmit={handleSubmit}
    >

      <textarea
        ref={textareaRef}
        value={message}
        onChange={handleChange}
        onKeyDown={handleKeyDown}
        disabled={
          loading || disabled
        }
        rows={1}
        placeholder={
          disabled
            ? "Create a conversation to start..."
            : isListening
              ? "Listening..."
              : "Ask a question about your documents..."
        }
      />


      {/* ====================================================
          MICROPHONE
          ==================================================== */}

      <button
        type="button"
        className={`microphone-button ${
          isListening
            ? "microphone-listening"
            : ""
        }`}
        onClick={handleMicrophone}
        disabled={
          loading ||
          disabled ||
          !speechSupported
        }
        title={
          !speechSupported
            ? "Speech recognition is not supported"
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

      </button>


      {/* ====================================================
          SEND
          ==================================================== */}

      <button
        type="submit"
        className="chat-send-button"
        disabled={
          loading ||
          disabled ||
          !message.trim()
        }
        title="Send message"
      >

        {loading ? (
          <span className="send-spinner"></span>
        ) : (
          <Send size={18} />
        )}

      </button>

    </form>
  );
}

export default ChatInput;