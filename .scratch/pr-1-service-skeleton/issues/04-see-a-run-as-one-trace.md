# 04: See a Run as one trace in Logfire

**What to build:** Each Run's work shows up in Logfire as one trace under its submit request.
- A named `research run` span contains each status change.
- Every status poll is its own small trace.
- Nothing is sent when no token is configured, so the tests send nothing.

**Blocked by:** 01, 03

**Status:** done

- [ ] *(deferred to the last PR)* With `LOGFIRE_TOKEN` set, a submitted Run appears as one trace. The trace holds the submit request, the insert, and a `research run` span that carries the run ID and contains each status update.
- [x] Each status poll appears as a separate trace.
- [x] Without a token, nothing is sent and the tests still pass.
- [ ] *(deferred to the last PR)* Someone checked by eye whether the submit request's span lasts as long as the Run, and the README records the answer. The spec asked for this check.
- [x] The README explains how to view the traces in Logfire.
- [ ] *(deferred to the last PR)* The developer was taught the Run trace shape in front of the real trace, then quizzed, and explained it back. It is ticked in the spec.

## Comments

- 2026-10-22: Built. Spans were captured locally with an in-memory exporter, and they show the agreed shape: `POST` → `INSERT`, plus `BackgroundTask start_run` → `research run` → one `UPDATE` per status. Each poll is its own trace.
- Two findings. First, OpenTelemetry's SQLAlchemy hook doesn't support SQLAlchemy 2.1, so queries are recorded at the asyncpg level instead. Second, the `POST` span ends at about 5 ms, and the background work's span outlasts it. Both are in the README decision log, and the spec's must-explain item was corrected to match.
- Still open: the first criterion and the by-eye check need the developer's Logfire token (ticket 01). After that comes the teach-and-quiz in front of the real trace.
- 2026-10-22: With the developer's token set, the first Run's trace arrived in Logfire, and the developer saw a span of 821 µs. The full by-eye check of the tree and of the two spans' durations moved to the last PR, together with the teach-and-quiz.
- 2026-10-22: Closed, following the new flow (step 5 in "The flow for every PR" in `CLAUDE.md`). The criteria marked *(deferred to the last PR)* stay open until PR 4.
