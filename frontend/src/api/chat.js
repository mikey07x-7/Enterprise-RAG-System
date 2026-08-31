import api from "./axios";

// ==========================================================
// Create Conversation
// ==========================================================

export const createConversation = async (
  title = "New Conversation"
) => {
  const response = await api.post(
    "/conversations",
    {
      title,
    }
  );

  return response.data;
};


// ==========================================================
// Get All Conversations
// ==========================================================

export const getConversations = async () => {
  const response = await api.get(
    "/conversations"
  );

  return response.data;
};


// ==========================================================
// Get Single Conversation
// ==========================================================

export const getConversation = async (
  conversationId
) => {
  const response = await api.get(
    `/conversations/${conversationId}`
  );

  return response.data;
};


// ==========================================================
// Delete Conversation
// ==========================================================

export const deleteConversation = async (
  conversationId
) => {
  await api.delete(
    `/conversations/${conversationId}`
  );
};


// ==========================================================
// Send Chat Message
// ==========================================================

export const sendChatMessage = async (
  conversationId,
  query,
  topK = 12
) => {
  const response = await api.post(
    "/chat",
    {
      conversation_id: conversationId,
      query,
      top_k: topK,
    }
  );

  return response.data;
};