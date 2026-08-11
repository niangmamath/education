import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import create_async_engine

from app.core.config import settings

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = None


def _validate_heads(script):
    heads = script.get_heads()
    # Prevent running migrations when multiple heads exist in repo
    if len(heads) > 1:
        raise RuntimeError("Multiple migration heads detected in repository; resolve before applying migrations.")


def do_run_migrations(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online():
    # Use DATABASE_URL from settings (should be async URL)
    database_url = settings.DATABASE_URL
    connectable = create_async_engine(database_url, poolclass=pool.NullPool)

    # basic check for multiple heads in the repo
    script = context.script
    _validate_heads(script)

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)


if __name__ == "__main__":
    asyncio.run(run_migrations_online())
