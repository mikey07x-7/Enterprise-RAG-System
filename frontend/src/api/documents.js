import api from "./axios";

// ==========================================================
// Get all documents
// ==========================================================

export const getDocuments = async () => {
  const response = await api.get("/documents");
  return response.data;
};


// ==========================================================
// Upload document
// ==========================================================

export const uploadDocument = async (file) => {
  const formData = new FormData();

  formData.append("file", file);

  const response = await api.post(
    "/documents/upload",
    formData,
    {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    }
  );

  return response.data;
};


// ==========================================================
// Get single document
// ==========================================================

export const getDocument = async (documentId) => {
  const response = await api.get(
    `/documents/${documentId}`
  );

  return response.data;
};


// ==========================================================
// Delete document
// ==========================================================

export const deleteDocument = async (documentId) => {
  await api.delete(
    `/documents/${documentId}`
  );
};