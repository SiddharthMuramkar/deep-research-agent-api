"""A Run's background work: the swap point, the placeholder behind it, and
the start-up sweep."""

import asyncio
import uuid
from collections.abc import Awaitable, Callable

import logfire
from sqlalchemy import update

from app.config import settings
from app.database import new_session
from app.tables import Run, RunStatus

# The work calls this to say how far the Run has got.
UpdateStatus = Callable[[RunStatus], Awaitable[None]]


async def placeholder(query: str, update_status: UpdateStatus) -> None:
    """Stands in for a real Architecture until PR 2: it only pretends to work."""
    wait = settings.placeholder_step_seconds
    await asyncio.sleep(wait)
    await update_status(RunStatus.planning)
    await asyncio.sleep(wait)
    await update_status(RunStatus.running)
    await asyncio.sleep(wait)


# The Architecture that start_run runs. PR 2 points this at a real one.
research = placeholder


async def start_run(run_id: uuid.UUID, query: str) -> None:
    """The single swap point: the endpoint hands each new Run to this function,
    which runs it in the background, to the end."""

    async def update_status(status: RunStatus) -> None:
        await set_status(run_id, status)

    try:
        # The one manual span. An error that escapes it marks it failed in Logfire.
        with logfire.span("research run", run_id=str(run_id)):
            await research(query, update_status)
            await set_status(run_id, RunStatus.done)
    except Exception as error:  # noqa: BLE001 (on purpose: any error fails the Run)
        # Any error ends the Run, with the error recorded on it.
        message = f"{type(error).__name__}: {error}"
        await set_status(run_id, RunStatus.failed, error=message)


async def fail_interrupted_runs() -> None:
    """At start-up, fail every Run that a restart cut off, so none stays stuck.

    Background work lives inside the server process, so a restart stops it.
    """
    unfinished = [RunStatus.queued, RunStatus.planning, RunStatus.running]
    async with new_session() as session:
        await session.execute(
            update(Run)
            .where(Run.status.in_(unfinished))
            .values(status=RunStatus.failed, error="interrupted by restart")
        )
        await session.commit()


async def set_status(
    run_id: uuid.UUID, status: RunStatus, error: str | None = None
) -> None:
    async with new_session() as session:
        await session.execute(
            update(Run).where(Run.id == run_id).values(status=status, error=error)
        )
        await session.commit()
