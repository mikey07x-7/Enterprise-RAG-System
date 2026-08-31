function Sidebar({
  username,
  conversations,
  activeConversationId,
  onSelectConversation,
  onNewChat,
  onDeleteConversation,
  activePage,
  onNavigate,
  onLogout,
}) {
  return (
    <aside className="chat-sidebar">

      {/* BRAND */}
      <div className="chat-sidebar-brand">
        <div className="brand-icon">R</div>

        <div>
          <h2>Enterprise RAG</h2>
          <span>Private Intelligence</span>
        </div>
      </div>

      {/* NAVIGATION */}
      <div className="chat-navigation">

        <button
          className={`chat-nav-item ${
            activePage === "chat" ? "active" : ""
          }`}
          onClick={() => onNavigate("chat")}
        >
          <span>💬</span>
          Chat
        </button>

        <button
          className={`chat-nav-item ${
            activePage === "documents" ? "active" : ""
          }`}
          onClick={() => onNavigate("documents")}
        >
          <span>📄</span>
          Documents
        </button>

      </div>

      {/* CONVERSATIONS */}
      {activePage === "chat" && (
        <div className="conversation-section">

          <div className="conversation-header">
            <span>Conversations</span>

            <button
              className="new-chat-button"
              onClick={onNewChat}
              title="New conversation"
            >
              +
            </button>
          </div>

          <div className="conversation-list">

            {conversations.length === 0 ? (
              <div className="no-conversations">
                No conversations yet.
                <br />
                Start a new chat.
              </div>
            ) : (
              conversations.map((conversation) => (
                <div
                  key={conversation.id}
                  className={`conversation-item ${
                    activeConversationId === conversation.id
                      ? "active"
                      : ""
                  }`}
                >

                  <button
                    className="conversation-select"
                    onClick={() =>
                      onSelectConversation(conversation.id)
                    }
                  >
                    <span className="conversation-icon">
                      💬
                    </span>

                    <span className="conversation-title">
                      {conversation.title ||
                        "New Conversation"}
                    </span>
                  </button>

                  <button
                    className="conversation-delete"
                    onClick={() =>
                      onDeleteConversation(conversation.id)
                    }
                    title="Delete conversation"
                  >
                    ×
                  </button>

                </div>
              ))
            )}

          </div>

        </div>
      )}

      {/* BOTTOM USER */}
      <div className="chat-sidebar-bottom">

        <div className="chat-user-card">

          <div className="chat-avatar">
            {username
              ? username.charAt(0).toUpperCase()
              : "U"}
          </div>

          <div>
            <strong>
              {username || "User"}
            </strong>

            <span>
              Authenticated
            </span>
          </div>

        </div>

        <button
          className="chat-logout-button"
          onClick={onLogout}
        >
          Logout
        </button>

      </div>

    </aside>
  );
}

export default Sidebar;