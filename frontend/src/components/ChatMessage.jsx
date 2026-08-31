import SourceCard from "./SourceCard";

function ChatMessage({ message }) {

  const isUser = message.role === "user";

  return (
    <div
      className={`chat-message-row ${
        isUser ? "user-message-row" : "assistant-message-row"
      }`}
    >

      <div className="message-avatar">
        {isUser ? "U" : "R"}
      </div>

      <div className="message-content">

        <div className="message-role">
          {isUser ? "You" : "Enterprise RAG"}
        </div>

        <div
          className={`message-bubble ${
            isUser
              ? "user-message"
              : "assistant-message"
          }`}
        >
          {message.content}
        </div>

        {/* SOURCES */}
        {!isUser &&
          message.sources &&
          message.sources.length > 0 && (
            <div className="sources-container">

              <div className="sources-title">
                📚 Retrieved Sources
              </div>

              <div className="sources-list">
                {message.sources.map((source, index) => (
                  <SourceCard
                    key={index}
                    source={source}
                    index={index}
                  />
                ))}
              </div>

            </div>
          )}

      </div>

    </div>
  );
}

export default ChatMessage;