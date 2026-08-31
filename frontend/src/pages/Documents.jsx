import { useEffect, useRef, useState } from "react";
import {
  getDocuments,
  uploadDocument,
  deleteDocument,
} from "../api/documents";

function Documents() {
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const fileInputRef = useRef(null);

  // =========================================================
  // LOAD DOCUMENTS
  // =========================================================

  const loadDocuments = async () => {
    try {
      setLoading(true);
      setError("");

      const data = await getDocuments();

      setDocuments(data);
    } catch (err) {
      console.error(err);

      setError(
        err.response?.data?.detail ||
          "Failed to load documents."
      );
    } finally {
      setLoading(false);
    }
  };

  // =========================================================
  // INITIAL LOAD
  // =========================================================

  useEffect(() => {
    loadDocuments();
  }, []);

  // =========================================================
  // OPEN FILE SELECTOR
  // =========================================================

  const handleChooseDocument = () => {
    fileInputRef.current?.click();
  };

  // =========================================================
  // UPLOAD DOCUMENT
  // =========================================================

  const handleFileChange = async (event) => {
    const file = event.target.files?.[0];

    if (!file) {
      return;
    }

    setError("");
    setSuccess("");
    setUploading(true);

    try {
      await uploadDocument(file);

      setSuccess(
        `${file.name} uploaded and processed successfully.`
      );

      await loadDocuments();
    } catch (err) {
      console.error(err);

      setError(
        err.response?.data?.detail ||
          "Failed to upload document."
      );
    } finally {
      setUploading(false);

      // Allow selecting the same file again
      event.target.value = "";
    }
  };

  // =========================================================
  // DELETE DOCUMENT
  // =========================================================

  const handleDelete = async (documentId, filename) => {
    const confirmed = window.confirm(
      `Are you sure you want to delete "${filename}"?`
    );

    if (!confirmed) {
      return;
    }

    setError("");
    setSuccess("");

    try {
      await deleteDocument(documentId);

      setDocuments((currentDocuments) =>
        currentDocuments.filter(
          (document) => document.id !== documentId
        )
      );

      setSuccess(
        `${filename} deleted successfully.`
      );
    } catch (err) {
      console.error(err);

      setError(
        err.response?.data?.detail ||
          "Failed to delete document."
      );
    }
  };

  // =========================================================
  // FORMAT DATE
  // =========================================================

  const formatDate = (dateString) => {
    if (!dateString) {
      return "Unknown";
    }

    const date = new Date(dateString);

    if (Number.isNaN(date.getTime())) {
      return "Unknown";
    }

    return date.toLocaleString();
  };

  // =========================================================
  // FILE TYPE
  // =========================================================

  const getFileType = (document) => {
    if (document.file_type) {
      return document.file_type.toUpperCase();
    }

    const filename = document.filename || "";

    const extension = filename
      .split(".")
      .pop();

    return extension
      ? extension.toUpperCase()
      : "FILE";
  };

  // =========================================================
  // RENDER
  // =========================================================

  return (
    <div className="page-container">

      {/* =====================================================
          PAGE HEADER
      ===================================================== */}

      <header className="page-header">

        <div>
          <h1>Documents</h1>

          <p>
            Manage your private enterprise knowledge base.
          </p>
        </div>

        <div className="status-badge">
          <span></span>
          System Online
        </div>

      </header>


      {/* =====================================================
          UPLOAD SECTION
      ===================================================== */}

      <section className="upload-panel">

        <div className="upload-info">

          <div className="upload-icon">
            📄
          </div>

          <div>
            <h2>
              Upload a document
            </h2>

            <p>
              Add PDF, DOCX, TXT or Markdown files
              to your knowledge base.
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
          className="primary-button"
          onClick={handleChooseDocument}
          disabled={uploading}
        >
          {uploading
            ? "Processing..."
            : "Choose Document"}
        </button>

      </section>


      {/* =====================================================
          SUCCESS MESSAGE
      ===================================================== */}

      {success && (
        <div className="success-message">
          {success}
        </div>
      )}


      {/* =====================================================
          ERROR MESSAGE
      ===================================================== */}

      {error && (
        <div className="error-message">
          {error}
        </div>
      )}


      {/* =====================================================
          DOCUMENT LIST HEADER
      ===================================================== */}

      <div className="documents-header">

        <div>
          <h2>
            Your Documents
          </h2>

          <p>
            {documents.length}{" "}
            {documents.length === 1
              ? "document"
              : "documents"}
          </p>
        </div>

        <button
          className="secondary-button"
          onClick={loadDocuments}
          disabled={loading}
        >
          ↻ Refresh
        </button>

      </div>


      {/* =====================================================
          LOADING
      ===================================================== */}

      {loading && (
        <div className="empty-state">
          <div className="loading-spinner"></div>

          <p>
            Loading your documents...
          </p>
        </div>
      )}


      {/* =====================================================
          EMPTY STATE
      ===================================================== */}

      {!loading && documents.length === 0 && (
        <div className="empty-state">

          <div className="empty-icon">
            📄
          </div>

          <h3>
            No documents yet
          </h3>

          <p>
            Upload your first document to start
            building your private knowledge base.
          </p>

          <button
            className="primary-button"
            onClick={handleChooseDocument}
          >
            Upload Document
          </button>

        </div>
      )}


      {/* =====================================================
          DOCUMENT LIST
      ===================================================== */}

      {!loading && documents.length > 0 && (
        <section className="documents-list">

          {documents.map((document) => (
            <article
              className="document-item"
              key={document.id}
            >

              {/* FILE ICON */}

              <div className="document-icon">
                📄
              </div>


              {/* DOCUMENT INFORMATION */}

              <div className="document-info">

                <h3>
                  {document.filename}
                </h3>

                <div className="document-meta">

                  <span>
                    {getFileType(document)}
                  </span>

                  <span>
                    ID: {document.id}
                  </span>

                  <span>
                    {formatDate(
                      document.created_at
                    )}
                  </span>

                </div>

              </div>


              {/* STATUS */}

              <div className="document-status">

                <span
                  className={
                    document.status === "ready"
                      ? "status-ready"
                      : "status-processing"
                  }
                >
                  <span></span>

                  {document.status || "Processing"}
                </span>

              </div>


              {/* DELETE */}

              <button
                className="delete-button"
                onClick={() =>
                  handleDelete(
                    document.id,
                    document.filename
                  )
                }
              >
                Delete
              </button>

            </article>
          ))}

        </section>
      )}

    </div>
  );
}

export default Documents;