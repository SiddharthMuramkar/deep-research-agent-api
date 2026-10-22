# Research: the PR 1 service skeleton (FastAPI, SQLAlchemy, Alembic, PostgreSQL)

These facts were checked on 2026-10-22 against Context7 and the installed versions. Re-check them with Context7 before relying on them in a later PR.

## Versions in `uv.lock`

FastAPI 0.159, Starlette 1.9, Pydantic 2.14, pydantic-settings 2.16, SQLAlchemy **2.1**, Alembic 1.20, asyncpg 0.32, uvicorn 0.54, Python 3.14. The database is PostgreSQL 18.6, from the `postgres:18` Docker image.

## PostgreSQL 18 Docker image

From version 18, the image keeps its data under **`/var/lib/postgresql`**, with `PGDATA` set to `/var/lib/postgresql/18/docker`. Before 18 it was `/var/lib/postgresql/data`, which many guides still show. Mount the volume at `/var/lib/postgresql`. *(docker-library/postgres, Dockerfile template)*

Scripts in `/docker-entrypoint-initdb.d/` run only when the data volume is first created. This is how `research_test` gets created.

## SQLAlchemy 2.1

- `greenlet`, which async SQLAlchemy needs, is **no longer installed by default**. Install `sqlalchemy[asyncio]`. *(migration_21.rst)*
- PostgreSQL named types, such as `ENUM`, are no longer dropped by `Table.drop()`. This is why `runs.status` is text with a CHECK constraint (`Enum(..., native_enum=False, create_constraint=True)`). *(postgresql/named_types.py)*
- Use `async_sessionmaker(engine, expire_on_commit=False)`. Then a row's values can still be read after `commit()` without another database trip. *(orm/extensions/asyncio)*

## Alembic

- `alembic init -t async migrations` creates an `env.py` that runs migrations through an async engine with `asyncio.run(...)`.
- Our `env.py` reads the URL from `app.config.Settings` instead of from `alembic.ini`. The app, the CLI and the tests then share one source of truth.
- Called from code, `command.upgrade(Config("alembic.ini"), "head")` works from a normal, synchronous pytest fixture, because no event loop is running there yet.

## FastAPI and Starlette testing

- `with TestClient(app) as client:` runs the app's `lifespan` start-up on entry and its shut-down on exit. *(fastapi testing-events)*
- If start-up raises an exception, for example a `ValidationError` from missing settings, the `with` block raises it too.
- Starlette 1.x's `TestClient` is built on **`httpx2`**. Plain `httpx` still works, but it is deprecated and prints a warning, so the dev dependency is `httpx2`. *(starlette docs/testclient.md)*

## pydantic-settings

- A required field that no source provides raises `ValidationError` ("Field required").
- Environment variables win over `.env`.
- By default `extra='forbid'` rejects unknown keys in `.env`. We use `extra='ignore'`, because `.env` holds keys for later PRs.
- `StringConstraints(strip_whitespace=True, min_length=1, max_length=2000)` trims the string first, then checks its length.
