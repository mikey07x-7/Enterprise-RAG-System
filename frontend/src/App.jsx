import { useEffect, useRef, useState } from "react";

import { loginUser, registerUser } from "./api/auth";
import { getDocuments, uploadDocument, deleteDocument } from "./api/documents";
import {
  createConversation,
  getConversations,
  getConversation,
  deleteConversation,
  sendChatMessage,
} from "./api/chat";

import "./index.css";

// ============================================================
// APP
// ============================================================

function App() {
  // ----------------------------------------------------------
  // Authentication
  // ----------------------------------------------------------
  const [token, setToken] = useState(localStorage.getItem("access_token"));
  const [username, setUsername] = useState(localStorage.getItem("username") || "");

  // Current page
  const [currentPage, setCurrentPage] = useState("dashboard");

  // Auth form
  const [isRegister, setIsRegister] = useState(false);
  const [formUsername, setFormUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // ==========================================================
  // LOGIN / REGISTER
  // ==========================================================
  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    try {
      if (isRegister) {
        await registerUser(formUsername.trim(), email.trim(), password);
        setIsRegister(false);
        setPassword("");
        setError("");
        alert("Registration successful. Please login.");
      } else {
        const data = await loginUser(formUsername.trim(), password);

        if (!data?.access_token) {
          throw new Error("Authentication token was not returned.");
        }

        localStorage.setItem("access_token", data.access_token);
        localStorage.setItem("username", formUsername.trim());

        setToken(data.access_token);
        setUsername(formUsername.trim());
        setCurrentPage("dashboard");
      }
    } catch (err) {
      console.error(err);
      setError(err.response?.data?.detail || err.message || "Something went wrong.");
    } finally {
      setLoading(false);
    }
  };

  // ==========================================================
  // LOGOUT
  // ==========================================================
  const handleLogout = () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("username");
    setToken(null);
    setUsername("");
    setCurrentPage("dashboard");
  };

  // ==========================================================
  // AUTH PAGE
  // ==========================================================
  if (!token) {
    return (
      <div className="auth-page">
        <div className="auth-card">
          <div className="brand">
            <div className="brand-icon">R</div>
            <div>
              <h1>Enterprise RAG</h1>
              <p>Private Document Intelligence</p>
            </div>
          </div>

          <div className="auth-heading">
            <h2>{isRegister ? "Create your account" : "Welcome back"}</h2>
            <p>
              {isRegister
                ? "Start asking questions about your documents."
                : "Sign in to access your enterprise knowledge base."}
            </p>
          </div>

          {error && <div className="error-message">{error}</div>}

          <form onSubmit={handleSubmit}>
            <label>Username</label>
            <input
              type="text"
              placeholder="Enter your username"
              value={formUsername}
              onChange={(e) => setFormUsername(e.target.value)}
              autoComplete="username"
              required
            />

            {isRegister && (
              <>
                <label>Email</label>
                <input
                  type="email"
                  placeholder="Enter your email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  autoComplete="email"
                  required
                />
              </>
            )}

            <label>Password</label>
            <input
              type="password"
              placeholder="Enter your password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              autoComplete={isRegister ? "new-password" : "current-password"}
              required
            />

            <button type="submit" disabled={loading}>
              {loading ? "Please wait..." : isRegister ? "Create Account" : "Sign In"}
            </button>
          </form>

          <div className="auth-switch">
            <span>{isRegister ? "Already have an account?" : "Don't have an account?"}</span>
            <button
              type="button"
              onClick={() => {
                setIsRegister((prev) => !prev);
                setError("");
                setPassword("");
              }}
            >
              {isRegister ? "Sign In" : "Create Account"}
            </button>
          </div>
        </div>
      </div>
    );
  }

  // ==========================================================
  // AUTHENTICATED APPLICATION
  // ==========================================================
  return (
    <AuthenticatedApp
      username={username}
      currentPage={currentPage}
      setCurrentPage={setCurrentPage}
      onLogout={handleLogout}
    />
  );
}

// ============================================================
// AUTHENTICATED APPLICATION
// ============================================================

function AuthenticatedApp({ username, currentPage, setCurrentPage, onLogout }) {
  // ==========================================================
  // SIDEBAR
  // ==========================================================
  const Sidebar = () => (
    <aside className="sidebar">
      <div className="sidebar-brand">
        <div className="brand-icon">R</div>
        <div>
          <h2>Enterprise RAG</h2>
          <span>Private Intelligence</span>
        </div>
      </div>

      <nav className="sidebar-nav">
        <button
          className={`nav-item ${currentPage === "dashboard" ? "active" : ""}`}
          onClick={() => setCurrentPage("dashboard")}
        >
          <span>🏠</span>
          Dashboard
        </button>

        <button
          className={`nav-item ${currentPage === "chat" ? "active" : ""}`}
          onClick={() => setCurrentPage("chat")}
        >
          <span>💬</span>
          Chat
        </button>

        <button
          className={`nav-item ${currentPage === "documents" ? "active" : ""}`}
          onClick={() => setCurrentPage("documents")}
        >
          <span>📄</span>
          Documents
        </button>

        <button
          className={`nav-item ${currentPage === "voice" ? "active" : ""}`}
          onClick={() => setCurrentPage("voice")}
        >
          <span>🎙️</span>
          Voice Assistant
        </button>
      </nav>

      <div className="sidebar-bottom">
        <div className="user-card">
          <div className="avatar">{username ? username.charAt(0).toUpperCase() : "U"}</div>
          <div className="user-info">
            <strong>{username || "User"}</strong>
            <span>Authenticated</span>
          </div>
        </div>

        <button className="logout-button" onClick={onLogout}>
          Logout
        </button>
      </div>
    </aside>
  );

  // ==========================================================
  // DASHBOARD
  // ==========================================================
  const Dashboard = () => (
    <main className="dashboard-main">
      <header className="dashboard-header">
        <div>
          <h1>Enterprise Knowledge Assistant</h1>
          <p>Ask questions about your private documents.</p>
        </div>
        <div className="status-badge">
          <span></span>
          System Online
        </div>
      </header>

      <section className="welcome-section">
        <div className="welcome-icon">✨</div>
        <h2>Welcome to your knowledge base</h2>
        <p>
          Upload your documents and ask questions. The RAG system will retrieve relevant
          information and generate grounded answers.
        </p>
      </section>

      <section className="dashboard-cards">
        <div className="dashboard-card">
          <div className="card-icon">📄</div>
          <h3>Documents</h3>
          <p>Upload and manage your private enterprise documents.</p>
          <button onClick={() => setCurrentPage("documents")}>Manage Documents</button>
        </div>

        <div className="dashboard-card">
          <div className="card-icon">💬</div>
          <h3>RAG Chat</h3>
          <p>Ask natural-language questions about your documents.</p>
          <button onClick={() => setCurrentPage("chat")}>Start Conversation</button>
        </div>

        <div className="dashboard-card">
          <div className="card-icon">🎙️</div>
          <h3>Voice Assistant</h3>
          <p>Talk naturally with your enterprise knowledge assistant using your microphone.</p>
          <button onClick={() => setCurrentPage("voice")}>Open Voice Assistant</button>
        </div>
      </section>
    </main>
  );

  // ==========================================================
  // CHAT PAGE
  // ==========================================================
  const ChatPage = () => {
    const [conversations, setConversations] = useState([]);
    const [selectedConversation, setSelectedConversation] = useState(null);
    const [messages, setMessages] = useState([]);
    const [messageInput, setMessageInput] = useState("");
    const [chatLoading, setChatLoading] = useState(false);
    const [conversationsLoading, setConversationsLoading] = useState(true);
    const [chatError, setChatError] = useState("");
    const messagesEndRef = useRef(null);

    useEffect(() => {
      const loadConversations = async () => {
        try {
          setConversationsLoading(true);
          setChatError("");
          const data = await getConversations();
          setConversations(Array.isArray(data) ? data : []);
        } catch (err) {
          console.error(err);
          setChatError(err.response?.data?.detail || "Failed to load conversations.");
        } finally {
          setConversationsLoading(false);
        }
      };
      loadConversations();
    }, []);

    useEffect(() => {
      messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [messages]);

    const handleSelectConversation = async (conversationId) => {
      try {
        setChatError("");
        const data = await getConversation(conversationId);
        setSelectedConversation(data);
        setMessages(data.messages || []);
      } catch (err) {
        console.error(err);
        setChatError(err.response?.data?.detail || "Failed to load conversation.");
      }
    };

    const handleNewConversation = async () => {
      try {
        setChatError("");
        const conversation = await createConversation("New Conversation");
        setConversations((prev) => [conversation, ...prev]);
        setSelectedConversation(conversation);
        setMessages([]);
      } catch (err) {
        console.error(err);
        setChatError(err.response?.data?.detail || "Failed to create conversation.");
      }
    };

    const handleDeleteConversation = async (conversationId, event) => {
      event?.stopPropagation();
      try {
        await deleteConversation(conversationId);
        setConversations((prev) => prev.filter((c) => c.id !== conversationId));
        if (selectedConversation?.id === conversationId) {
          setSelectedConversation(null);
          setMessages([]);
        }
      } catch (err) {
        console.error(err);
        setChatError(err.response?.data?.detail || "Failed to delete conversation.");
      }
    };

    const handleSendMessage = async (e) => {
      e?.preventDefault();
      const query = messageInput.trim();
      if (!query || chatLoading) return;

      let conversation = selectedConversation;

      try {
        setChatError("");
        setChatLoading(true);

        if (!conversation) {
          conversation = await createConversation(query.slice(0, 60));
          setSelectedConversation(conversation);
          setConversations((prev) => [conversation, ...prev]);
        }

        const temporaryUserMessage = {
          id: `temp-user-${Date.now()}`,
          role: "user",
          content: query,
        };
        setMessages((prev) => [...prev, temporaryUserMessage]);
        setMessageInput("");

        const response = await sendChatMessage(conversation.id, query, 5);

        const assistantMessage = {
          id: `temp-assistant-${Date.now()}`,
          role: "assistant",
          content: response.answer,
          sources: response.sources || [],
        };
        setMessages((prev) => [...prev, assistantMessage]);
      } catch (err) {
        console.error(err);
        setChatError(err.response?.data?.detail || "Failed to generate answer.");
      } finally {
        setChatLoading(false);
      }
    };

    const handleInputKeyDown = (e) => {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        handleSendMessage();
      }
    };

    return (
      <main className="dashboard-main">
        <header className="dashboard-header">
          <div>
            <h1>RAG Chat</h1>
            <p>Ask questions about your private documents.</p>
          </div>
          <div className="status-badge">
            <span></span>
            System Online
          </div>
        </header>

        <div
          style={{
            display: "grid",
            gridTemplateColumns: "260px minmax(0, 1fr)",
            gap: "16px",
            flex: 1,
            minHeight: 0,
            paddingTop: "20px",
          }}
        >
          {/* CONVERSATION SIDEBAR */}
          <section
            style={{
              border: "1px solid #263247",
              borderRadius: "12px",
              background: "#0d111b",
              display: "flex",
              flexDirection: "column",
              overflow: "hidden",
            }}
          >
            <div style={{ padding: "14px", borderBottom: "1px solid #263247" }}>
              <button
                onClick={handleNewConversation}
                style={{
                  width: "100%",
                  padding: "11px",
                  borderRadius: "8px",
                  border: "1px solid #4f46e5",
                  background: "#4f46e5",
                  color: "white",
                  cursor: "pointer",
                  fontWeight: "600",
                }}
              >
                + New Conversation
              </button>
            </div>

            <div style={{ flex: 1, overflowY: "auto", padding: "8px" }}>
              {conversationsLoading && (
                <p style={{ padding: "12px", color: "#64748b", fontSize: "13px" }}>
                  Loading conversations...
                </p>
              )}

              {!conversationsLoading && conversations.length === 0 && (
                <p style={{ padding: "12px", color: "#64748b", fontSize: "13px", lineHeight: "1.5" }}>
                  No conversations yet.
                  <br />
                  Start a new conversation.
                </p>
              )}

              {conversations.map((conversation) => (
                <div
                  key={conversation.id}
                  onClick={() => handleSelectConversation(conversation.id)}
                  style={{
                    padding: "11px",
                    marginBottom: "5px",
                    borderRadius: "8px",
                    cursor: "pointer",
                    background: selectedConversation?.id === conversation.id ? "#171b3a" : "transparent",
                    border:
                      selectedConversation?.id === conversation.id
                        ? "1px solid #3b3f72"
                        : "1px solid transparent",
                  }}
                >
                  <div style={{ display: "flex", justifyContent: "space-between", gap: "8px" }}>
                    <span
                      style={{
                        color: "#e2e8f0",
                        fontSize: "13px",
                        overflow: "hidden",
                        textOverflow: "ellipsis",
                        whiteSpace: "nowrap",
                      }}
                    >
                      {conversation.title || "Conversation"}
                    </span>
                    <button
                      onClick={(event) => handleDeleteConversation(conversation.id, event)}
                      style={{ border: "none", background: "transparent", color: "#ef4444", cursor: "pointer", fontSize: "12px" }}
                      title="Delete"
                    >
                      ×
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </section>

          {/* CHAT WINDOW */}
          <section
            style={{
              border: "1px solid #263247",
              borderRadius: "12px",
              background: "#0d111b",
              display: "flex",
              flexDirection: "column",
              minWidth: 0,
              overflow: "hidden",
            }}
          >
            <div style={{ padding: "14px 18px", borderBottom: "1px solid #263247" }}>
              <strong style={{ color: "#f8fafc" }}>
                {selectedConversation?.title || "New Conversation"}
              </strong>
            </div>

            {chatError && (
              <div
                style={{
                  margin: "12px 16px 0",
                  padding: "10px 12px",
                  borderRadius: "8px",
                  background: "rgba(239,68,68,0.1)",
                  border: "1px solid rgba(239,68,68,0.3)",
                  color: "#fca5a5",
                  fontSize: "13px",
                }}
              >
                {chatError}
              </div>
            )}

            <div style={{ flex: 1, overflowY: "auto", padding: "20px" }}>
              {messages.length === 0 && (
                <div style={{ height: "100%", display: "flex", alignItems: "center", justifyContent: "center", textAlign: "center" }}>
                  <div>
                    <div style={{ fontSize: "44px", marginBottom: "12px" }}>💬</div>
                    <h2 style={{ color: "#f8fafc", marginBottom: "8px" }}>Ask your knowledge base</h2>
                    <p style={{ color: "#64748b", maxWidth: "480px", lineHeight: "1.6" }}>
                      Ask a question about the documents you have uploaded. The RAG system will
                      retrieve relevant information and generate a grounded answer.
                    </p>
                  </div>
                </div>
              )}

              {messages.map((message, index) => (
                <div
                  key={message.id || `${message.role}-${index}`}
                  style={{ marginBottom: "18px", display: "flex", justifyContent: message.role === "user" ? "flex-end" : "flex-start" }}
                >
                  <div
                    style={{
                      maxWidth: "75%",
                      padding: "12px 15px",
                      borderRadius: "12px",
                      background: message.role === "user" ? "#25205a" : "#141a27",
                      border: "1px solid #2a3549",
                    }}
                  >
                    <div style={{ fontSize: "11px", color: "#818cf8", marginBottom: "6px", fontWeight: "600", textTransform: "uppercase" }}>
                      {message.role === "user" ? "You" : "Assistant"}
                    </div>

                    <div style={{ color: "#e2e8f0", lineHeight: "1.6", whiteSpace: "pre-wrap", fontSize: "14px" }}>
                      {message.content}
                    </div>

                    {message.sources && message.sources.length > 0 && (
                      <div style={{ marginTop: "14px", paddingTop: "12px", borderTop: "1px solid #263247" }}>
                        <div style={{ color: "#94a3b8", fontSize: "11px", fontWeight: "600", marginBottom: "8px" }}>
                          SOURCES
                        </div>
                        {message.sources.map((source, sourceIndex) => (
                          <div
                            key={sourceIndex}
                            style={{
                              padding: "8px 10px",
                              marginBottom: "6px",
                              borderRadius: "7px",
                              background: "#0b101a",
                              border: "1px solid #202b3e",
                              fontSize: "12px",
                              color: "#94a3b8",
                            }}
                          >
                            <strong style={{ color: "#cbd5e1" }}>
                              {source.filename || source.document_name || source.title || "Document"}
                            </strong>
                            {source.content && (
                              <div style={{ marginTop: "5px", lineHeight: "1.5" }}>{source.content}</div>
                            )}
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              ))}

              {chatLoading && (
                <div style={{ display: "flex", justifyContent: "flex-start" }}>
                  <div
                    style={{
                      padding: "12px 15px",
                      borderRadius: "12px",
                      background: "#141a27",
                      border: "1px solid #2a3549",
                      color: "#94a3b8",
                      fontSize: "13px",
                      marginBottom: "12px",
                    }}
                  >
                    Thinking...
                  </div>
                </div>
              )}

              <div ref={messagesEndRef} />
            </div>

            <form onSubmit={handleSendMessage} style={{ padding: "14px", borderTop: "1px solid #263247", display: "flex", gap: "10px" }}>
              <textarea
                value={messageInput}
                onChange={(e) => setMessageInput(e.target.value)}
                onKeyDown={handleInputKeyDown}
                placeholder="Ask a question about your documents..."
                rows={2}
                disabled={chatLoading}
                style={{
                  flex: 1,
                  resize: "none",
                  borderRadius: "9px",
                  border: "1px solid #334155",
                  background: "#0b101a",
                  color: "#f8fafc",
                  padding: "11px 13px",
                  outline: "none",
                  fontFamily: "inherit",
                  fontSize: "14px",
                }}
              />

              <button
                type="submit"
                disabled={chatLoading || !messageInput.trim()}
                style={{
                  alignSelf: "stretch",
                  minWidth: "90px",
                  borderRadius: "9px",
                  border: "1px solid #4f46e5",
                  background: chatLoading ? "#252a45" : "#4f46e5",
                  color: "white",
                  cursor: chatLoading ? "not-allowed" : "pointer",
                  fontWeight: "600",
                }}
              >
                {chatLoading ? "..." : "Send"}
              </button>
            </form>
          </section>
        </div>
      </main>
    );
  };

  // ==========================================================
  // DOCUMENTS PAGE
  // ==========================================================
  const DocumentsPage = () => {
    const [documents, setDocuments] = useState([]);
    const [loadingDocuments, setLoadingDocuments] = useState(true);
    const [uploading, setUploading] = useState(false);
    const [documentError, setDocumentError] = useState("");
    const [uploadSuccess, setUploadSuccess] = useState("");
    const fileInputRef = useRef(null);

    const loadDocuments = async () => {
      try {
        setLoadingDocuments(true);
        setDocumentError("");
        const data = await getDocuments();
        setDocuments(Array.isArray(data) ? data : []);
      } catch (err) {
        console.error(err);
        setDocumentError(err.response?.data?.detail || "Failed to load documents.");
      } finally {
        setLoadingDocuments(false);
      }
    };

    useEffect(() => {
      loadDocuments();
    }, []);

    const handleFileChange = async (event) => {
      const file = event.target.files?.[0];
      if (!file) return;

      try {
        setUploading(true);
        setDocumentError("");
        setUploadSuccess("");
        await uploadDocument(file);
        setUploadSuccess(`${file.name} uploaded and processed successfully.`);
        await loadDocuments();
      } catch (err) {
        console.error(err);
        setDocumentError(err.response?.data?.detail || "Failed to upload document.");
      } finally {
        setUploading(false);
        if (fileInputRef.current) fileInputRef.current.value = "";
      }
    };

    const handleDelete = async (documentId) => {
      const confirmed = window.confirm("Are you sure you want to delete this document?");
      if (!confirmed) return;

      try {
        setDocumentError("");
        await deleteDocument(documentId);
        setDocuments((prev) => prev.filter((d) => d.id !== documentId));
      } catch (err) {
        console.error(err);
        setDocumentError(err.response?.data?.detail || "Failed to delete document.");
      }
    };

    return (
      <main className="dashboard-main">
        <header className="dashboard-header">
          <div>
            <h1>Documents</h1>
            <p>Manage your private enterprise knowledge base.</p>
          </div>
          <div className="status-badge">
            <span></span>
            System Online
          </div>
        </header>

        <section
          style={{
            marginTop: "24px",
            border: "1px solid #29364c",
            borderRadius: "12px",
            padding: "18px",
            background: "#0d111b",
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            gap: "20px",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: "14px" }}>
            <div style={{ width: "42px", height: "42px", borderRadius: "10px", display: "flex", alignItems: "center", justifyContent: "center", background: "#191d3e", fontSize: "20px" }}>
              📄
            </div>
            <div>
              <h3 style={{ margin: 0, color: "#f8fafc", fontSize: "15px" }}>Upload a document</h3>
              <p style={{ margin: "4px 0 0", color: "#64748b", fontSize: "12px" }}>
                Add PDF, DOCX, TXT or Markdown files to your knowledge base.
              </p>
            </div>
          </div>

          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf,.docx,.txt,.md"
            onChange={handleFileChange}
            style={{ display: "none" }}
          />

          <button
            onClick={() => fileInputRef.current?.click()}
            disabled={uploading}
            style={{
              padding: "11px 20px",
              borderRadius: "8px",
              border: "1px solid #4f46e5",
              background: uploading ? "#30345a" : "#6366f1",
              color: "white",
              cursor: uploading ? "not-allowed" : "pointer",
              fontWeight: "600",
            }}
          >
            {uploading ? "Processing..." : "Choose Document"}
          </button>
        </section>

        {documentError && (
          <div style={{ marginTop: "14px", padding: "10px 13px", borderRadius: "8px", background: "rgba(239,68,68,0.1)", border: "1px solid rgba(239,68,68,0.3)", color: "#fca5a5", fontSize: "13px" }}>
            {documentError}
          </div>
        )}

        {uploadSuccess && (
          <div style={{ marginTop: "14px", padding: "10px 13px", borderRadius: "8px", background: "rgba(34,197,94,0.08)", border: "1px solid rgba(34,197,94,0.25)", color: "#86efac", fontSize: "13px" }}>
            {uploadSuccess}
          </div>
        )}

        <div style={{ marginTop: "28px", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <div>
            <h2 style={{ margin: "0 0 4px", color: "#f8fafc", fontSize: "17px" }}>Your Documents</h2>
            <span style={{ color: "#64748b", fontSize: "12px" }}>
              {documents.length} document{documents.length !== 1 ? "s" : ""}
            </span>
          </div>

          <button
            onClick={loadDocuments}
            disabled={loadingDocuments}
            style={{ padding: "8px 13px", borderRadius: "7px", border: "1px solid #334155", background: "#111827", color: "#e2e8f0", cursor: "pointer", fontSize: "12px" }}
          >
            ↻ Refresh
          </button>
        </div>

        <section style={{ marginTop: "12px", display: "flex", flexDirection: "column", gap: "8px" }}>
          {loadingDocuments && (
            <div style={{ padding: "30px", textAlign: "center", color: "#64748b" }}>Loading documents...</div>
          )}

          {!loadingDocuments && documents.length === 0 && (
            <div style={{ padding: "40px", textAlign: "center", border: "1px dashed #334155", borderRadius: "10px", color: "#64748b" }}>
              No documents uploaded yet.
            </div>
          )}

          {!loadingDocuments &&
            documents.map((document) => (
              <div
                key={document.id}
                style={{ display: "flex", alignItems: "center", justifyContent: "space-between", gap: "16px", padding: "14px", border: "1px solid #29364c", borderRadius: "10px", background: "#0d111b" }}
              >
                <div style={{ display: "flex", alignItems: "center", gap: "12px", minWidth: 0 }}>
                  <div style={{ width: "38px", height: "38px", borderRadius: "9px", display: "flex", alignItems: "center", justifyContent: "center", background: "#191d3e", flexShrink: 0 }}>
                    📄
                  </div>
                  <div style={{ minWidth: 0 }}>
                    <strong style={{ display: "block", color: "#e2e8f0", fontSize: "13px", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                      {document.filename}
                    </strong>
                    <span style={{ display: "block", marginTop: "4px", color: "#64748b", fontSize: "11px" }}>
                      {(document.file_type || "").toUpperCase()} · ID: {document.id} ·{" "}
                      {document.created_at ? new Date(document.created_at).toLocaleString() : "Unknown date"}
                    </span>
                  </div>
                </div>

                <div style={{ display: "flex", alignItems: "center", gap: "12px", flexShrink: 0 }}>
                  <span style={{ color: document.status === "ready" ? "#4ade80" : "#fbbf24", fontSize: "11px" }}>
                    ● {document.status || "Processing"}
                  </span>

                  <button
                    onClick={() => handleDelete(document.id)}
                    style={{ padding: "7px 11px", borderRadius: "7px", border: "1px solid rgba(239,68,68,0.35)", background: "rgba(239,68,68,0.05)", color: "#f87171", cursor: "pointer", fontSize: "11px" }}
                  >
                    Delete
                  </button>
                </div>
              </div>
            ))}
        </section>
      </main>
    );
  };

  // ==========================================================
  // VOICE ASSISTANT PAGE
  // ==========================================================
  const VoiceAssistantPage = () => {
    const [conversationId, setConversationId] = useState(null);
    const [messages, setMessages] = useState([]);
    const [voiceLoading, setVoiceLoading] = useState(false);
    const [voiceError, setVoiceError] = useState("");
    const [isListening, setIsListening] = useState(false);
    const [liveTranscript, setLiveTranscript] = useState("");
    const [micSupported, setMicSupported] = useState(true);

    const recognitionRef = useRef(null);
    const finalTranscriptRef = useRef("");
    const keepListeningRef = useRef(false);
    const messagesEndRef = useRef(null);

    useEffect(() => {
      const SpeechRecognitionAPI = window.SpeechRecognition || window.webkitSpeechRecognition;
      if (!SpeechRecognitionAPI) {
        setMicSupported(false);
      }
    }, []);

    useEffect(() => {
      messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [messages]);

    // Clean up recognition + speech synthesis on unmount.
    useEffect(() => {
      return () => {
        keepListeningRef.current = false;
        recognitionRef.current?.stop();
        if ("speechSynthesis" in window) {
          window.speechSynthesis.cancel();
        }
      };
    }, []);

    // --------------------------------------------------------
    // CREATE CONVERSATION (once, lazily)
    // --------------------------------------------------------
    const ensureConversation = async (query) => {
      if (conversationId) return conversationId;

      const conversation = await createConversation(
        query ? query.substring(0, 60) : "Voice Conversation"
      );
      setConversationId(conversation.id);
      return conversation.id;
    };

    // --------------------------------------------------------
    // SEND VOICE QUERY TO RAG + SPEAK THE ANSWER
    // --------------------------------------------------------
    const handleVoiceMessage = async (query) => {
      const cleanQuery = query.trim();
      if (!cleanQuery) return;

      setVoiceError("");
      setVoiceLoading(true);

      setMessages((prev) => [
        ...prev,
        { id: `user-${Date.now()}`, role: "user", content: cleanQuery },
      ]);

      try {
        const id = await ensureConversation(cleanQuery);
        const result = await sendChatMessage(id, cleanQuery, 5);
        const answer = result?.answer || "I could not generate an answer.";

        setMessages((prev) => [
          ...prev,
          {
            id: `assistant-${Date.now()}`,
            role: "assistant",
            content: answer,
            sources: result?.sources || [],
          },
        ]);

        if ("speechSynthesis" in window) {
          window.speechSynthesis.cancel();
          const speech = new SpeechSynthesisUtterance(answer);
          speech.lang = "en-IN";
          speech.rate = 0.95;
          speech.pitch = 1;
          window.speechSynthesis.speak(speech);
        }
      } catch (err) {
        console.error("Voice RAG error:", err);
        setVoiceError(err.response?.data?.detail || err.message || "Failed to generate voice response.");
        setMessages((prev) => prev.slice(0, -1));
      } finally {
        setVoiceLoading(false);
      }
    };

    // --------------------------------------------------------
    // MIC CONTROL
    //
    // Tap once to start listening. Recognition stays open and
    // keeps transcribing (it will not stop itself on a pause),
    // so the assistant does NOT reply automatically. Only when
    // the mic is tapped again do we stop listening, take the
    // full transcript, and send it off for a reply.
    // --------------------------------------------------------
    const startListening = () => {
      const SpeechRecognitionAPI = window.SpeechRecognition || window.webkitSpeechRecognition;

      if (!SpeechRecognitionAPI) {
        setMicSupported(false);
        setVoiceError("Voice recognition isn't supported in this browser. Try Chrome or Edge.");
        return;
      }

      // Interrupt any answer currently being read out loud.
      if ("speechSynthesis" in window) {
        window.speechSynthesis.cancel();
      }

      setVoiceError("");
      setLiveTranscript("");
      finalTranscriptRef.current = "";
      keepListeningRef.current = true;

      const recognition = new SpeechRecognitionAPI();
      recognition.continuous = true;
      recognition.interimResults = true;
      recognition.lang = "en-IN";

      recognition.onresult = (event) => {
        let interim = "";

        for (let i = event.resultIndex; i < event.results.length; i++) {
          const transcriptPiece = event.results[i][0].transcript;

          if (event.results[i].isFinal) {
            finalTranscriptRef.current += `${transcriptPiece} `;
          } else {
            interim += transcriptPiece;
          }
        }

        setLiveTranscript(`${finalTranscriptRef.current}${interim}`.trim());
      };

      recognition.onerror = (event) => {
        // A momentary silence isn't a real error — keep listening.
        if (event.error === "no-speech" || event.error === "aborted") {
          return;
        }

        console.error("Speech recognition error:", event.error);
        keepListeningRef.current = false;
        setIsListening(false);
        setVoiceError("Microphone error. Please check your permissions and try again.");
      };

      // Some browsers end recognition after a short silence even in
      // continuous mode — restart it automatically as long as the
      // user hasn't tapped the mic to stop, so we truly wait for them.
      recognition.onend = () => {
        if (keepListeningRef.current) {
          try {
            recognition.start();
          } catch {
            // Recognition may already be starting; safe to ignore.
          }
        }
      };

      recognitionRef.current = recognition;
      recognition.start();
      setIsListening(true);
    };

    const stopListeningAndSend = () => {
      keepListeningRef.current = false;
      setIsListening(false);
      recognitionRef.current?.stop();

      const query = finalTranscriptRef.current.trim() || liveTranscript.trim();
      setLiveTranscript("");
      finalTranscriptRef.current = "";

      if (query) {
        handleVoiceMessage(query);
      } else {
        setVoiceError("I didn't catch anything. Tap the mic and try again.");
      }
    };

    const handleMicClick = () => {
      if (voiceLoading) return;
      if (isListening) {
        stopListeningAndSend();
      } else {
        startListening();
      }
    };

    const micStatusLabel = voiceLoading
      ? "Thinking..."
      : isListening
      ? "Listening — tap to send"
      : "Voice Ready";

    return (
      <main className="dashboard-main">
        <style>{`
          @keyframes voiceOrbPulse {
            0%   { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.45); }
            70%  { box-shadow: 0 0 0 22px rgba(239, 68, 68, 0); }
            100% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0); }
          }
          @keyframes voiceDotBlink {
            0%, 100% { opacity: 0.25; }
            50% { opacity: 1; }
          }
        `}</style>

        <header className="dashboard-header">
          <div>
            <h1>Voice Assistant</h1>
            <p>Ask questions about your private documents using your voice.</p>
          </div>
          <div className="status-badge">
            <span
              style={{
                display: "inline-block",
                width: "8px",
                height: "8px",
                borderRadius: "50%",
                background: isListening ? "#ef4444" : voiceLoading ? "#fbbf24" : "#22c55e",
                marginRight: "6px",
              }}
            ></span>
            {micStatusLabel}
          </div>
        </header>

        <section
          style={{
            marginTop: "24px",
            border: "1px solid #29364c",
            borderRadius: "16px",
            padding: "40px 24px",
            background: "#0d111b",
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            textAlign: "center",
            gap: "18px",
          }}
        >
          {/* MIC ORB */}
          <button
            onClick={handleMicClick}
            disabled={voiceLoading || !micSupported}
            title={isListening ? "Tap to stop and send" : "Tap to start speaking"}
            style={{
              width: "96px",
              height: "96px",
              borderRadius: "50%",
              border: "none",
              cursor: voiceLoading || !micSupported ? "not-allowed" : "pointer",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              fontSize: "36px",
              color: "white",
              background: isListening
                ? "linear-gradient(135deg, #ef4444, #b91c1c)"
                : voiceLoading
                ? "linear-gradient(135deg, #64748b, #334155)"
                : "linear-gradient(135deg, #6366f1, #4338ca)",
              animation: isListening ? "voiceOrbPulse 1.6s infinite" : "none",
              transition: "background 0.2s ease, transform 0.15s ease",
            }}
          >
            🎙️
          </button>

          <div>
            <h2 style={{ color: "#f8fafc", margin: "0 0 8px", fontSize: "19px" }}>
              {isListening ? "Listening..." : "Talk to your knowledge base"}
            </h2>
            <p style={{ color: "#64748b", maxWidth: "480px", lineHeight: "1.6", margin: "0 auto" }}>
              {isListening
                ? "Speak your question, then tap the mic again when you're done. I'll only reply after you tap it — take your time."
                : "Tap the microphone and ask a question. Tap it again once you've finished speaking to get your answer."}
            </p>
          </div>

          {/* LIVE TRANSCRIPT */}
          {isListening && (
            <div
              style={{
                width: "100%",
                maxWidth: "560px",
                minHeight: "44px",
                padding: "12px 16px",
                borderRadius: "10px",
                background: "#0b101a",
                border: "1px solid #334155",
                color: liveTranscript ? "#e2e8f0" : "#64748b",
                fontSize: "14px",
                lineHeight: "1.5",
              }}
            >
              {liveTranscript || "Say something..."}
            </div>
          )}

          {voiceLoading && (
            <div style={{ display: "flex", alignItems: "center", gap: "10px", color: "#94a3b8", fontSize: "13px" }}>
              <span
                style={{
                  width: "8px",
                  height: "8px",
                  borderRadius: "50%",
                  background: "#818cf8",
                  animation: "voiceDotBlink 1s infinite",
                }}
              ></span>
              Retrieving information and generating answer...
            </div>
          )}

          {!micSupported && (
            <div style={{ padding: "10px 13px", borderRadius: "8px", background: "rgba(239,68,68,0.1)", border: "1px solid rgba(239,68,68,0.3)", color: "#fca5a5", fontSize: "13px" }}>
              This browser doesn't support voice input. Please try Chrome or Edge.
            </div>
          )}

          {voiceError && (
            <div style={{ padding: "10px 13px", borderRadius: "8px", background: "rgba(239,68,68,0.1)", border: "1px solid rgba(239,68,68,0.3)", color: "#fca5a5", fontSize: "13px" }}>
              {voiceError}
            </div>
          )}
        </section>

        {/* CONVERSATION */}
        {messages.length > 0 && (
          <section
            style={{
              marginTop: "20px",
              border: "1px solid #263247",
              borderRadius: "12px",
              background: "#0d111b",
              overflow: "hidden",
            }}
          >
            <div style={{ padding: "14px 18px", borderBottom: "1px solid #263247", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <strong style={{ color: "#f8fafc" }}>Voice Knowledge Session</strong>
              <span style={{ color: "#64748b", fontSize: "12px" }}>{messages.length} messages</span>
            </div>

            <div style={{ maxHeight: "360px", overflowY: "auto", padding: "18px" }}>
              {messages.map((message) => (
                <div
                  key={message.id}
                  style={{ marginBottom: "16px", display: "flex", justifyContent: message.role === "user" ? "flex-end" : "flex-start" }}
                >
                  <div
                    style={{
                      maxWidth: "75%",
                      padding: "12px 15px",
                      borderRadius: "12px",
                      background: message.role === "user" ? "#25205a" : "#141a27",
                      border: "1px solid #2a3549",
                    }}
                  >
                    <div style={{ fontSize: "11px", color: "#818cf8", marginBottom: "6px", fontWeight: "600", textTransform: "uppercase" }}>
                      {message.role === "user" ? "You" : "Enterprise RAG"}
                    </div>
                    <div style={{ color: "#e2e8f0", lineHeight: "1.6", whiteSpace: "pre-wrap", fontSize: "14px" }}>
                      {message.content}
                    </div>
                  </div>
                </div>
              ))}
              <div ref={messagesEndRef} />
            </div>
          </section>
        )}

        {/* INFO CARDS */}
        <section className="dashboard-cards" style={{ marginTop: "20px" }}>
          <div className="dashboard-card">
            <div className="card-icon">🎤</div>
            <h3>Speech Recognition</h3>
            <p>Speak naturally and your browser converts your speech into text.</p>
          </div>

          <div className="dashboard-card">
            <div className="card-icon">🧠</div>
            <h3>RAG Retrieval</h3>
            <p>Your question is processed against your private document knowledge base.</p>
          </div>

          <div className="dashboard-card">
            <div className="card-icon">🔊</div>
            <h3>Spoken Response</h3>
            <p>The generated answer is automatically read back using text-to-speech.</p>
          </div>
        </section>
      </main>
    );
  };

  // ==========================================================
  // PAGE SELECTOR
  // ==========================================================
  let pageContent;

  if (currentPage === "chat") {
    pageContent = <ChatPage />;
  } else if (currentPage === "documents") {
    pageContent = <DocumentsPage />;
  } else if (currentPage === "voice") {
    pageContent = <VoiceAssistantPage />;
  } else {
    pageContent = <Dashboard />;
  }

  // ==========================================================
  // FINAL LAYOUT
  // ==========================================================
  return (
    <div className="dashboard">
      <Sidebar />
      {pageContent}
    </div>
  );
}

// ============================================================
// EXPORT
// ============================================================

export default App;
