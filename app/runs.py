"""A Run's background work: the swap point, the placeholder behind it, and
the start-up sweep."""

import asyncio
import uuid
from collections.abc import Awaitable, Callable

import logfire
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.tables import Run, RunStatus

Sessions = async_sessionmaker[AsyncSession]
# The work calls this to say how far the Run has got.
Report = Callable[[RunStatus], Awaitable[None]]


async def placeholder(report: Report, step_seconds: float) -> None:
    """Stands in for a real Architecture until PR 2: it only pretends to work."""
    await asyncio.sleep(step_seconds)
    await report(RunStatus.planning)
    await asyncio.sleep(step_seconds)
    await report(RunStatus.running)
    await asyncio.sleep(step_seconds)


# The work behind start_run. PR 2 replaces the placeholder with a real Architecture.
research = placeholder


async def start_run(run_id: uuid.UUID, sessions: Sessions, step_seconds: float) -> None:
    """The single swap point: runs one Run's work in the background, to the end."""

    async def report(status: RunStatus) -> None:
        await set_status(sessions, run_id, status)

    # The one manual span: every status update below appears inside it.
    with logfire.span("research run", run_id=str(run_id)):
        try:
            await research(report, step_seconds)
        except Exception as error:  # noqa: BLE001 (on purpose: any error fails the Run)
            # Any error ends the Run, with the error recorded on it.
            message = f"{type(error).__name__}: {error}"
            await set_status(sessions, run_id, RunStatus.failed, error=message)
            return
        await set_status(sessions, run_id, RunStatus.done)


async def fail_interrupted_runs(sessions: Sessions) -> None:
    """At start-up, fail every Run that a restart cut off, so none stays stuck.

    Background work lives inside the server process, so a restart stops it.
    """
    unfinished = [RunStatus.queued, RunStatus.planning, RunStatus.running]
    async with sessions() as session:
        await session.execute(
            update(Run)
            .where(Run.status.in_(unfinished))
            .values(status=RunStatus.failed, error="interrupted by restart")
        )
        await session.commit()


async def set_status(
    sessions: Sessions,
    run_id: uuid.UUID,
    status: RunStatus,
    error: str | None = None,
) -> None:
    async with sessions() as session:
        await session.execute(
            update(Run).where(Run.id == run_id).values(status=status, error=error)
        )
        await session.commit()
