from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config
from sqlalchemy import pool

from core.config import settings
from database.database import Base

# Import all models so Alembic can detect them
from models.user import User
from models.document import Document
from models.chunk import Chunk
from models.conversation import Conversation
from models.message import Message


# ==========================================================
# Alembic Config
# ==========================================================

config = context.config


# ==========================================================
# Logging
# ==========================================================

if config.config_file_name is not None:
    fileConfig(config.config_file_name)


# ==========================================================
# Database URL
# ==========================================================

# Escape '%' characters because Alembic uses ConfigParser.
database_url = settings.DATABASE_URL.replace("%", "%%")

config.set_main_option(
    "sqlalchemy.url",
    database_url,
)


# ==========================================================
# Metadata
# ==========================================================

target_metadata = Base.metadata


# ==========================================================
# Offline Migration
# ==========================================================

def run_migrations_offline() -> None:
    """
    Run migrations without creating a database connection.
    """

    url = config.get_main_option("sqlalchemy.url")

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={
            "paramstyle": "named"
        },
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


# ==========================================================
# Online Migration
# ==========================================================

def run_migrations_online() -> None:
    """
    Run migrations using an active database connection.
    """

    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:

        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()


# ==========================================================
# Execute
# ==========================================================

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()