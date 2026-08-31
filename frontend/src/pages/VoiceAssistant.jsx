import { useEffect, useRef, useState } from "react";
import {
  Mic,
  MicOff,
  ArrowLeft,
  Volume2,
  MessageSquare,
  Sparkles,
} from "lucide-react";

function VoiceAssistant({
  onNavigate,
  onSendMessage,
}) {
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState("");
  const [speechSupported, setSpeechSupported] = useState(true);
  const [error, setError] = useState("");

  const recognitionRef = useRef(null);

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

    const recognition = new SpeechRecognition();

    recognition.continuous = false;
    recognition.interimResults = true;
    recognition.lang = "en-US";

    recognition.onstart = () => {
      setError("");
      setIsListening(true);
    };

    recognition.onresult = (event) => {
      let finalTranscript = "";

      for (
        let i = event.resultIndex;
        i < event.results.length;
        i++
      ) {
        finalTranscript +=
          event.results[i][0].transcript;
      }

      setTranscript(finalTranscript);
    };

    recognition.onerror = (event) => {
      console.error(
        "Voice recognition error:",
        event.error
      );

      setIsListening(false);

      if (event.error === "not-allowed") {
        setError(
          "Microphone permission was denied. Please allow microphone access in your browser."
        );
      } else if (event.error === "no-speech") {
        setError(
          "No speech was detected. Please try again."
        );
      } else {
        setError(
          "Unable to recognize your voice. Please try again."
        );
      }
    };

    recognition.onend = () => {
      setIsListening(false);
    };

    recognitionRef.current = recognition;

    return () => {
      try {
        recognition.stop();
      } catch {
        // Recognition may already be stopped.
      }

      recognitionRef.current = null;
    };
  }, []);

  // ==========================================================
  // START / STOP LISTENING
  // ==========================================================

  const toggleListening = () => {
    if (!speechSupported) {
      return;
    }

    if (!recognitionRef.current) {
      return;
    }

    if (isListening) {
      try {
        recognitionRef.current.stop();
      } catch {
        // Ignore stop errors.
      }

      return;
    }

    setTranscript("");
    setError("");

    try {
      recognitionRef.current.start();
    } catch (err) {
      console.error(err);
    }
  };

  // ==========================================================
  // SEND TRANSCRIPT TO RAG CHAT
  // ==========================================================

  const handleSendToChat = () => {
    const text = transcript.trim();

    if (!text) {
      return;
    }

    if (isListening) {
      try {
        recognitionRef.current?.stop();
      } catch {
        // Ignore.
      }
    }

    if (onSendMessage) {
      onSendMessage(text);
    }

    if (onNavigate) {
      onNavigate("chat");
    }
  };

  // ==========================================================
  // CLEAR
  // ==========================================================

  const handleClear = () => {
    setTranscript("");
    setError("");
  };

  // ==========================================================
  // RENDER
  // ==========================================================

  return (
    <div className="voice-assistant-page">

      {/* ======================================================
          HEADER
          ====================================================== */}

      <header className="voice-assistant-header">

        <button
          className="voice-back-button"
          onClick={() =>
            onNavigate?.("chat")
          }
        >
          <ArrowLeft size={17} />

          <span>
            Back to RAG Chat
          </span>
        </button>

        <div className="voice-header-status">
          <span></span>
          Voice Assistant Online
        </div>

      </header>


      {/* ======================================================
          MAIN CONTENT
          ====================================================== */}

      <main className="voice-assistant-content">

        <div className="voice-assistant-intro">

          <div className="voice-assistant-icon">
            <Sparkles size={22} />
          </div>

          <h1>
            Voice Knowledge Assistant
          </h1>

          <p>
            Ask questions about your private
            documents using your voice.
          </p>

        </div>


        {/* ====================================================
            MICROPHONE
            ==================================================== */}

        <div
          className={`voice-microphone-wrapper ${
            isListening
              ? "voice-microphone-active"
              : ""
          }`}
        >

          <div className="voice-orbit orbit-one"></div>
          <div className="voice-orbit orbit-two"></div>

          <button
            className={`voice-main-button ${
              isListening
                ? "voice-main-button-active"
                : ""
            }`}
            onClick={toggleListening}
            disabled={!speechSupported}
            aria-label={
              isListening
                ? "Stop listening"
                : "Start listening"
            }
          >

            {isListening ? (
              <MicOff size={42} />
            ) : (
              <Mic size={42} />
            )}

          </button>

        </div>


        {/* ====================================================
            STATUS
            ==================================================== */}

        <div className="voice-listening-status">

          {isListening ? (
            <>
              <div className="voice-live-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>

              <strong>
                Listening...
              </strong>

              <p>
                Speak naturally. I'm listening.
              </p>
            </>
          ) : (
            <>
              <strong>
                {speechSupported
                  ? "Ready to listen"
                  : "Voice recognition unavailable"}
              </strong>

              <p>
                {speechSupported
                  ? "Click the microphone and ask your question."
                  : "Your current browser does not support speech recognition."}
              </p>
            </>
          )}

        </div>


        {/* ====================================================
            TRANSCRIPT
            ==================================================== */}

        <section className="voice-transcript-card">

          <div className="voice-transcript-header">

            <div>
              <MessageSquare size={16} />

              <span>
                Your question
              </span>
            </div>

            {transcript && (
              <button
                className="voice-clear-button"
                onClick={handleClear}
              >
                Clear
              </button>
            )}

          </div>


          <div className="voice-transcript">

            {transcript ? (
              <p>
                {transcript}
              </p>
            ) : (
              <span className="voice-transcript-placeholder">
                Your spoken question will appear here...
              </span>
            )}

          </div>


          {/* ==================================================
              ACTIONS
              ================================================== */}

          <div className="voice-actions">

            <button
              className="voice-secondary-button"
              onClick={toggleListening}
              disabled={!speechSupported}
            >

              {isListening ? (
                <>
                  <MicOff size={16} />
                  Stop Listening
                </>
              ) : (
                <>
                  <Mic size={16} />
                  Start Listening
                </>
              )}

            </button>


            <button
              className="voice-primary-button"
              onClick={handleSendToChat}
              disabled={!transcript.trim()}
            >

              <Volume2 size={16} />

              Ask RAG Assistant

            </button>

          </div>

        </section>


        {/* ====================================================
            ERROR
            ==================================================== */}

        {error && (
          <div className="voice-error">
            {error}
          </div>
        )}


        {/* ====================================================
            INFORMATION
            ==================================================== */}

        <div className="voice-info">

          <div className="voice-info-item">

            <Mic size={17} />

            <div>
              <strong>
                Speak naturally
              </strong>

              <span>
                Ask your question just like
                you would normally speak.
              </span>
            </div>

          </div>


          <div className="voice-info-item">

            <MessageSquare size={17} />

            <div>
              <strong>
                RAG powered
              </strong>

              <span>
                Your question is sent to the
                same private knowledge base.
              </span>
            </div>

          </div>

        </div>

      </main>

    </div>
  );
}

export default VoiceAssistant;