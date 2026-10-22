"""The FastAPI app: its start-up, and the research endpoints."""

import uuid
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import Settings
from app.runs import fail_interrupted_runs, start_run
from app.schemas import QueryAccepted, QueryRequest, RunStatusResponse
from app.tables import Run, RunStatus


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Runs once at start-up (before `yield`) and once at shut-down (after)."""
    # Raises, so the service refuses to start, if DATABASE_URL is missing.
    settings = Settings()
    engine = create_async_engine(settings.database_url)
    app.state.settings = settings
    app.state.sessions = async_sessionmaker(engine, expire_on_commit=False)
    await fail_interrupted_runs(app.state.sessions)
    yield
    await engine.dispose()


app = FastAPI(title="Deep Research Agent API", lifespan=lifespan)


async def get_session(request: Request) -> AsyncIterator[AsyncSession]:
    """Gives each request its own database session, closed when it's done."""
    async with request.app.state.sessions() as session:
        yield session


Session = Annotated[AsyncSession, Depends(get_session)]


@app.post("/research/query", status_code=202)
async def submit_query(
    body: QueryRequest,
    session: Session,
    background_tasks: BackgroundTasks,
    request: Request,
) -> QueryAccepted:
    """Start a Run. Answers at once; the research happens later."""
    run = Run(id=uuid.uuid4(), query=body.query, status=RunStatus.queued)
    session.add(run)
    await session.commit()
    # Runs after the response has been sent, in this same server process.
    background_tasks.add_task(
        start_run,
        run.id,
        request.app.state.sessions,
        request.app.state.settings.placeholder_step_seconds,
    )
    return QueryAccepted(run_id=run.id, status=run.status)


@app.get("/research/{run_id}/status")
async def get_run_status(run_id: uuid.UUID, session: Session) -> RunStatusResponse:
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
