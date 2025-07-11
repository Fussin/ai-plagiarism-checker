from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
# target_metadata = None # Will be replaced

# Ensure the application's modules can be imported.
import os
import sys
# Get the directory of the current file (env.py, which is in backend/alembic)
current_dir = os.path.dirname(os.path.abspath(__file__))
# Path to the 'backend' directory (one level up from 'alembic')
backend_dir = os.path.dirname(current_dir)
# Path to the project root (one level up from 'backend')
project_root = os.path.dirname(backend_dir)

# Add project root to sys.path to allow imports like 'from backend.database import Base'
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Now import Base from your application
from backend.database import Base # Base for SQLAlchemy models
from backend.models import UserDB, ScanHistoryDB # Import all your SQLAlchemy models here
from backend.config import settings # To get DATABASE_URL

target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    # url = config.get_main_option("sqlalchemy.url") # Original line
    url = settings.DATABASE_URL # Use DATABASE_URL from settings
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    # section = config.get_section(config.config_ini_section, {}) # Original way to get section
    # section['sqlalchemy.url'] = settings.DATABASE_URL # Override with our settings

    # A cleaner way might be to directly use the engine from database.py if it's already configured
    # However, alembic's standard way is to use its own config.
    # Let's ensure the config object used by engine_from_config has the correct URL.

    # The config object is already loaded. We can directly set the URL for the current section.
    db_config = config.get_section(config.config_ini_section, {})
    db_config["sqlalchemy.url"] = settings.DATABASE_URL

    connectable = engine_from_config(
        db_config, # Use the modified config
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
