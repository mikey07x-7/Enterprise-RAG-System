import { useEffect, useState } from "react";

import {
  createConversation,
  getConversations,
  getConversation,
  deleteConversation,
  sendChatMessage,
} from "../api/chat";

import Sidebar from "../components/Sidebar";
import ChatWindow from "../components/ChatWindow";

function Chat({
  username,
  onLogout,
  onNavigate,
}) {

  const [conversations, setConversations] =
    useState([]);

  const [activeConversationId, setActiveConversationId] =
    useState(null);

  const [activeConversation, setActiveConversation] =
    useState(null);

  const [messages, setMessages] =
    useState([]);

  const [loading, setLoading] =
    useState(false);

  const [pageLoading, setPageLoading] =
    useState(true);

  const [error, setError] =
    useState("");

  // ========================================================
  // LOAD CONVERSATIONS
  // ========================================================

  useEffect(() => {
    loadConversations();
  }, []);

  const loadConversations = async () => {

    try {

      setPageLoading(true);
      setError("");

      const data =
        await getConversations();

      setConversations(
        Array.isArray(data)
          ? data
          : data.conversations || []
      );

    } catch (err) {

      console.error(err);

      setError(
        err.response?.data?.detail ||
        "Failed to load conversations."
      );

    } finally {

      setPageLoading(false);

    }
  };

  // ========================================================
  // SELECT CONVERSATION
  // ========================================================

  const handleSelectConversation = async (
    conversationId
  ) => {

    try {

      setError("");
      setActiveConversationId(
        conversationId
      );

      const data =
        await getConversation(
          conversationId
        );

      setActiveConversation(data);

      setMessages(
        data.messages || []
      );

    } catch (err) {

      console.error(err);

      setError(
        err.response?.data?.detail ||
        "Failed to load conversation."
      );

    }
  };

  // ========================================================
  // NEW CONVERSATION
  // ========================================================

  const handleNewChat = async () => {

    try {

      setError("");

      const conversation =
        await createConversation(
          "New Conversation"
        );

      setConversations((previous) => [
        conversation,
        ...previous,
      ]);

      setActiveConversation(
        conversation
      );

      setActiveConversationId(
        conversation.id
      );

      setMessages([]);

    } catch (err) {

      console.error(err);

      setError(
        err.response?.data?.detail ||
        "Failed to create conversation."
      );

    }
  };

  // ========================================================
  // DELETE CONVERSATION
  // ========================================================

  const handleDeleteConversation = async (
    conversationId
  ) => {

    const confirmed =
      window.confirm(
        "Delete this conversation?"
      );

    if (!confirmed) {
      return;
    }

    try {

      await deleteConversation(
        conversationId
      );

      const remaining =
        conversations.filter(
          (conversation) =>
            conversation.id !== conversationId
        );

      setConversations(remaining);

      if (
        activeConversationId ===
        conversationId
      ) {

        setActiveConversationId(null);
        setActiveConversation(null);
        setMessages([]);

      }

    } catch (err) {

      console.error(err);

      setError(
        err.response?.data?.detail ||
        "Failed to delete conversation."
      );

    }
  };

  // ========================================================
  // SEND MESSAGE
  // ========================================================

  const handleSendMessage = async (
    query
  ) => {

    if (!activeConversationId) {

      // Automatically create conversation
      // if user tries to chat without one.

      try {

        const conversation =
          await createConversation(
            query.substring(0, 60)
          );

        setConversations((previous) => [
          conversation,
          ...previous,
        ]);

        setActiveConversation(
          conversation
        );

        setActiveConversationId(
          conversation.id
        );

        await sendMessage(
          conversation.id,
          query
        );

      } catch (err) {

        console.error(err);

        setError(
          err.response?.data?.detail ||
          "Failed to start conversation."
        );

      }

      return;
    }

    await sendMessage(
      activeConversationId,
      query
    );
  };

  // ========================================================
  // SEND MESSAGE TO BACKEND
  // ========================================================

  const sendMessage = async (
    conversationId,
    query
  ) => {

    setError("");
    setLoading(true);

    // Immediately show user message
    setMessages((previous) => [
      ...previous,
      {
        role: "user",
        content: query,
      },
    ]);

    try {

      const result =
        await sendChatMessage(
          conversationId,
          query,
          5
        );

      // Add assistant answer
      setMessages((previous) => [
        ...previous,
        {
          role: "assistant",
          content: result.answer,
          sources:
            result.sources || [],
        },
      ]);

      // Refresh conversations so updated
      // timestamps/titles are reflected.
      const updated =
        await getConversations();

      setConversations(
        Array.isArray(updated)
          ? updated
          : updated.conversations || []
      );

      // Refresh active conversation
      try {

        const conversation =
          await getConversation(
            conversationId
          );

        setActiveConversation(
          conversation
        );

      } catch {
        // The chat response itself is
        // already successfully displayed.
      }

    } catch (err) {

      console.error(err);

      // Remove optimistic user message
      setMessages((previous) =>
        previous.slice(0, -1)
      );

      setError(
        err.response?.data?.detail ||
        "Failed to generate RAG response."
      );

    } finally {

      setLoading(false);

    }
  };

  // ========================================================
  // LOADING
  // ========================================================

  if (pageLoading) {

    return (
      <div className="chat-loading-page">
        <div className="loading-spinner"></div>

        <p>
          Loading your knowledge base...
        </p>
      </div>
    );
  }

  // ========================================================
  // RENDER
  // ========================================================

  return (
    <div className="chat-page">

      <Sidebar
        username={username}
        conversations={conversations}
        activeConversationId={
          activeConversationId
        }
        onSelectConversation={
          handleSelectConversation
        }
        onNewChat={
          handleNewChat
        }
        onDeleteConversation={
          handleDeleteConversation
        }
        activePage="chat"
        onNavigate={onNavigate}
        onLogout={onLogout}
      />

      <ChatWindow
        conversation={activeConversation}
        messages={messages}
        loading={loading}
        error={error}
        onSendMessage={
          handleSendMessage
        }
      />

    </div>
  );
}

export default Chat;