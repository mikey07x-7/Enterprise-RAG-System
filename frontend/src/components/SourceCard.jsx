function SourceCard({ source, index }) {

  const filename =
    source.filename ||
    source.file_name ||
    source.document_name ||
    source.document ||
    "Document";

  const page =
    source.page ||
    source.page_number ||
    source.metadata?.page;

  const score =
    source.score ??
    source.similarity ??
    source.relevance_score;

  const content =
    source.content ||
    source.text ||
    source.chunk ||
    "";

  return (
    <div className="source-card">

      <div className="source-number">
        {index + 1}
      </div>

      <div className="source-info">

        <div className="source-header">

          <strong>
            {filename}
          </strong>

          {page && (
            <span className="source-page">
              Page {page}
            </span>
          )}

        </div>

        {content && (
          <p>
            {content.length > 220
              ? `${content.substring(0, 220)}...`
              : content}
          </p>
        )}

        {score !== undefined && (
          <span className="source-score">
            Relevance:{" "}
            {(Number(score) * 100).toFixed(1)}%
          </span>
        )}

      </div>

    </div>
  );
}

export default SourceCard;