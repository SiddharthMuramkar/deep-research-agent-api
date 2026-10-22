"""The FastAPI app: its start-up, and the research endpoints."""

import uuid
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Annotated

import logfire
from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import engine, new_session
from app.runs import fail_interrupted_runs, start_run
from app.schemas import QueryAccepted, QueryRequest, RunStatusResponse
from app.tables import Run, RunStatus

# Send traces to Logfire only when a token is configured, so tests send nothing.
logfire.configure(
    service_name="deep-research-agent-api",
    token=settings.logfire_token,
    send_to_logfire=bool(settings.logfire_token),
    console=False,
)
# Every database query becomes a span, automatically. This hooks asyncpg, the
# driver under SQLAlchemy, because the SQLAlchemy hook doesn't support 2.1 yet.
logfire.instrument_asyncpg()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Runs once at start-up (before `yield`) and once at shut-down (after)."""
    await fail_interrupted_runs()
    yield
    await engine.dispose()


app = FastAPI(title="Deep Research Agent API", lifespan=lifespan)
# Every request becomes a span (the start of a trace), automatically.
logfire.instrument_fastapi(app)


async def get_session() -> AsyncIterator[AsyncSession]:
    """Gives each request its own database session, closed when it's done."""
    async with new_session() as session:
        yield session


DbSession = Annotated[AsyncSession, Depends(get_session)]


@app.post("/research/query", status_code=202)
async def submit_query(
    body: QueryRequest, session: DbSession, background_tasks: BackgroundTasks
) -> QueryAccepted:
    """Start a Run. Answers at once; the research happens later."""
    run = Run(id=uuid.uuid4(), query=body.query, status=RunStatus.queued)
    session.add(run)
    await session.commit()
    # Runs after the response has been sent, in this same server process.
    background_tasks.add_task(start_run, run.id, run.query)
    return QueryAccepted(run_id=run.id, status=run.status)


@app.get("/research/{run_id}/status")
async def get_run_status(run_id: uuid.UUID, session: DbSession) -> RunStatusResponse:
    run = await session.get(Run, run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Run not found")
    return RunStatusResponse(
        run_id=run.id,
        status=run.status,
        error=run.error,
        created_at=run.created_at,
        updated_at=run.updated_at,
    )
