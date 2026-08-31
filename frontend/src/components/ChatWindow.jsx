import ChatMessage from "./ChatMessage";
import ChatInput from "./ChatInput";

function ChatWindow({
  conversation,
  messages,
  loading,
  error,
  onSendMessage,
}) {
  return (
    <main className="chat-main">

      {/* ======================================================
          HEADER
          ====================================================== */}

      <header className="chat-header">

        <div>
          <h1>
            {conversation?.title ||
              "RAG Chat"}
          </h1>

          <p>
            Ask questions about your private documents.
          </p>
        </div>

        <div className="status-badge">
          <span></span>
          System Online
        </div>

      </header>


      {/* ======================================================
          CHAT CONTENT
          ====================================================== */}

      <section className="chat-content">

        {messages.length === 0 ? (

          <div className="chat-empty-state">

            <div className="chat-empty-icon">
              💬
            </div>

            <h2>
              Ask your knowledge base
            </h2>

            <p>
              Ask a question about the documents
              you have uploaded. The RAG system
              retrieves relevant information and
              generates a grounded answer.
            </p>


            {/* ==================================================
                EXAMPLE QUESTIONS
                ================================================== */}

            <div className="example-questions">

              <button
                onClick={() =>
                  onSendMessage(
                    "What are the main topics covered in my documents?"
                  )
                }
                disabled={loading || !conversation}
              >
                What are the main topics in my documents?
              </button>

              <button
                onClick={() =>
                  onSendMessage(
                    "Summarize the uploaded documents."
                  )
                }
                disabled={loading || !conversation}
              >
                Summarize my documents
              </button>

              <button
                onClick={() =>
                  onSendMessage(
                    "What important information should I know from these documents?"
                  )
                }
                disabled={loading || !conversation}
              >
                What important information should I know?
              </button>

            </div>

          </div>

        ) : (

          <div className="messages-container">

            {messages.map(
              (message, index) => (
                <ChatMessage
                  key={
                    message.id ||
                    `${message.role}-${index}`
                  }
                  message={message}
                />
              )
            )}


            {/* ==================================================
                LOADING
                ================================================== */}

            {loading && (

              <div className="chat-message-row assistant-message-row">

                <div className="message-avatar">
                  R
                </div>

                <div className="message-content">

                  <div className="message-role">
                    Enterprise RAG
                  </div>

                  <div className="message-bubble assistant-message">

                    <div className="typing-indicator">
                      <span></span>
                      <span></span>
                      <span></span>
                    </div>

                  </div>

                </div>

              </div>

            )}

            <div className="chat-bottom-space"></div>

          </div>

        )}

      </section>


      {/* ======================================================
          ERROR
          ====================================================== */}

      {error && (
        <div className="chat-error">
          {error}
        </div>
      )}


      {/* ======================================================
          INPUT
          ====================================================== */}

      <div className="chat-input-area">

        <ChatInput
          onSend={onSendMessage}
          loading={loading}
          disabled={!conversation}
        />

      </div>


      {/* ======================================================
          DISCLAIMER
          ====================================================== */}

      <div className="chat-disclaimer">
        Enterprise RAG generates answers from your
        private document knowledge base.
      </div>

    </main>
  );
}

export default ChatWindow;