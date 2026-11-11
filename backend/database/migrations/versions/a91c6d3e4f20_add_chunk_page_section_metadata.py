"""Add page and section provenance to document chunks.

Revision ID: a91c6d3e4f20
Revises: 72e50798c00f
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "a91c6d3e4f20"
down_revision: Union[str, Sequence[str], None] = "72e50798c00f"
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.add_column("document_chunks", sa.Column("page_number", sa.Integer(), nullable=True))
    op.add_column("document_chunks", sa.Column("section_title", sa.Text(), nullable=True))
    op.create_index("ix_document_chunks_page_number", "document_chunks", ["page_number"])

def downgrade() -> None:
    op.drop_index("ix_document_chunks_page_number", table_name="document_chunks")
    op.drop_column("document_chunks", "section_title")
    op.drop_column("document_chunks", "page_number")
