
"""
Document API

Provides endpoints for uploading, listing,
viewing, and deleting documents.
"""

from pathlib import Path
from uuid import uuid4

from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    UploadFile,
    status,
)
from sqlalchemy.orm import Session

from core.security import get_current_user
from database.database import get_db
from models.document import Document
from models.user import User
from schemas.upload import DocumentResponse
from services.document_service import process_and_store_document
from services.indexing_service import indexing_service


router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
)


# ==========================================================
# Upload Document
# ==========================================================

@router.post(
    "/upload",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
)
def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Upload and process a document.

    Each physical file receives a unique UUID filename,
    while the original filename is preserved in PostgreSQL.
    """

    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Filename is required.",
        )

    original_filename = Path(file.filename).name
    extension = Path(original_filename).suffix.lower()

    supported_extensions = {
        ".pdf",
        ".docx",
        ".txt",
        ".md",
    }

    if extension not in supported_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Unsupported file type: {extension}. "
                "Supported types: PDF, DOCX, TXT, MD."
            ),
        )

    # ------------------------------------------------------
    # Create user-specific storage directory
    # ------------------------------------------------------

    upload_directory = Path("storage/uploads")

    user_directory = upload_directory / str(current_user.id)

    user_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    # ------------------------------------------------------
    # Generate unique physical filename
    # ------------------------------------------------------

    unique_filename = f"{uuid4().hex}{extension}"
    file_path = user_directory / unique_filename

    # ------------------------------------------------------
    # Save uploaded file
    # ------------------------------------------------------

    try:
        with file_path.open("xb") as buffer:
            while True:
                chunk = file.file.read(1024 * 1024)

                if not chunk:
                    break

                buffer.write(chunk)

    except Exception as exc:
        if file_path.exists():
            file_path.unlink()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save uploaded file: {exc}",
        ) from exc

    finally:
        file.file.close()

    # ------------------------------------------------------
    # Process document and generate embeddings
    # ------------------------------------------------------

    try:
        document = process_and_store_document(
            db=db,
            file_path=file_path,
            user_id=current_user.id,
            filename=original_filename,
        )

    except Exception as exc:
        if file_path.exists():
            file_path.unlink()

        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Document processing failed: {exc}",
        ) from exc

    return document


# ==========================================================
# List Documents
# ==========================================================

@router.get(
    "",
    response_model=list[DocumentResponse],
)
def list_documents(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return documents belonging to the authenticated user."""

    documents = (
        db.query(Document)
        .filter(
            Document.user_id == current_user.id
        )
        .order_by(
            Document.created_at.desc()
        )
        .all()
    )

    return documents


# ==========================================================
# Get Document
# ==========================================================

@router.get(
    "/{document_id}",
    response_model=DocumentResponse,
)
def get_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return a document belonging to the authenticated user."""

    document = (
        db.query(Document)
        .filter(
            Document.id == document_id,
            Document.user_id == current_user.id,
        )
        .first()
    )

    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found.",
        )

    return document


# ==========================================================
# Delete Document
# ==========================================================

@router.delete(
    "/{document_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Delete a document belonging to the authenticated user
    and rebuild the FAISS index.
    """

    document = (
        db.query(Document)
        .filter(
            Document.id == document_id,
            Document.user_id == current_user.id,
        )
        .first()
    )

    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found.",
        )

    file_path = Path(document.file_path)

    try:
        db.delete(document)
        db.flush()

        # Correct method defined in indexing_service.py.
        # Rebuild the index without the deleted document's chunks.
        indexing_service.rebuild_index(db)

        db.commit()

    except Exception as exc:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete document and rebuild the vector index.",
        ) from exc

    # Remove the physical file after successful database deletion.
    try:
        if file_path.exists():
            file_path.unlink()

    except OSError:
        # Database deletion succeeded; an orphaned physical file
        # can be cleaned up separately.
        pass

    return None
